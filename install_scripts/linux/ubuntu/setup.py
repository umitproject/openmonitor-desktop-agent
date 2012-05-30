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

from distutils.core import setup, Extension, Command
from distutils.command.install import install
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils import log, dir_util

from icmagent.umit.icm.agent.Version import VERSION

from icmagent.install_scripts.common import *
from icmagent.install_scripts import common

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

"""data_files = [
        (IMAGES_DIR,
            glob(os.path.join(IMAGES_DIR, '*.ico')) +
            glob(os.path.join(IMAGES_DIR, '*.png')) +
            glob(os.path.join(IMAGES_DIR, '*.xpm')) +
            glob(os.path.join(IMAGES_DIR, '*.gif'))),
        (ICONS_DIR,
            glob(os.path.join(ICONS_DIR, '*.ico')) + 
            glob(os.path.join(ICONS_DIR, '*.png'))),
        (CONFIG_DIR,
            [os.path.join(CONFIG_DIR, 'agent.cfg')]),
        (LOG_DIR,
            glob(os.path.join(LOG_DIR, '*.log'))),
        #(LOCALES_DIR,
        #    glob(os.path.join(LOCALES_DIR, '*.*')))
        (DB_DIR,
            [os.path.join(DB_DIR, 'storage.db3')])
        #(DOCS_DIR,
        #    [os.path.join(DOCS_DIR, 'README')])
        ]"""
 
##############################################################################
# Distutils subclasses

class icm_agent_install(install):
    """
    """
    def initialize_options(self):
        install.initialize_options(self)
        
    def run(self):
        install.run(self)
            
class icm_agent_build(build):
    """
    """
    def run(self):
        build.run(self)
        
class icm_agent_sdist(sdist):
    """
    """
    def run(self):
        sdist.run(self)

##################### Umit banner #######################################
print
print "%s OpenMonitor Desktop Agent for Linux %s %s" % ("#" * 10, VERSION, "#" * 10)
print
#########################################################################

cmdclasses = {
              "install":icm_agent_install,
              "build":icm_agent_build,
              "sdist":icm_agent_sdist
              }

setup(name         = 'icm-agent',
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
#     packages     = ['icmagent',
#                      'icmagent.bin','icmagent.install_scripts',
#                      'icmagent.conf','icmagent.tools',
#                      'icmagent.umit',
#                      'icmagent.umit.icm',
#                      'icmagent.umit.icm.agent',
#                      'icmagent.umit.icm.agent.core',
#                      'icmagent.umit.icm.agent.gui',
#                      'icmagent.umit.icm.agent.rpc',
#                      'icmagent.umit.icm.agent.secure',           
#                      'icmagent.umit.icm.agent.super', 
#                      'icmagent.umit.icm.agent.utils',                                 
#                     ],
#     package_dir  = {'icmagent' : os.path.join(ROOT_DIR, 'icmagent')},
      data_files   = data_files,
      cmdclass     = cmdclasses,
      #scripts      = [os.path.join(BIN_DIRNAME,
      #                             'icm-agent')],
      classifiers = [
            'Development Status :: 1 - Alpha',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: System :: Networking',
            ]
)
