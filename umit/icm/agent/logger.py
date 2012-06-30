#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
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

__all__ = ['g_logger']

import os
import sys
import traceback

from umit.icm.agent.BasePaths import LOG_DIR
from umit.common.UmitLogging import Log


_levels = {
    'CRITICAL' : 50,
    'FATAL' : 50,
    'ERROR' : 40,
    'WARN' : 30,
    'WARNING' : 30,
    'INFO' : 20,
    'DEBUG' : 10,
    'NOTSET' : 0,
}
LOGLEVEL = 'DEBUG'

print LOG_DIR
#if not os.path.exists(LOG_DIR):
#    os.mkdir(LOG_DIR)
log_path = os.path.join(LOG_DIR, 'icm-desktop.log')

class ICMLog(Log):
    """Extends Log class for custom changes.
    """

    def error(self, string, *args, **kwargs):
        """Overrides method to add traceback if available.

        Since we may not be on an exception stack, first we should test if
        sys.exc_info() returns a traceback object.
        """
        exc_info = sys.exc_info()
        print string
        if exc_info:
            tb = exc_info[-1]
            traceback_string = "\n".join(
                ["=FULL TRACEBACK=================="]  + \
                traceback.format_tb(tb)                + \
                ["=================================="]
            )
            string += "\n%s" % traceback_string

        
        return super(ICMLog, self).error(string, *args, **kwargs)




        
g_logger = ICMLog("ICM Desktop Agent", _levels[LOGLEVEL], log_path)
open(log_path, 'w')


