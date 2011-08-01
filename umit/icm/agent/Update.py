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
import shutil
import sys
import time
import zlib

from umit.icm.agent.Global import *

def update_agent(result, *args, **kw):
    g_logger.info("Updating Desktop Agent...")
    # args = ((version, check_code=0), {})
    version = args[0]
    if len(args) == 2:
        check_code = args[1]
    else:
        check_code = 0

    filename = 'icm-agent_' + version + '.tar.gz'
    path = os.path.join(TMP_DIR, filename)
    if not os.path.exists(path):
        g_logger.error("Package %s can't be found under '/tmp' folder." %
                       filename)
        return

    if check_code != 0:
        # Verify if the file is the correct one
        content = open(filename, 'rb').read()
        crc = zlib.crc32(content) & 0xffffffff
        if crc != check_code:
            g_logger.error("Package %s is corrupt. Try to download it again." %
                           filename)
            return
    # Stop current agent
    from twisted.internet import reactor
    reactor.callInThread(restart_agent, path)
    reactor.stop()
    g_logger.debug("reactor stopped.")

def restart_agent(path):
    while os.path.exists(
        os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running')):
        time.sleep(0.1)
    # Remove files
    shutil.rmtree(os.path.join(ROOT_DIR, 'umit'))
    # Extract tarfile
    import tarfile
    t = tarfile.open(path)
    t.extractall(ROOT_DIR)
    # Restart
    g_logger.info("Restarting Desktop Agent.")
    bin_path = os.path.join(ROOT_DIR, 'bin', 'icm-agent.py')
    print(sys.argv)
    #os.execvp(sys.argv[0], sys.argv)
    execfile(sys.argv[0])
    g_logger.info("Desktop Agent Updated.")

def update_test_mod(result, *args, **kw):
    g_logger.info("Updating Test Module...")
    # args = ((version, check_code=0), {})
    version = args[0]
    if len(args) == 2:
        check_code = args[1]
    else:
        check_code = 0

    filename = 'test_' + version + '.py'
    path = os.path.join(TMP_DIR, filename)
    if not os.path.exists(path):
        g_logger.error("Test mod %s can't be found under '/tmp' folder." %
                       filename)
        return

    if check_code != 0:
        # Verify if the file is the correct one
        content = open(filename, 'rb').read()
        crc = zlib.crc32(content) & 0xffffffff
        if crc != check_code:
            g_logger.error("Test mod %s is corrupt. Try to download it again." %
                           filename)
            return

    # Rename the original test.py to test.py.bak,
    # and replace test.py with new one
    origin = os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'test.py')
    shutil.copy(origin, origin + '.bak')
    shutil.copy(path, origin)
    if 'umit.icm.agent.test' in sys.modules:
        reload(sys.modules['umit.icm.agent.test'])
    g_logger.info("Test Module updated.")


if __name__ == "__main__":
    pass
