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
"""
This will create a thread for doing all sort of testing jobs
"""

execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')

import threading
import time

from umit.icm.agent import test
from umit.icm.agent.core.TestManager import g_test_manager
from umit.icm.agent.core.TestScheduler import TestScheduler
from umit.icm.agent.Logging import log

########################################################################
class TestThread(threading.Thread):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name='TestThread'):
        """Constructor"""
        threading.Thread.__init__(self, name=name)
        self.manager = g_test_manager
        self.scheduler = TestScheduler(g_test_manager)
        
    def run(self):
        log.info("Test thread started. Current version: %s" % 
                 test.TEST_PACKAGE_VERSION)

        g_test_manager.add_test({'test_id':1, 'run_time':'*/2 * * * *', 
                 'args': {'url':'http://www.baidu.com'}, 'priority':3})
        g_test_manager.add_test({'test_id':2, 'run_time':'*/3 * * * *', 
                 'args': {'service':'ftp'}})
        g_test_manager.add_test({'test_id':1, 'run_time':'* * * * *', 
                 'args': {'url':'http://www.sina.com'}, 'priority':2})
        
        self.scheduler.run()
        
    
    def stop(self):
        log.info("Test thread stoped.")
        
    
if __name__ == "__main__":
    rt = TestThread()
    rt.start()
    print('hello')
    