#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stratux Cursor-on-Target Gateway.

"""
Stratux Cursor-on-Target Gateway.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2021 Orion Labs, Inc.
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/stratuxcot>

"""

from .constants import LOG_FORMAT, LOG_LEVEL, DEFAULT_COT_STALE  # NOQA

from .functions import stratux_to_cot  # NOQA

from .classes import StratuxWorker  # NOQA

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"
