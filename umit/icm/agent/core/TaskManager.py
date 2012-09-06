#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
#         
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

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id, test_by_id

class TestEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = 0
        self.Name = None
        self.Priority = 0
        self.CronTimeStr = None
        self.RunTime = None
        self.LastRunTime = 0
        self.Enabled = True
        self.Args = {}
        self.RunFlag = False

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


#---------------------------------------------------------------------
class TaskManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.task_list = []  # a list of TestEntry

    def add_test(self, test_id, exec_time, args, priority=0):
        """"""
        test_entry = TestEntry()
        test_entry.ID = test_id
        test_entry.Name = test_name_by_id[test_entry.ID]
        test_entry.set_run_time(exec_time)
        test_entry.Args = args
        test_entry.Priority = priority
        
        self.task_list.append(test_entry)
        g_logger.info("Test has been added. %s" % test_entry)
        self.sort_by_priority()
        theApp.statistics.tasks_current_num = theApp.statistics.tasks_current_num + 1

    def remove_test(self, test_id, args):
        """"""
        for i in range(len(self.task_list)):
            entry = self.task_list[i]
            if entry.ID == test_id:
                flag = True
                for arg in args:
                    if arg in entry.Args and args[arg] != entry.Args[arg]:
                        flag = False
                if flag:
                    entry = self.task_list.pop(i)
                    g_logger.info("Test has been removed. %s" % entry)
                    theApp.statistics.tests_total = \
                          theApp.statistics.tasks_current_num - 1
                    i = i - 1

    def remove_test_by_pos(self, index):
        entry = self.task_list.pop(index-1)
        g_logger.info("Test has been removed. %s" % entry)
        theApp.statistics.tasks_current_num = theApp.statistics.tasks_current_num - 1

    def toggle_test_by_pos(self, index):
        self.task_list[index-1].Enabled = not self.task_list[index-1].Enabled

    def list_tests(self):
        for i in range(len(self.task_list)):
            print(str(i+1) + '. ' + str(self.task_list[i]))

    def sort_by_priority(self):
        self.task_list.sort(cmp=lambda x,y: cmp(y.Priority, x.Priority))
        g_logger.debug("Test list has been sorted by priority.")


if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.add_test(1, '*/10 * * * *', {'url':'http://www.baidu.com'}, 3)
    task_manager.add_test(2, '*/6 * * * *', {'service':'ftp'})
    task_manager.add_test(1, '*/3 * * * *', {'url':'http://www.sina.com'}, 2)
    task_manager.list_tests()
    #task_manager.toggle_test_by_pos(1)
    task_manager.sort_by_priority()
    task_manager.list_tests()
    #task_manager.remove_test({'test_id':1, 'run_time':'*/2 * * * *',
                 #'args': {'url':'http://www.baidu.com'}})
    #task_manager.list_tests()
    #task_manager.remove_test_by_pos(1)
    #task_manager.list_tests()

