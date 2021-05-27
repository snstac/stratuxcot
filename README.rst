stratuxcot - Stratux Cursor-on-Target Gateway.
**********************************************

.. image:: https://raw.githubusercontent.com/ampledata/stratuxcot/main/docs/screenshot_18452.png
   :alt: Screenshot of ADS-B PLI in ATAK.
   :target: https://github.com/ampledata/stratuxcot/blob/main/docs/screenshot_18452.png


The Stratux Cursor on Target Gateway transforms Stratux aircraft
position information into Cursor on Target (CoT) Position Location Information
(PLI) for display on Situational Awareness (SA) applications such as the
Android Team Awareness Kit (ATAK), WinTAK, RaptorX, et al.

Stratux messages are received via the /traffic Websocket.

For more information on the TAK suite of tools, see: https://www.civtak.org/

For more information on the Stratux Portable ADS-B receiver, see: http://stratux.me/

Support StratuxCoT Development
==============================

StratuxCoT has been developed for the Disaster Response, Public Safety and Frontline community at-large. This software
is currently provided at no-cost to our end-users. All development is self-funded and all time-spent is entirely
voluntary. Any contribution you can make to further these software development efforts, and the mission of StratuxCoT
to provide ongoing SA capabilities to our end-users, is greatly appreciated:

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support StratuxCoT development: Buy me a coffee!


Installation
============

The Stratux to Cursor on Target Gateway is provided by a command-line tool
called `stratuxcot`, which can be installed several ways.

Installing as a Debian/Ubuntu Package::

    $ wget https://github.com/ampledata/aircot/releases/latest/download/python3-aircot_latest_all.deb
    $ sudo apt install -f ./python3-aircot_latest_all.deb
    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/stratuxcot/releases/latest/download/python3-stratuxcot_latest_all.deb
    $ sudo apt install -f ./python3-stratuxcot_latest_all.deb

Install from the Python Package Index::

    $ python3 -m pip install -U stratuxcot


Install from this source tree::

    $ git clone https://github.com/ampledata/stratuxcot.git
    $ cd stratuxcot/
    $ python setup.py stratuxcot

If you'd like to run `stratuxcot` side-by-side on the Stratux Raspberry Pi, Paul has put together an excellent
guide:

https://github.com/ampledata/stratuxcot/blob/main/docs/Stratux_-_Mobile_Station_Set-up.pdf

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
stratuxcot is Copyright 2021 Orion Labs, Inc. https://www.orionlabs.io

License
=======
stratuxcot is licensed under the Apache License, Version 2.0. See LICENSE for details.

Examples
========
Connect to the Stratux device at ws://172.17.2.188/traffic, and forward CoT to
TCP Port 8087 on Host 172.17.2.152::

    $ stratuxcot -U tcp:172.17.2.152:8087 -W ws://172.17.2.188/traffic


Running as a Service
====================

It's recommended to run `stratuxcot` as a service ("daemon") using a built-in service manager like systemd.

To accomplish this, first create the file `/etc/systemd/system/stratuxcot.service`::

     [Unit]
     Description=StratuxCoT Service
     After=multi-user.target
     [Service]
     ExecStart=/usr/local/bin/stratuxcot -U tcp:x.x.x.x:8088 -W ws://127.0.0.1/traffic
     Restart=always
     RestartSec=5
     Environment=DEBUG=1
     [Install]
     WantedBy=multi-user.target

Then, it's as easy as::

    $ sudo systemctl enable stratuxcot.service
    $ sudo systemctl start stratuxcot.service

To see status & logs::

    $ sudo systemctl status stratuxcot.service
    $ sudo journalctl -xe

Alternatively, you can use supervisord::

    $ sudo yum install supervisor
    $ sudo service supervisord start

Create /etc/supervisor.d/stratuxcot.ini with the following content::

    [program:stratuxcot]
    command=stratuxcot -U tcp:172.17.2.152:8087 -W ws://172.17.2.188/traffic

And update supervisor::

    $ sudo supervisorctl update
