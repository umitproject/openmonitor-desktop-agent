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

__all__ = ['g_config', 'g_db_helper']

import os
import sys

from umit.icm.agent.BasePaths import *

#----------------------------------------------------------------------
from umit.icm.agent.config import FileConfig, DBConfig

useFileConf = True
if useFileConf:
    try:
        g_config = FileConfig(CONFIG_PATH)
    except IOError:
        from umit.icm.agent.utils import CreateConf
        CreateConf.create_file_conf(CONFIG_PATH)
        g_config = FileConfig(CONFIG_PATH)
else:
    try:
        g_config = DBConfig(DB_PATH)
    except IOError:
        from umit.icm.agent.utils import CreateConf
        CreateConf.create_db_conf(DB_PATH)
        g_config = DBConfig(DB_PATH)

#----------------------------------------------------------------------
from umit.icm.agent.db import DBHelper

try:
    g_db_helper = DBHelper('sqlite')
    g_db_helper.connect(DB_PATH)
except IOError:
    from umit.icm.agent.utils import CreateDB
    CreateDB.create(DB_PATH)
    g_db_helper.connect(DB_PATH)
