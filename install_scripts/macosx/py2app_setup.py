# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
#                           <cleber@globalred.com.br>
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
# Override the setup name in the main setup.py
from setuptools import setup



if hasattr(sys,'frozen'):
    ROOT_DIR = os.path.dirname(unicode(sys.executable,encoding))
    ROOT_DIR = os.path.join(ROOT_DIR,'icmagent')  #the address is the EXE execute path
else:
    ROOT_DIR = os.path.abspath(
                    os.path.join(os.path.dirname(unicode(__file__,encoding)),os.path.pardir))
        
if os.path.exists(os.path.join(ROOT_DIR,'umit')):
     sys.path.insert(0, ROOT_DIR)
     execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))
     sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'higwidgets'))
else:
     raise Exception("Can't find root dir.")

from install_scripts import common



# py2app requires the values in the app's list to have known extensions, but
# bin/umit doesn't. Here bin/umit is renamed to bin/umit_main.py and the old
# name is stored in common.OLD_UMIT_MAIN so it can be renamed again later.
import shutil
shutil.move(common.UMIT_MAIN, common.UMIT_MAIN + '_main.py')
common.OLD_UMIT_MAIN = common.UMIT_MAIN
common.UMIT_MAIN = os.path.join(common.BIN_DIRNAME, 'umit_main.py')

def revert_rename():
    if not hasattr(common, 'OLD_UMIT_MAIN'):
        # The rename hasn't happened.
        return
    shutil.move(common.UMIT_MAIN, common.OLD_UMIT_MAIN)

py2app_options = dict(
        app = [common.UMIT_MAIN],
        options = {'py2app': {
            'argv_emulation': True,
            'compressed': True,
            'packages': [ "gobject", "gtk", "cairo"],
            'includes': ["atk", "pango", "pangocairo"]
            }
            },
        setup_requires = ["py2app"]
        )
