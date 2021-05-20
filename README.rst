stratuxcot - Stratux Cursor-on-Target Gateway.
**********************************************

.. image:: https://raw.githubusercontent.com/ampledata/stratuxcot/main/docs/screenshot-1604561447-25.png
   :alt: Screenshot of ADS-B PLI in ATAK.
   :target: https://github.com/ampledata/stratuxcot/blob/main/docs/screenshot-1604561447.png


The Stratux Cursor on Target Gateway transforms Stratux aircraft
position information into Cursor on Target (CoT) Position Location Information
(PLI) for display on Situational Awareness (SA) applications such as the
Android Team Awareness Kit (ATAK), WinTAK, RaptorX, et al.

Stratux messages are received via the /traffic Websocket.

For more information on the TAK suite of tools, see: https://www.civtak.org/

For more information on the Stratux Portable ADS-B receiver, see: http://stratux.me/

Installation
============

The Stratux to Cursor on Target Gateway is provided by a command-line tool
called `stratuxcot`, which can be installed several ways.

Installing as a Debian/Ubuntu Package::

    $ wget https://github.com/ampledata/aircot/releases/latest/download/python3-aircot_latest_all.deb
    $ sudo apt install -f ./python3-aircot_latest_all.deb
    $ wget https://github.com/ampledata/stratuxcot/releases/latest/download/python3-stratuxcot_latest_all.deb
    $ sudo apt install -f ./python3-stratuxcot_latest_all.deb

Install from the Python Package Index::

    $ pip install stratuxcot


Install from this source tree::

    $ git clone https://github.com/ampledata/stratuxcot.git
    $ cd aircot/
    $ python setup.py stratuxcot


Usage
=====

The `stratuxcot` command-line program has several runtime arguments::

    $ stratuxcot -h
    usage: stratuxcot [-h] [-c CONFIG_FILE] [-d] [-U COT_URL] [-W STRATUX_WS] [-S COT_STALE] [-F FILTER_CONFIG] [-K KNOWN_CRAFT]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE
      -d, --DEBUG           Enable DEBUG logging
      -U COT_URL, --COT_URL COT_URL
                            URL to CoT Destination. Must be a URL, e.g. tcp:1.2.3.4:1234 or tls:...:1234, etc.
      -W STRATUX_WS, --STRATUX_WS STRATUX_WS
                            Stratux Websocket URL.
      -S COT_STALE, --COT_STALE COT_STALE
                            CoT Stale period, in seconds
      -F FILTER_CONFIG, --FILTER_CONFIG FILTER_CONFIG
                            FILTER_CONFIG
      -K KNOWN_CRAFT, --KNOWN_CRAFT KNOWN_CRAFT
                            KNOWN_CRAFT

Troubleshooting
===============

To report bugs, please set the DEBUG=1 environment variable to collect logs.

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
