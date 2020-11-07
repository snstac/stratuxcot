#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Gateway Functions."""

import datetime

import pycot

import stratuxcot.constants

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


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

def icao_hex(addr) -> str:
    return str(hex(addr)).lstrip('0x')


def stratux_to_cot(msg: dict, cot_type: str = None, # NOQA pylint: disable=too-many-locals
                   stale: int = None) -> pycot.Event:
    """
    Transforms a Stratux to a Cursor-on-Target PLI.
    """
    time = datetime.datetime.now(datetime.timezone.utc)
    cot_type = cot_type or stratuxcot.constants.DEFAULT_TYPE
    stale = stale or stratuxcot.constants.DEFAULT_STALE

    lat = msg.get('Lat')
    lon = msg.get('Lng')
    if lat is None or lon is None:
        return None

    c_hex = icao_hex(msg.get('Icao_addr'))
    name = f"ICAO24.{c_hex}"
    flight = msg.get('Tail', '').strip()
    if flight:
        callsign = flight
    else:
        callsign = c_hex

    point = pycot.Point()
    point.lat = lat
    point.lon = lon
    point.ce = '9999999.0'
    point.le = '9999999.0'

    # alt_geom: geometric (GNSS / INS) altitude in feet referenced to the
    #           WGS84 ellipsoid
    alt_geom = int(msg.get('Alt', 0))
    if alt_geom:
        point.hae = alt_geom * 0.3048
    else:
        point.hae = '9999999.0'

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
    _remark = (f"ICAO24: {c_hex} Squawk: {msg.get('Squawk')} "
               f"SignalLevel: {msg.get('SignalLevel')}")
    if flight:
        remarks.value = f"Flight: {flight} " + _remark
    else:
        remarks.value = _remark

    detail = pycot.Detail()
    detail.uid = uid
    detail.contact = contact
    detail.track = track
    # Not supported by FTS 1.1?
    # detail.remarks = remarks

    event = pycot.Event()
    event.version = '2.0'
    event.event_type = cot_type
    event.uid = name
    event.time = time
    event.start = time
    event.stale = time + datetime.timedelta(seconds=stale)
    event.how = 'm-g'
    event.point = point
    event.detail = detail

    return event


def hello_event():
    time = datetime.datetime.now(datetime.timezone.utc)
    name = 'stratuxcot'
    callsign = 'stratuxcot'

    point = pycot.Point()
    point.lat = 0.0
    point.lon = 0.0

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
