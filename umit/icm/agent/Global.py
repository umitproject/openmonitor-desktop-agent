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

__all__ = ['g_config', 'g_logger', 'g_db_helper',
           'ROOT_DIR', 'CONFIG_DIR', 'LOG_DIR', 'LOCALES_DIR', 'IMAGES_DIR',
           'ICONS_DIR', 'DB_DIR', 'TMP_DIR']

import os

from umit.icm.agent.BasePaths import *

#----------------------------------------------------------------------
from umit.icm.agent.ICMConfig import ICMConfig
g_config = ICMConfig(os.path.join(CONFIG_DIR, 'agent_config.txt'))

#----------------------------------------------------------------------
from umit.common.UmitLogging import Log
LOGLEVEL = g_config.get('logging', 'log_level')
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
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
log_filename = os.path.join(LOG_DIR, 'icm-desktop.log')

open(log_filename, 'w')
g_logger = Log("ICM Desktop Agent", _levels[LOGLEVEL], log_filename)

#----------------------------------------------------------------------
from umit.icm.agent.utils.DBHelper import DBHelper
g_db_helper = DBHelper('sqlite')
g_db_helper.connect(os.path.join(DB_DIR, 'storage.db3'))
