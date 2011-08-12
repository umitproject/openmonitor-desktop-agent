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

# find root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir

execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))

# check if there's GTK environment
useGTK = True
if useGTK:
    if 'twisted.internet.reactor' in sys.modules:
        del sys.modules['twisted.internet.reactor']
    from twisted.internet import gtk2reactor # for gtk-2.0
    gtk2reactor.install()

from umit.icm.agent.Application import theApp

def main(args):
    if useGTK:
        theApp.use_gui = True
    else:
        theApp.use_gui = False
    theApp.start()

if __name__ == "__main__":
    main(sys.argv)