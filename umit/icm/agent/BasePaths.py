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

import os
import sys

__all__ = ['ROOT_DIR', 'CONFIG_DIR', 'LOG_DIR', 'LOCALES_DIR', 'IMAGES_DIR',
           'ICONS_DIR', 'DB_DIR', 'TMP_DIR']

ROOT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir

#ROOT_DIR = "F:\\workspace\\PyWork\\icm-agent\\"

CONFIG_DIR = os.path.join(ROOT_DIR, 'conf')
LOG_DIR = os.path.join(ROOT_DIR, 'log')
LOCALES_DIR = os.path.join(ROOT_DIR, 'share', 'locales')
IMAGES_DIR = os.path.join(ROOT_DIR, 'share', 'images')
ICONS_DIR = os.path.join(ROOT_DIR, 'share', 'icons')
DB_DIR = os.path.join(ROOT_DIR, 'share', 'db')
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')