stratuxcot - Stratux Cursor-on-Target Gateway.
**********************************************

.. image:: https://raw.githubusercontent.com/ampledata/stratuxcot/main/docs/screenshot_18452-50.png
   :alt: Screenshot of ADS-B PLI in ATAK.
   :target: https://github.com/ampledata/stratuxcot/blob/main/docs/screenshot_18452.png


The Stratux Cursor-On-Target Gateway (StratuxCOT) transforms Stratux aircraft
position information into Cursor on Target Position Location Information for 
display on Situational Awareness applications such as the Android Team 
Awareness Kit (ATAK), WinTAK, RaptorX, et al. For more information on the TAK 
suite of tools, see: https://www.tak.gov/

For more information on the Stratux Portable ADS-B receiver, see: http://stratux.me/

StratuxCOT uses the `Python Team Awareness Kit (PyTAK) <https://github.com/ampledata/pytak>`_ module.

Support Development
===================

**Tech Support**: Email support@undef.net or Signal/WhatsApp: +1-310-621-9598

This tool has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to users. Any contribution you can make to further this project's development
efforts is greatly appreciated.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support Development: Buy me a coffee!


Installation
============

Functionality provided by a command-line tool called ``stratuxcot``, which can 
be installed several ways.

**Preferred Method** Installing as a Debian/Ubuntu Package::

    $ wget https://github.com/ampledata/aircot/releases/latest/download/python3-aircot_latest_all.deb
    $ sudo apt install -f ./python3-aircot_latest_all.deb
    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/stratuxcot/releases/latest/download/python3-stratuxcot_latest_all.deb
    $ sudo apt install -f ./python3-stratuxcot_latest_all.deb

**Alternate Method** Install from the Python Package Index::

    $ python3 -m pip install -U aircot
    $ python3 -m pip install -U pytak
    $ python3 -m pip install -U stratuxcot

**For Developers** Install from this source tree::

    $ git clone https://github.com/ampledata/stratuxcot.git
    $ cd stratuxcot/
    $ python3 setup.py stratuxcot


Usage
=====

The ``stratuxcot`` command-line program has several runtime arguments::

    $ stratuxcot -h
    usage: stratuxcot [-h] [-c CONFIG_FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE Default: config.ini


Configuration
=============
Configuration parameters can be specified either via environment variables or in
a INI-stile configuration file.

Parameters:

* **STRATUX_WS**: Stratux Websocket URL. Default: ``ws://stratux.local/traffic```
* **COT_URL**: (*optional*) Destination for Cursor-On-Target messages. See `PyTAK <https://github.com/ampledata/pytak#configuration-parameters>`_ for options.
* **KNOWN_CRAFT**: (*optional*) CSV-style aircraft hints file for overriding callsign, icon, COT Type, etc.
* **INCLUDE_ALL_CRAFT**: (*optional*) If set & KNOWN_CRAFT is set, will include aircraft not in KNOWN_CRAFT.

There are other configuration parameters available via `PyTAK <https://github.com/ampledata/pytak#configuration-parameters>`_.

Configuration parameters are imported in the following priority order:

1. ``config.ini`` (if exists) or ``-c <filename>`` (if specified).
2. Environment Variables (if set).
3. Defaults.


Running as a Service
====================

It's recommended to run ``stratuxcot`` as a service ("daemon") using a built-in service manager like systemd.

To accomplish this, first create the file ``/etc/systemd/system/stratuxcot.service``::

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
    command=stratuxcot -c /home/pi/stratux-config.ini

And update supervisor::

    $ sudo supervisorctl update


Source
======
The source for stratuxcot can be found on Github: https://github.com/ampledata/stratuxcot


Author
======
stratuxcot is written and maintained by Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/


Copyright
=========
stratuxcot is Copyright 2022 Greg Albrecht


License
=======
Copyright 2022 Greg Albrecht <oss@undef.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
