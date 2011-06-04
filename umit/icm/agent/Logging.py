#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__all__ = ['log', 'file_log']

import os
import sys

execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')

from umit.common.UmitLogging import Log
from umit.icm.agent.Basic import LOG_DIR

LOGLEVEL = 0
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
log_filename = os.path.join(LOG_DIR, 'icm-desktop.log')

log = Log("ICM Desktop Agent", LOGLEVEL)
open(log_filename, 'a')
file_log = Log("ICM Desktop Agent File Log", LOGLEVEL, log_filename)

if __name__ == "__main__":
    log.debug("Debug Message")
    log.info("Info Message")
    log.warning("Warning Message")
    log.error("Error Message")
    log.critical("Critical Message")

    file_log.debug("Debug Message")
    file_log.info("Info Message")
    file_log.warning("Warning Message")
    file_log.error("Error Message")
    file_log.critical("Critical Message")

