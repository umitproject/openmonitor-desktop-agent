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

import time

from umit.icm.agent.test import test_by_id
from umit.icm.agent.Global import *

########################################################################
class TestScheduler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, test_manager):
        """Constructor"""
        self.test_manager = test_manager
        self.index = 0
        self._stop_flag = False
        
    def fetch_one_test(self):
        test_list = self.test_manager.get_test_list()
        for i in range(self.index, self.index+len(test_list)):
            idx = i % len(test_list)
            self.index = self.index + 1
            if test_list[idx].RunFlag and test_list[idx].Enabled:
                return test_list[idx]
            
        self.index = 0        
        return None
                
    def run_test(self, entry):
        entry.LastRunTime = time.time()
        entry.RunFlag = False
        test = test_by_id[entry.ID]()
        test.prepare(entry.Args)
        test.execute()
        
    def check_run_time(self):
        cur_time = time.gmtime()
        test_list = self.test_manager.get_test_list()
        for entry in test_list:
            if entry.time_to_run(cur_time):
                entry.RunFlag = True
                
    def run(self):
        last_min = -1
        while not self._stop_flag:  # run until the stop method is called
            cur_time = time.localtime()
            #g_logger.debug(cur_time)
            if cur_time.tm_min != last_min:
                self.check_run_time()  # using GMT time     
            last_min = cur_time.tm_min
        
            test_entry = self.fetch_one_test()
            
            if test_entry is None:  # no work to do, sleep until next minute
                #tt = time.localtime()
                #if cur_time.tm_sec < 59:
                    #tt1 = cur_time[:5] + (0,) + cur_time[6:]
                    #sleep_time = time.mktime(tt1) + 60 - time.mktime(tt)
                    #g_logger.debug("Sleep %d seconds." % sleep_time)
                    #time.sleep(sleep_time)
                #else:
                time.sleep(1)
            else:
                self.run_test(test_entry)
                
    def stop(self):
        self._stop_flag = True
        
if __name__ == "__main__":
    #g_task_manager.add_test({'test_id':1, 'run_time':'*/2 * * * *', 
                 #'args': {'url':'http://www.baidu.com'}})
    #g_task_manager.add_test({'test_id':2, 'run_time':'*/3 * * * *', 
                 #'args': {'service':'ftp'}})
    #g_task_manager.add_test({'test_id':1, 'run_time':'*/5 * * * *', 
                 #'args': {'url':'http://www.sina.com'}})    
    
    ts = TestScheduler()
    ts.fetch_one_test()