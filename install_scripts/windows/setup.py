#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008, 2009 Adriano Monteiro Marques
#
# Author: Tianwei Liu <liutianweidlut@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import re
import sys

from stat import *
from glob import glob

import os
import os.path
import shutil

if os.name == 'nt':
    try:
        import py2exe
        import py2exe.mf as modulefinder
        from py2exe.build_exe import py2exe as BuildExe
    except ImportError:
        import modulefinder
        print "Install py2exe to use setup.py"
        sys.exit(-1)
    import win32com
    for path in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", path)

from distutils.core import setup, Extension, Command
from distutils.command.install import install
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils import log, dir_util

from umit.icm.agent.Version import VERSION

from install_scripts.common import *
from install_scripts import common

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

###############################################################################
# Installation variables

# What to copy to the destiny
# Here, we define what should be put inside the directories set in the
# beginning of this file. This list contain tuples where the first element
# contains a path to where the other elements of the tuple should be installed.
# The first element is a path in the INSTALLATION PREFIX, and the other
# elements are the path in the source base.
# Ex: [("share/pixmaps", "/umit/trunk/share/pixmaps/test.png")]
# This will install the test.png file in the installation dir share/pixmaps.

file_path = []

def walk_dir(dir,topdown=True):
    for root,dirs,files in os.walk(dir, topdown):
        for name in files:
            #print root,name
            current_path = os.path.relpath(root, ROOT_DIR)
            file_path.append((current_path,[os.path.join(current_path, name)]))

walk_dir(os.path.join(ROOT_DIR,ICM_AGENT_ROOT))

data_files = file_path
         
##################### Umit banner #######################################
print
print "%s OpenMonitor Desktop Agent for Windows %s %s" % ("#" * 10, VERSION, "#" * 10)
print
#########################################################################

options = { 'py2exe': {
                        'compressed' : 1,  
                        'optimize': 2,
                        #'bundle_files':2, 
                        'packages' : [ 'encodings', 'email','glib','twisted','google','xml.etree'],
                        'includes' : ['gobject', 'pickle', 'bz2','xml.etree'
                                    ,'twisted.internet','sqlite3','Crypto',
                                    "cairo","gtk","gio","pango","pangocairo","atk",
                                    'OpenSSL','glib', 'google', 'google.protobuf', 'zope', 'zope.interface'],                          
                        'excludes': ['Tkinter', 'pdb',"pywin", "pywin.debugger"]
                     }
         } 


setup(
		name         = 'icm-agent',
		version      =  VERSION,
		description  = 'Open Monitor Desktop Agent made easy',
		author       = 'Umit Group',
		author_email = 'Umit-devel@lists.sourceforge.net',	
		url          = 'http://www.openmonitor.org',
		download_url = 'http://www.openmonitor.org',
		maintainer = 'Adriano Monteiro',
		maintainer_email = 'adriano@umitproject.org',		
		license      = 'GNU GPL 2',
		requires     = ['gtk'],
		platforms    = ['Platform Independent'],		
		zipfile 	 = "lib/library.zip",
		options = options,
		data_files   = data_files,
		scripts      = [os.path.join('.','bin','icm-agent')],
		
		windows = [{
			'dest_base': "icmagent",
            'script': r'bin\icm-agent',
            'uac_info' : 'requireAdministrator',
            'icon_resources' :[(1,r'share\images\icm-agent.ico') ]
            }],
		packages     = [
                      'bin','install_scripts',
                      'conf','tools',
                      'umit',
                      'umit.icm',
                      'umit.icm.agent',
                      'umit.icm.agent.core',
                      'umit.icm.agent.gui',
                      'umit.icm.agent.rpc',
                      'umit.icm.agent.secure',           
                      'umit.icm.agent.super', 
                      'umit.icm.agent.utils', 
		      'umit.common',	 
		      'umit.proto', 
		      'higwidgets',                              
                     ],
		package_dir  = {'.' : os.path.join(ROOT_DIR, '.')},
)

