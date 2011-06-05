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

execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')

import time

from umit.common.CronParser import CronParser
from umit.icm.agent.Logging import log
from umit.icm.agent.test import test_name_by_id, test_by_id

########################################################################
class TestEntry(object):
    """"""
    __all__ = ['id', 'name']

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.parser = CronParser()
        self.run_time = self._CronTime()
        
    def __str__(self):
        return "(id=%d, name=%s, args=%s, cron_time=\"%s\", last_run_time=%s, "\
               "priority=%d, enabled=%s)" % \
               (self.id, 
                self.name, 
                self.args, 
                self.cron_time,
                self.last_run_time,
                self.priority,
                self.enabled)

    def set_run_time(self, cron_time):        
        time_ = cron_time.split()
        try:
            self.run_time.minute = self.parser.parse_minute(time_[0])
            self.run_time.hour = self.parser.parse_hour(time_[1])
            self.run_time.day = self.parser.parse_day(time_[2])
            self.run_time.month = self.parser.parse_month(time_[3])
            self.run_time.weekday = self.parser.parse_weekday(time_[4])            
        except:            
            log.error("Error in parsing cron time: %s" % cron_time)
        self.cron_time = cron_time
        
    def time_to_run(self, cur_time):
        if cur_time.tm_min in self.run_time.minute and \
           cur_time.tm_hour in self.run_time.hour and \
           cur_time.tm_mday in self.run_time.day and \
           cur_time.tm_mon in self.run_time.month and \
           cur_time.tm_wday in self.run_time.weekday:            
            log.debug("It's time to run '%s'" % self)
            return True
        else:
            return False

    class _CronTime(object):
        minute = None
        hour = None
        day = None
        month = None
        weekday = None
            
    id = 0
    name = None
    priority = 0
    cron_time = None
    run_time = None
    last_run_time = 0
    enabled = True
    args = {}
    run_flag = False
    
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
        test_entry.id = param['test_id']
        test_entry.name = test_name_by_id[test_entry.id]
        test_entry.set_run_time(param['run_time'])
        test_entry.args = param['args']
        if 'priority' in param:
            test_entry.priority = param['priority']
        self._test_list.append(test_entry)
        log.info("Test has been added. %s" % test_entry) 
        self.sort_by_priority()
    
    def remove_test(self, param):
        """"""
        id = param['test_id']
        args = param['args']
        
        for i in range(len(self._test_list)):
            if self._test_list[i].id == id:
                for arg in args:
                    if arg in self._test_list[i].args and \
                       args[arg] != self._test_list[i].args[arg]:
                        return
            entry = self._test_list.pop(i)
            log.info("Test has been removed. %s" % entry) 
            i = i - 1
    
    
    def remove_test_by_pos(self, index):        
        entry = self._test_list.pop(index-1)
        log.info("Test has been removed. %s" % entry) 
    
    def toggle_test_by_pos(self, index):
        self._test_list[index-1].enabled = not self._test_list[index-1].enabled
    
    def list_tests(self):
        for i in range(len(self._test_list)):
            print(str(i+1) + '. ' + str(self._test_list[i]))
        
    def get_test_list(self):
        """"""         
        return self._test_list
    
    def sort_by_priority(self):
        self._test_list.sort(cmp=lambda x,y: cmp(y.priority, x.priority))
        log.debug("Test list has been sorted by priority.")

g_test_manager = TestManager()
        
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
    
    