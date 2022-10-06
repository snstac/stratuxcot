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

"""StratuxCOT Gateway Functions."""


import xml.etree.ElementTree as ET

from configparser import ConfigParser
from typing import Union, Set
from urllib.parse import ParseResult, urlparse

import aircot
import pytak
import stratuxcot

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def create_tasks(
    config: ConfigParser, clitool: pytak.CLITool
) -> Set[pytak.Worker, ]:
    """
    Creates specific coroutine task set for this application.

    Parameters
    ----------
    config : `ConfigParser`
        Configuration options & values.
    clitool : `pytak.CLITool`
        A PyTAK Worker class instance.

    Returns
    -------
    `set`
        Set of PyTAK Worker classes for this application.
    """
    stratux_ws: ParseResult = urlparse(config.get("STRATUX_WS"))

    message_worker = stratuxcot.StratuxWorker(clitool.tx_queue, config)
    message_worker.url = stratux_ws

    return set([message_worker])


def stratux_to_cot_xml(  # NOQA pylint: disable=too-many-locals,too-many-branches,too-many-statements
    craft: dict, config: Union[dict, None] = None, known_craft: Union[dict, None] = None
) -> Union[ET.Element, None]:
    """
    Transforms Stratux Websocket Messages to a Cursor-on-Target PLI Events.
    """
    lat = craft.get("Lat")
    lon = craft.get("Lng")
    if lat is None or lon is None:
        return None

    remarks_fields = []
    known_craft: dict = known_craft or {}
    config: dict = config or {}
    category = None
    tisb: bool = False

    uid_key = config.get("UID_KEY", "ICAO")
    cot_stale = int(config.get("COT_STALE", pytak.DEFAULT_COT_STALE))
    cot_host_id = config.get("COT_HOST_ID", pytak.DEFAULT_HOST_ID)

    aircotx = ET.Element("_aircot_")
    aircotx.set("cot_host_id", cot_host_id)

    icao_hex = aircot.icao_int_to_hex(craft.get("Icao_addr"))
    flight: str = craft.get("Tail", "")
    reg: str = craft.get("Reg", "")
    cat: str = str(craft.get("Emitter_category", ""))
    squawk: str = str(craft.get("Squawk", ""))
    target_type: int = craft.get("TargetType")

    if flight:
        flight = flight.strip().upper()
        remarks_fields.append(flight)
        aircotx.set("flight", flight)

    if reg:
        reg = reg.strip().upper()
        remarks_fields.append(reg)
        aircotx.set("reg", reg)

    if squawk:
        squawk = squawk.strip().upper()
        remarks_fields.append(f"Squawk: {squawk}")
        aircotx.set("squawk", squawk)

    if icao_hex:
        icao_hex = icao_hex.strip().upper()
        remarks_fields.append(icao_hex)
        aircotx.set("icao", icao_hex)

    if cat:
        cat = cat.strip().upper()
        category = aircot.set_category(cat, known_craft)
        remarks_fields.append(f"Cat.: {category}")
        aircotx.set("cat", category)

    if target_type:
        aircotx.set("target_type", str(target_type))
        target_type_name: Union[str, None] = None
        if target_type == 0:
            target_type_name = "Mode S"
        elif target_type == 1:
            target_type_name = "ADS-B"
        elif target_type == 2:
            target_type_name = "ADS-R"
        elif target_type == 3:
            target_type_name = "TIS-B S"
            tisb = True
        elif target_type == 4:
            target_type_name = "TIS-B"
            tisb = True
        if target_type_name:
            remarks_fields.append(f"ADS-B Type: {target_type_name}")
            aircotx.set("target_type_name", target_type_name)

    if "REG" in uid_key and reg:
        cot_uid = f"REG-{reg}"
    elif "ICAO" in uid_key and icao_hex:
        cot_uid = f"ICAO-{icao_hex}"
    if "FLIGHT" in uid_key and flight:
        cot_uid = f"FLIGHT-{flight}"
    elif icao_hex:
        cot_uid = f"ICAO-{icao_hex}"
    elif flight:
        cot_uid = f"FLIGHT-{flight}"
    else:
        return None

    if flight:
        callsign = flight
    elif reg:
        callsign = reg
    else:
        callsign = icao_hex

    _, callsign = aircot.set_name_callsign(icao_hex, reg, None, flight, known_craft)

    if tisb:
        cot_type = "a-u-A"
    else:
        cot_type = aircot.set_cot_type(icao_hex, category, flight, known_craft)

    point = ET.Element("point")
    point.set("lat", str(lat))
    point.set("lon", str(lon))

    if craft.get("OnGround"):
        point.set("ce", str(51.56 + int(craft.get("NACp"))))
        point.set("le", str(12.5 + int(craft.get("NACp"))))
        point.set("hae", "9999999.0")
    else:
        point.set("ce", str(56.57 + int(craft.get("NACp"))))
        point.set("le", str(12.5 + int(craft.get("NACp"))))
        point.set("hae", aircot.functions.get_hae(craft.get("Alt")))

    uid = ET.Element("UID")
    uid.set("Droid", str(callsign))

    contact = ET.Element("contact")
    contact.set("callsign", str(callsign))

    track = ET.Element("track")
    track.set("course", str(craft.get("Track", "9999999.0")))
    track.set("speed", aircot.functions.get_speed(craft.get("Speed")))

    detail = ET.Element("detail")
    detail.set("uid", cot_uid)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    icon = known_craft.get("ICON")
    if icon:
        usericon = ET.Element("usericon")
        usericon.set("iconsetpath", icon)
        detail.append(usericon)

    remarks = ET.Element("remarks")
    remarks_fields.append(f"{cot_host_id}")
    _remarks = " ".join(list(filter(None, remarks_fields)))
    remarks.text = _remarks
    detail.append(remarks)

    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type)
    root.set("uid", cot_uid)
    root.set("how", "m-g")
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(cot_stale))

    root.append(point)
    root.append(detail)
    root.append(aircotx)

    return root


def stratux_to_cot(
    craft: dict, config: Union[dict, None] = None, known_craft: Union[dict, None] = None
) -> Union[bytes, None]:
    """Wrapper that returns COT as an XML string."""
    cot: Union[ET.Element, None] = stratux_to_cot_xml(craft, config, known_craft)
    return (
        b"\n".join([pytak.DEFAULT_XML_DECLARATION, ET.tostring(cot)]) if cot else None
    )