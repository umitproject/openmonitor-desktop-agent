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

from umit.common.CronParser import CronParser
from umit.icm.agent.Global import g_logger
from umit.icm.agent.test import test_name_by_id, test_by_id

########################################################################
class TestEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.parser = CronParser()
        self.RunTime = self._CronTime()
        
    def __str__(self):
        return "(id=%d, name=%s, args=%s, cron_time=\"%s\", last_run_time=%s, "\
               "priority=%d, enabled=%s)" % \
               (self.ID, 
                self.Name, 
                self.Args, 
                self.CronTimeStr,
                self.LastRunTime,
                self.Priority,
                self.Enabled)

    def set_run_time(self, cron_time):        
        time_ = cron_time.split()
        try:
            self.RunTime.minute = self.parser.parse_minute(time_[0])
            self.RunTime.hour = self.parser.parse_hour(time_[1])
            self.RunTime.day = self.parser.parse_day(time_[2])
            self.RunTime.month = self.parser.parse_month(time_[3])
            self.RunTime.weekday = self.parser.parse_weekday(time_[4])            
        except:            
            g_logger.error("Error in parsing cron time: %s" % cron_time)
        self.CronTimeStr = cron_time
        
    def time_to_run(self, cur_time):
        if cur_time.tm_min in self.RunTime.minute and \
           cur_time.tm_hour in self.RunTime.hour and \
           cur_time.tm_mday in self.RunTime.day and \
           cur_time.tm_mon in self.RunTime.month and \
           cur_time.tm_wday in self.RunTime.weekday:            
            g_logger.debug("It's time to run '%s'" % self)
            return True
        else:
            return False

    class _CronTime(object):
        minute = None
        hour = None
        day = None
        month = None
        weekday = None
            
    ID = 0
    Name = None
    Priority = 0
    CronTimeStr = None
    RunTime = None
    LastRunTime = 0
    Enabled = True
    Args = {}
    RunFlag = False
    
########################################################################
class TestManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self._test_list = []  # a list of TestEntry
        
    def add_test(self, param):
        """"""
        test_entry = TestEntry()
        test_entry.ID = param['test_id']
        test_entry.Name = test_name_by_id[test_entry.ID]
        test_entry.set_run_time(param['run_time'])
        test_entry.Args = param['args']
        if 'priority' in param:
            test_entry.Priority = param['priority']
        self._test_list.append(test_entry)
        g_logger.info("Test has been added. %s" % test_entry) 
        self.sort_by_priority()
    
    def remove_test(self, param):
        """"""
        id_ = param['test_id']
        args = param['args']
        
        for i in range(len(self._test_list)):
            if self._test_list[i].ID == id_:
                for arg in args:
                    if arg in self._test_list[i].Args and \
                       args[arg] != self._test_list[i].Args[arg]:
                        return
            entry = self._test_list.pop(i)
            g_logger.info("Test has been removed. %s" % entry) 
            i = i - 1
        
    def remove_test_by_pos(self, index):        
        entry = self._test_list.pop(index-1)
        g_logger.info("Test has been removed. %s" % entry) 
    
    def toggle_test_by_pos(self, index):
        self._test_list[index-1].Enabled = not self._test_list[index-1].Enabled
    
    def list_tests(self):
        for i in range(len(self._test_list)):
            print(str(i+1) + '. ' + str(self._test_list[i]))
        
    def get_test_list(self):    
        return self._test_list
    
    def sort_by_priority(self):
        self._test_list.sort(cmp=lambda x,y: cmp(y.Priority, x.Priority))
        g_logger.debug("Test list has been sorted by priority.")

        
if __name__ == "__main__":
    g_test_manager = TestManager() 
    g_test_manager.add_test({'test_id':1, 'run_time':'*/2 * * * *', 
                 'args': {'url':'http://www.baidu.com'}, 'priority':3})
    g_test_manager.add_test({'test_id':2, 'run_time':'*/3 * * * *', 
                 'args': {'service':'ftp'}})
    g_test_manager.add_test({'test_id':1, 'run_time':'*/5 * * * *', 
                 'args': {'url':'http://www.sina.com'}, 'priority':2})
    g_test_manager.list_tests()
    #test_manager.toggle_test_by_pos(1)
    g_test_manager.sort_by_priority()
    g_test_manager.list_tests()
    #test_manager.remove_test({'test_id':1, 'run_time':'*/2 * * * *', 
                 #'args': {'url':'http://www.baidu.com'}})
    #test_manager.list_tests()
    #test_manager.remove_test_by_pos(1)
    #test_manager.list_tests()
    
    