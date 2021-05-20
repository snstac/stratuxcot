#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Class Definitions."""

import asyncio
import configparser
import json
import logging
import os
import random
import time
import urllib
import websockets

import aircot
import pytak

import stratuxcot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"


class StratuxWorker(pytak.MessageWorker):

    def __init__(self, event_queue: asyncio.Queue, opts):
        super().__init__(event_queue)
        self.url: urllib.parse.ParseResult = urllib.parse.urlparse(opts.get("ADSBX_URL"))
        self.cot_stale = opts.get("COT_STALE")

        self.include_tisb = bool(opts.get("INCLUDE_TISB")) or False
        self.include_all_craft = bool(opts.get("INCLUDE_ALL_CRAFT")) or False

        self.filters = opts.get("FILTERS")
        self.known_craft = opts.get("KNOWN_CRAFT")
        self.known_craft_key = opts.get("KNOWN_CRAFT_KEY") or "HEX"

        self.filter_type = ""
        self.known_craft_db = None

    async def handle_message(self, msg: dict) -> None:
        """Processes Stratux Message"""
        craft = msg

        icao = aircot.icao_int_to_hex(craft.get("Icao_addr"))
        flight = craft.get("Tail", "").strip().upper()
        reg: str = craft.get("Reg", "").strip().upper()

        if "~" in icao and not self.include_tisb:
            return

        known_craft = {}

        if self.filter_type:
            if self.filter_type == "HEX":
                filter_key: str = icao
            elif self.filter_type == "FLIGHT":
                filter_key: str = flight
            elif self.filter_type == "REG":
                filter_key: str = reg
            else:
                filter_key: str = ""

            # self._logger.debug("filter_key=%s", filter_key)

            if self.known_craft_db and filter_key:
                known_craft = (list(filter(
                    lambda x: x[self.known_craft_key].strip().upper() == filter_key, self.known_craft_db)) or
                               [{}])[0]
                # self._logger.debug("known_craft='%s'", known_craft)
            elif filter_key:
                if "include" in self.filters[self.filter_type] and filter_key not in self.filters.get(filter_type,
                                                                                                 "include"):
                    return
                if "exclude" in self.filters[self.filter_type] and filter_key in self.filters.get(filter_type,
                                                                                             "exclude"):
                    return

        # If we're using a known_craft csv and this craft wasn't found, skip:
        if self.known_craft_db and not known_craft and not self.include_all_craft:
            return

        event: str = stratuxcot.stratux_to_cot(craft, stale=self.cot_stale, known_craft=known_craft)

        if not event:
            self._logger.debug("Empty CoT Event")
            return

        icao = aircot.icao_int_to_hex(msg.get("Icao_addr"))
        self._logger.debug(
            "Handling ICAO: %s Flight: %s ", icao, msg.get("Tail"))

        await self._put_event_queue(event)

    async def run(self) -> None:
        self._logger.info("Running StratuxWorker")

        if self.known_craft is not None:
            self._logger.info("Using KNOWN_CRAFT File: '%s'", self.known_craft)
            self.known_craft_db = aircot.read_known_craft(self.known_craft)
            self.filters = configparser.ConfigParser()
            self.filters.add_section(self.known_craft_key)
            self.filters[self.known_craft_key]["include"] = \
                str([x[self.known_craft_key].strip().upper() for x in self.known_craft_db])

        if self.filters or self.known_craft_db:
            filter_src = self.filters or self.known_craft_key
            self._logger.debug("filter_src=%s", filter_src)
            if filter_src:
                if "HEX" in filter_src:
                    self.filter_type = "HEX"
                elif "FLIGHT" in filter_src:
                    self.filter_type = "FLIGHT"
                elif "REG" in filter_src:
                    self.filter_type = "REG"
                self._logger.debug("filter_type=%s", self.filter_type)

        while 1:
            try:
                async with websockets.connect(self.url.geturl()) as websocket:
                    self._logger.info("Connected to '%s'", self.url.geturl())
                    async for message in websocket:
                        self._logger.debug("message=%s", message)
                        if message:
                            j_event = json.loads(message)
                            await self.handle_message(j_event)
            except websockets.exceptions.ConnectionClosedError:
                self._logger.warning("Websocket closed, reconnecting...")
                await asyncio.sleep(2)
