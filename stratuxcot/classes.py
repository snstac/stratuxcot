#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Class Definitions."""

import asyncio
import json
import logging
import os
import random
import time
import urllib
import websockets

import pycot
import pytak

import stratuxcot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2020 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"


class StratuxWorker(pytak.MessageWorker):

    def __init__(self, event_queue, cot_stale):
        super().__init__(event_queue)
        self.cot_stale = cot_stale
        self.cot_renderer = stratuxcot.stratux_to_cot
        self.cot_classifier = pytak.faa_to_cot_type

    async def handle_message(self, msg: dict) -> None:
        """Processes Stratux Message"""

        event: pycot.Event = self.cot_renderer(
            msg,
            stale=self.cot_stale,
            classifier=self.cot_classifier
        )

        if not event:
            self._logger.debug("Empty CoT Event")
            return

        icao = stratuxcot.icao_int_to_hex(msg.get("Icao_addr"))
        self._logger.debug(
            "Handling ICAO: %s Flight: %s ", icao, msg.get("Tail"))

        await self._put_event_queue(event)

    async def run(self) -> None:
        self._logger.info("Running StratuxWorker")

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
