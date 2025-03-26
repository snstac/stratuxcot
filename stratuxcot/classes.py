#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""StratuxCOT Class Definitions."""

import asyncio
import json

from configparser import SectionProxy
from typing import Union

import websockets

import aircot
import pytak
import stratuxcot


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class StratuxWorker(pytak.QueueWorker):
    """Connects to Stratux ADS-B WebSocket."""

    def __init__(self, queue: asyncio.Queue, config: SectionProxy) -> None:
        super().__init__(queue, config)
        self.known_craft_db: Union[dict, None] = None

    async def handle_data(  # pylint: disable=too-many-return-statements
        self, data: dict
    ) -> None:
        """Processes Stratux Message"""
        if not isinstance(data, dict):
            self._logger.warning("Invalid aircraft data, should be a Python `dict`.")
            return

        if not data:
            self._logger.warning("Empty aircraft `dict`")
            return

        if not data.get("Position_valid", True):
            return

        icao: Union[str, None] = None
        icao_int: str = data.get("Icao_addr", "")
        if icao_int:
            icao = aircot.icao_int_to_hex(icao_int)
        else:
            return

        if icao:
            icao = icao.strip().upper()
        else:
            return

        if "~" in icao and not self.config.getboolean("INCLUDE_TISB"):
            return

        known_craft: Union[dict, None] = None

        if self.known_craft_db:
            known_craft = (
                list(
                    filter(
                        lambda x: x["HEX"].strip().upper() == icao,
                        self.known_craft_db,
                    )
                )
                or [{}]
            )[0]
            # self._logger.debug("known_craft='%s'", known_craft)

        # Skip if we're using known_craft CSV and this Craft isn't found:
        if (
            self.known_craft_db
            and not known_craft
            and not self.config.getboolean("INCLUDE_ALL_CRAFT")
        ):
            return

        event: Union[str, None] = stratuxcot.stratux_to_cot(
            data, config=self.config, known_craft=known_craft
        )

        if not event:
            self._logger.debug("Empty COT Event")
            return

        self._logger.debug("Handling ICAO: %s", icao)
        await self.put_queue(event)

    async def run(self, number_of_iterations=-1) -> None:
        url: str = self.config.get("STRATUX_WS", stratuxcot.DEFAULT_STRATUX_WS)

        if not url or url == "":
            raise Exception("No STRATUX_WS specified.")

        self._logger.info("Running %s for: %s", self.__class__, url)

        known_craft: Union[str, None] = self.config.get("KNOWN_CRAFT")
        if known_craft:
            self._logger.info("Using KNOWN_CRAFT: %s", known_craft)
            self.known_craft_db = aircot.read_known_craft(known_craft)

        while 1:
            try:
                async with websockets.connect(url) as websocket:
                    self._logger.info("Connected to: %s", url)
                    async for message in websocket:
                        self._logger.debug("message=%s", message)
                        if message:
                            j_event = json.loads(message)
                            await self.handle_data(j_event)
            except websockets.exceptions.ConnectionClosedError:
                self._logger.warning("Websocket closed, reconnecting...")
                await asyncio.sleep(2)
