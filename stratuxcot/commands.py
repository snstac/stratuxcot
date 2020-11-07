#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Gateway Commands."""

import argparse
import asyncio
import concurrent
import os
import sys
import urllib

import pytak

import stratuxcot

if sys.version_info[:2] >= (3, 7):
    from asyncio import get_running_loop
else:
    from asyncio import _get_running_loop as get_running_loop

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2020 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


async def main(opts):
    loop = get_running_loop()

    tasks: set = set()
    event_queue: asyncio.Queue = asyncio.Queue(loop=loop)

    stratux_ws: urllib.parse.ParseResult = urllib.parse.urlparse(
        opts.stratux_ws)
    cot_url: urllib.parse.ParseResult = urllib.parse.urlparse(opts.cot_url)

    # CoT/TAK Event Workers (transmitters):
    if "http" in cot_url.scheme:
        eventworker = pytak.FTSClient(
            event_queue, cot_url.geturl(), opts.fts_token)
    elif "tcp" in cot_url.scheme:
        if ":" in cot_url.path:
            cot_host, cot_port = str(cot_url.path).split(":")
        else:
            cot_host = cot_url.path
            cot_port = pytak.DEFAULT_COT_PORT

        _, writer = await asyncio.open_connection(cot_host, cot_port)
        eventworker = pytak.EventWorker(event_queue, writer)

    # Stratux Receiver
    stratuxworker = stratuxcot.StratuxWorker(
        event_queue=event_queue,
        url=stratux_ws,
        cot_stale=opts.cot_stale
    )

    tasks.add(asyncio.ensure_future(eventworker.run()))
    tasks.add(asyncio.ensure_future(stratuxworker.run()))

    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        print(f"Task completed: {task}")


def cli():
    """Command Line interface for ADS-B Cursor-on-Target Gateway."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-U', '--cot_url', help='URL to CoT Destination.',
        required=True
    )
    parser.add_argument(
        '-W', '--stratux_ws', help='Stratux Websocket URL.',
        required=True
    )

    parser.add_argument(
        '-S', '--cot_stale', help='CoT Stale period, in seconds',
    )
    parser.add_argument(
        '-K', '--fts_token', help='FTS REST API Token'
    )
    opts = parser.parse_args()

    if sys.version_info[:2] >= (3, 7):
        asyncio.run(main(opts), debug=bool(os.environ.get('DEBUG')))
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main(opts))
        finally:
            loop.close()


if __name__ == '__main__':
    cli()
