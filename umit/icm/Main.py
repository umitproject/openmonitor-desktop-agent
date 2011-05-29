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

from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

from twisted.internet import reactor

# find the root directory of icm-agent
ROOT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir
execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))

from umit.icm.gui.GtkMain import GtkMain
from umit.icm.tests.WebsiteTest import WebsiteTest
from umit.icm.tests.HTTPFetcher import HTTPFetcher

def main():
    """
    The Main function 
    """
    gtk_main = GtkMain()
    gtk_main.show_all()
        
    reactor.run()
    #test = WebsiteTest('https://www.alipay.com')
    #test.prepare()
    #test.execute() 
    
def quit():
    reactor.stop()


if __name__ == "__main__":
    main()
    