stratuxcot - Stratux Cursor-on-Target Gateway.
**********************************************

.. image:: https://raw.githubusercontent.com/ampledata/stratuxcot/main/docs/screenshot-1604561447-25.png
   :alt: Screenshot of ADS-B PLI in ATAK.
   :target: https://github.com/ampledata/stratuxcot/blob/main/docs/screenshot-1604561447.png


The stratuxcot Stratux Cursor on Target Gateway transforms Stratux aircraft
position information into Cursor on Target (CoT) Position Location Information
(PLI) for display on Situational Awareness (SA) applications such as the
Android Team Awareness Kit (ATAK), WinTAK, RaptorX, et al.

Stratux messages are received via the /traffic Websocket.

CoT PLIs can be transmitted to SA clients using:

A. TCP Unicast to a specified host:port.
B. [COMING SOON] UDP Broadcast to a specified broadcast host:port or multicast host:port.
C. [COMING SOON] FreeTAKServer REST API.

For more information on the TAK suite of tools, see: https://www.civtak.org/

Installation
============

The Stratux to Cursor on Target Gateway is provided by a command-line tool
called `stratuxcot`, which can be installed either from the Python Package
Index, or directly from this source tree.

Install from the Python Package Index (PyPI)::

    $ pip install stratuxcot


Install from this source tree::

    $ git clone https://github.com/ampledata/stratuxcot.git
    $ cd stratuxcot/
    $ python setup.py install


Usage
=====

The `stratuxcot` command-line program has several runtime arguments::

    $ stratuxcot -h
    usage: stratuxcot [-h] -U COT_URL -W STRATUX_WS [-S COT_STALE] [-K FTS_TOKEN]

    optional arguments:
      -h, --help            show this help message and exit
      -U COT_URL, --cot_url COT_URL
                            URL to CoT Destination.
      -W STRATUX_WS, --stratux_ws STRATUX_WS
                            Stratux Websocket URL.
      -S COT_STALE, --cot_stale COT_STALE
                            CoT Stale period, in seconds
      -K FTS_TOKEN, --fts_token FTS_TOKEN
                            FTS REST API Token

Troubleshooting
===============

To report bugs, please set the DEBUG=1 environment variable to collect logs.

Unit Test/Build Status
======================

stratuxcot's current unit test and build status is available via Travis CI:

.. image:: https://travis-ci.com/ampledata/stratuxcot.svg?branch=master
    :target: https://travis-ci.com/ampledata/stratuxcot

Source
======
The source for stratuxcot can be found on Github: https://github.com/ampledata/stratuxcot

Author
======
stratuxcot is written and maintained by Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/

Copyright
=========
stratuxcot is Copyright 2020 Orion Labs, Inc. https://www.orionlabs.io

License
=======
stratuxcot is licensed under the Apache License, Version 2.0. See LICENSE for details.

Examples
========
Connect to the Stratux device at ws://172.17.2.188/traffic, and forward CoT to
TCP Port 8087 on Host 172.17.2.152::

    $ stratuxcot -U tcp:172.17.2.152:8087 -W ws://172.17.2.188/traffic


Running as a Daemon
===================
First, install supervisor::

    $ sudo yum install supervisor
    $ sudo service supervisord start

Create /etc/supervisor.d/stratuxcot.ini with the following content::

    [program:stratuxcot]
    command=stratuxcot -U tcp:172.17.2.152:8087 -W ws://172.17.2.188/traffic

And update supervisor::

    $ sudo supervisorctl update
