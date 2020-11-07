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

import stratuxcot


__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


class StratuxWorker:

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(stratuxcot.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(stratuxcot.LOG_LEVEL)
        _console_handler.setFormatter(stratuxcot.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False
    logging.getLogger('asyncio').setLevel(stratuxcot.LOG_LEVEL)

    def __init__(self, event_queue, url, cot_stale) -> None:
        self.event_queue = event_queue
        self.url = url
        self.cot_stale = cot_stale

    async def _put_event_queue(self, event: pycot.Event) -> None:
        """Puts Event onto the CoT Transmit Queue."""
        try:
            await self.event_queue.put(event)
        except queue.Full as exc:
            self._logger.warning(
                'Lost CoT Event (queue full): "%s"', _event)

    async def handle_message(self, msg: dict) -> None:
        """Processes Stratux Message"""
        event: pycot.Event = stratuxcot.stratux_to_cot(
            msg, stale=self.cot_stale)

        if not event:
            self._logger.debug('Empty CoT Event')
            return

        icao = stratuxcot.icao_hex(msg.get('Icao_addr'))
        self._logger.debug(
            'Handling ICAO24: %s Flight: %s ', icao, msg.get('Tail'))

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
