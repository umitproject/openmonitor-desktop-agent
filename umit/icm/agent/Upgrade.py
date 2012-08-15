#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutiawneidlut@gmail.com>
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
import subprocess

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Application import theApp

def onerror(func,path,exec_info):
    """
    shutil.rmtree callback(Attention:The rmtree cannot remove the readonly files in windows)
    """
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        g_logger.debug("rm:path%s"%path)    #ignore errors

def update_agent(result, *args, **kw):
    """
    update back
    """
    g_logger.info("Close task looping...")
    theApp.task_assgin_lc.stop()
    theApp.task_run_lc.stop()
    theApp.report_proc_lc.stop()
    theApp.test_sets_fetch_lc()    
    
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
    open(os.path.join(
        ROOT_DIR, 'umit', 'icm', 'agent', 'agent_restart_mark'), 'w').close()
    from twisted.internet import reactor
    reactor.callInThread(restart_agent, path)
    reactor.stop()
    g_logger.debug("reactor stopped.")

def restart_agent(path):
    while os.path.exists(
        os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running')):
        time.sleep(0.1)
    # Remove files
    remove_files = ["umit","bin","conf","deps","docs","install_scripts",
                    "share","tools"]
    for folder in remove_files:
        if os.name == 'nt':     #rmtree cannot remove the readonly files
            shutil.rmtree(os.path.join(ROOT_DIR, folder),onerror=onerror)
        else:
            shutil.rmtree(os.path.join(ROOT_DIR, folder))
    # Extract tarfile
    import tarfile
    t = tarfile.open(path)
    t.extractall(ROOT_DIR)
    #t.extractall(TMP_DIR)
    restart_function()

def restart_function():
    # Restart
    g_logger.info("Restarting Desktop Agent.")
    bin_path = os.path.join(ROOT_DIR, 'bin', 'icm-agent')
    subprocess.Popen([sys.executable, bin_path] + sys.argv[1:])
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
