#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Gateway Functions."""

import datetime
import os
import platform

import xml.etree.ElementTree

import aircot
import pytak

import stratuxcot.constants

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"


def stratux_to_cot_raw(craft: dict, stale: int = None, known_craft: dict = {}) -> str:  # NOQA pylint: disable=too-many-locals
    """
    Transforms Stratux Websocket Messages to a Cursor-on-Target PLI Events.
    """
    time = datetime.datetime.now(datetime.timezone.utc)
    cot_stale = stale or stratuxcot.DEFAULT_COT_STALE

    icao_hex = aircot.icao_int_to_hex(craft.get("Icao_addr"))
    flight = craft.get("Tail", "").strip().upper()
    craft_type: str = craft.get("t", "").strip().upper()
    reg: str = craft.get("Reg", "").strip().upper()

    name, callsign = aircot.set_name_callsign(icao_hex, reg, craft_type, flight, known_craft)
    category = aircot.set_category(craft.get("Emitter_category"), known_craft)
    cot_type = aircot.set_cot_type(icao_hex, category, flight, known_craft)
    print(locals())

    point = xml.etree.ElementTree.Element("point")
    point.set("lat", str(craft.get("Lat")))
    point.set("lon", str(craft.get("Lng")))

    if craft.get("OnGround"):
        point.set("ce", str(51.56 + int(craft.get("NACp"))))
        point.set("le", str(12.5 + int(craft.get("NACp"))))
        point.set("hae", "9999999.0")
    else:
        point.set("ce", str(56.57 + int(craft.get("NACp"))))
        point.set("le", str(12.5 + int(craft.get("NACp"))))
        point.set("hae", aircot.functions.get_hae(craft.get("Alt")))

    uid = xml.etree.ElementTree.Element("UID")
    uid.set("Droid", name)

    contact = xml.etree.ElementTree.Element("contact")
    contact.set("callsign", str(callsign))

    track = xml.etree.ElementTree.Element("track")
    track.set("course", str(craft.get("Track", "9999999.0")))
    track.set("speed", aircot.functions.get_speed(craft.get("Speed")))

    detail = xml.etree.ElementTree.Element("detail")
    detail.set("uid", name)
    detail.append(uid)
    detail.append(contact)
    detail.append(track)

    remarks = xml.etree.ElementTree.Element("remarks")

    _remarks = (
        f"{callsign} ICAO: {icao_hex} REG: {reg} Flight: {flight} Type: {craft_type} Squawk: {craft.get('Squawk')} "
        f"Category: {craft.get('Emitter_category')} (via stratuxcot@{platform.node()})")

    detail.set("remarks", _remarks)
    remarks.text = _remarks
    detail.append(remarks)

    root = xml.etree.ElementTree.Element("event")
    root.set("version", "2.0")
    root.set("type", cot_type)
    root.set("uid", f"ICAO-{icao_hex}")
    root.set("how", "m-g")
    root.set("time", time.strftime(pytak.ISO_8601_UTC))
    root.set("start", time.strftime(pytak.ISO_8601_UTC))
    root.set("stale", (time + datetime.timedelta(seconds=int(cot_stale))).strftime(pytak.ISO_8601_UTC))
    root.append(point)
    root.append(detail)

    return root


def stratux_to_cot(craft: dict, stale: int = None, known_craft: dict = {}) -> str:
    if craft.get("Lat") is None or craft.get("Lng") is None:
        return None
    return xml.etree.ElementTree.tostring(stratux_to_cot_raw(craft, stale, known_craft))

