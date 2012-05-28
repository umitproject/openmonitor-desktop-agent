#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
#
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

import os
import sys

__all__ = ['ROOT_DIR', 'CONFIG_DIR', 'LOG_DIR', 'LOCALES_DIR', 'IMAGES_DIR',
           'ICONS_DIR', 'DB_DIR', 'TMP_DIR',
           'CONFIG_PATH', 'DB_PATH','BIN_DIR']


encoding = sys.getfilesystemencoding()
if hasattr(sys,'frozen'):
    ROOT_DIR = os.path.dirname(unicode(sys.executable,encoding))
    ROOT_DIR = os.path.join(ROOT_DIR,'icmagent')  #the address is the EXE execute path
    BIN_DIR  = unicode(sys.executable,encoding)
else:
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
        new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
        if ROOT_DIR == new_dir:
            raise Exception("Can't find root dir.")
        ROOT_DIR = new_dir
    BIN_DIR = os.path.join(ROOT_DIR,'bin','icm-agent')  
          
CONFIG_DIR = os.path.join(ROOT_DIR, 'conf')
LOG_DIR = os.path.join(ROOT_DIR, 'log')
LOCALES_DIR = os.path.join(ROOT_DIR, 'share', 'locales')
IMAGES_DIR = os.path.join(ROOT_DIR, 'share', 'images')
ICONS_DIR = os.path.join(ROOT_DIR, 'share', 'icons')
DB_DIR = os.path.join(ROOT_DIR, 'share', 'db')
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')

if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

if not os.path.exists(LOCALES_DIR):
    os.mkdir(LOCALES_DIR)

if not os.path.exists(IMAGES_DIR):
    os.mkdir(IMAGES_DIR)

if not os.path.exists(ICONS_DIR):
    os.mkdir(ICONS_DIR)

if not os.path.exists(DB_DIR):
    os.mkdir(DB_DIR)

if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

CONFIG_PATH = os.path.join(CONFIG_DIR, 'agent.cfg')
DB_PATH = os.path.join(DB_DIR, 'storage.db3')