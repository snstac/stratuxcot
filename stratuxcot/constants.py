#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Stratux Cursor-on-Target Constants."""

import logging
import os

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2020 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"


if bool(os.environ.get('DEBUG')):
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = logging.Formatter(
        ('%(asctime)s stratuxcot %(levelname)s %(name)s.%(funcName)s:%(lineno)d '
         ' - %(message)s'))
    logging.debug('stratuxcot Debugging Enabled via DEBUG Environment Variable.')
else:
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = logging.Formatter(
        ('%(asctime)s stratuxcot %(levelname)s - %(message)s'))

DEFAULT_EVENT_STALE: int = 120
