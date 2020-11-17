#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Gateway Functions."""

import datetime
import os

import pycot

import stratuxcot.constants

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2020 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"


#
#
# {
#  'Icao_addr': 11160165,
#  'Reg': 'N762QS',
#  'Tail': 'N762QS',
#  'Squawk': 0,
#  'Lat': 37.89692,
#  'Lng': -122.74547,
#  'Addr_type': 0,
#  'Age': 28.29,
#  'AgeLastAlt': 1.33,
#  'Alt': 21850,
#  'AltIsGNSS': False,
#  'Bearing': 0,
#  'BearingDist_valid': False,
#  'Distance': 0,
#  'Emitter_category': 0,
#  'ExtrapolatedPosition': False,
#  'GnssDiffFromBaroAlt': -275,
#  'LastSent': '0001-01-01T00:39:16.44Z',
#  'Last_GnssDiff': '0001-01-01T00:39:53.84Z',
#  'Last_GnssDiffAlt': 21775,
#  'Last_alt': '0001-01-01T00:39:54.77Z',
#  'Last_seen': '0001-01-01T00:39:54.77Z',
#  'Last_source': 1,
#  'Last_speed': '0001-01-01T00:39:53.84Z',
#  'NACp': 10,
#  'NIC': 8,
#  'OnGround': False,
#  'Position_valid': True,
#  'PriorityStatus': 0,
#  'SignalLevel': -28.21023052706831,
#  'Speed': 340,
#  'Speed_valid': True,
#  'TargetType': 1,
#  'Timestamp': '2020-11-06T19:58:06.234Z',
#  'Track': 249,
#  'Vvel': 3392
#  }
#

#
# "Last_seen":"0001-01-01T00:43:19.61Z"  (ws://192.168.10.1/traffic)   0001-01-01 is day zero,
# +
# "GPSTime":"2020-05-12T08:27:10Z" (http://192.168.10.1/getSituation)
# -
# ("Uptime":2610230,ms)"UptimeClock":"0001-01-01T00:43:30.23Z" (http://192.168.10.1/getStatus)
# = Timestamp of traffic "event"
#

#
# This is an illuminated/commented version of the traffic output from StratuX:
# type TrafficInfo struct {
# Icao_addr          uint32   // decimal version of (ICAO HEX or ICAO OCTAL)
# Reg                string   // Registration. Calculated from Icao_addr for civil aircraft of US registry.
# Tail               string   // Callsign. Transmitted by aircraft. 8 Characters max including spaces
# Emitter_category   uint8    // Formatted using GDL90 standard 3.5.1.10 Table 11, e.g. in a Mode ES report, A7 becomes 0x07, B0 becomes 0x08, etc.
# OnGround           bool     // Air-ground status. On-ground is "true".
# Addr_type          uint8    // UAT address qualifier. Used by GDL90 format, so translations for ES TIS-B/ADS-R are needed. 3.5.1.2 Target Identity
# (GDL90 ICD)
# TargetType         uint8    // types decribed in const above https://github.com/cyoung/stratux/blob/master/main/traffic.go#L66
# SignalLevel        float64  // Signal level, dB RSSI.
# Squawk             int      // Squawk code
# Position_valid     bool     // false = MODE-S message without location data
# Lat                float32  // decimal degrees, north positive
# Lng                float32  // decimal degrees, east positive
# Alt                int32    // Pressure altitude, feet
# GnssDiffFromBaroAlt int32    // GNSS altitude above WGS84 datum. Reported in TC 20-22 messages (negative = below BaroAlt, smaller magnitude)
# AltIsGNSS          bool     // Pressure alt = 0; GNSS alt = 1
# NIC                int      // Navigation Integrity Category.
# NACp               int      // Navigation Accuracy Category for Position.
# Track              uint16   // degrees true
# Speed              uint16   // knots
# Speed_valid        bool     // set when speed report received.
# Vvel               int16    // feet per minute
# Timestamp          time.Time // timestamp of traffic message, UTC
# PriorityStatus     uint8    // Emergency or priority code as defined in GDL90 spec, DO-260B (Type 28 msg) and DO-282B
# // Parameters starting at 'Age' are calculated from last message receipt on each call of sendTrafficUpdates().
# // Mode S transmits position and track in separate messages, and altitude can also be
# // received from interrogations.
# Age                 float64  // Age of last valid position fix, seconds ago.
# AgeLastAlt          float64  // Age of last altitude message, seconds ago.
# Last_seen           time.Time // Time of last position update (stratuxClock). Used for timing out expired data.
# Last_alt            time.Time // Time of last altitude update (stratuxClock).
# Last_GnssDiff       time.Time // Time of last GnssDiffFromBaroAlt update (stratuxClock).
# Last_GnssDiffAlt    int32    // Altitude at last GnssDiffFromBaroAlt update.
# Last_speed          time.Time // Time of last velocity and track update (stratuxClock).
# Last_source         uint8    // Last frequency on which this target was received.
# ExtrapolatedPosition bool     //TODO: True if Stratux is "coasting" the target from last known position.
# BearingDist_valid   bool     // set when bearing and distance information is valid
# Bearing             float64  // Bearing in degrees true to traffic from ownship, if it can be calculated. Units: degrees.
# Distance            float64  // Distance to traffic from ownship, if it can be calculated. Units: meters.
# //FIXME: Rename variables for consistency, especially "Last_".
#

def icao_int_to_hex(addr) -> str:
    return str(hex(addr)).lstrip('0x').upper()


def stratux_to_cot(msg: dict, stale: int = None, # NOQA pylint: disable=too-many-locals
                   classifier: any = None) -> pycot.Event:
    """
    Transforms Stratux Websocket Messages to a Cursor-on-Target PLI Events.
    """
    time = datetime.datetime.now(datetime.timezone.utc)
    stale = stale or stratuxcot.DEFAULT_EVENT_STALE

    lat = msg.get("Lat")
    lon = msg.get("Lng")
    if lat is None or lon is None:
        return None

    icao_hex = icao_int_to_hex(msg.get('Icao_addr'))
    name = f"ICAO-{icao_hex}"

    flight = msg.get('Tail', '').strip()
    if flight:
        callsign = flight
    else:
        callsign = icao_hex

    # Figure out appropriate CoT Type:
    emitter_category = msg.get("Emitter_category")
    cot_type = classifier(icao_hex, emitter_category, flight)

    point = pycot.Point()
    point.lat = lat
    point.lon = lon

    if msg.get("OnGround"):
        point.hae = "9999999.0"
        point.ce = 51.56 + int(msg.get("NACp"))
        point.le = 12.5 + int(msg.get("NACp"))
    else:
        point.ce = 56.57 + int(msg.get("NACp"))
        point.le = 12.5 + int(msg.get("NACp"))
        alt = int(msg.get("Alt", 0))
        if alt:
            point.hae = alt * 0.3048
        else:
            point.hae = "9999999.0"

    uid = pycot.UID()
    uid.Droid = name

    contact = pycot.Contact()
    contact.callsign = callsign
    # Not supported by FTS 1.1?
    # if flight:
    #    contact.hostname = f'https://flightaware.com/live/flight/{flight}'

    track = pycot.Track()
    track.course = msg.get('Track', '9999999.0')

    # gs: ground speed in knots
    gs = int(msg.get('Speed', 0))
    if gs:
        track.speed = gs * 0.514444
    else:
        track.speed = '9999999.0'

    remarks = pycot.Remarks()
    _remarks = f"Squawk: {msg.get('Squawk')} Category: {emitter_category}"
    if flight:
        _remarks = f"{icao_hex}({flight}) {_remarks}"
    else:
        _remarks = f"{icao_hex} {_remarks}"

    if bool(os.environ.get('DEBUG')):
        _remarks = f"{_remarks} via stratuxcot"

    remarks.value = _remarks

    detail = pycot.Detail()
    detail.uid = uid
    detail.contact = contact
    detail.track = track
    detail.remarks = remarks

    event = pycot.Event()
    event.version = "2.0"
    event.event_type = cot_type
    event.uid = name
    event.time = time
    event.start = time
    event.stale = time + datetime.timedelta(seconds=stale)
    event.how = "m-g"
    event.point = point
    event.detail = detail

    return event


def hello_event():
    time = datetime.datetime.now(datetime.timezone.utc)
    name = 'stratuxcot'
    callsign = 'stratuxcot'

    point = pycot.Point()
    point.lat = '9999999.0'
    point.lon = '9999999.0'

    # FIXME: These values are static, should be dynamic.
    point.ce = '9999999.0'
    point.le = '9999999.0'
    point.hae = '9999999.0'

    uid = pycot.UID()
    uid.Droid = name

    contact = pycot.Contact()
    contact.callsign = callsign

    detail = pycot.Detail()
    detail.uid = uid
    detail.contact = contact

    event = pycot.Event()
    event.version = '2.0'
    event.event_type = 'a-u-G'
    event.uid = name
    event.time = time
    event.start = time
    event.stale = time + datetime.timedelta(hours=1)
    event.how = 'h-g-i-g-o'
    event.point = point
    event.detail = detail

    return event
