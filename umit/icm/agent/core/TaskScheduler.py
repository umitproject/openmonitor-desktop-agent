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

from zope.interface import implements
from twisted.internet.interfaces import IPushProducer

from umit.icm.agent.logger import g_logger
from umit.icm.agent.test import test_by_id
from umit.icm.agent.Global import *


class TaskScheduler(object):
    """"""

    implements(IPushProducer)

    #----------------------------------------------------------------------
    def __init__(self, task_manager, report_manager):
        """Constructor"""
        self.task_manager = task_manager
        self.report_manager = report_manager
        #self.index = 0

    """ Deprecated """
    def _fetch_one_test(self):
        task_list = self.task_manager.task_list
        for i in range(self.index, self.index+len(task_list)):
            idx = i % len(task_list)
            self.index = self.index + 1
            if task_list[idx].RunFlag and task_list[idx].Enabled:
                return task_list[idx]

        self.index = 0
        return None

    """ Deprecated """
    def _run_test(self, entry):
        entry.LastRunTime = time.time()
        entry.RunFlag = False
        test = test_by_id[entry.ID]()
        test.prepare(entry.Args)
        test.execute()

    def check_run_time(self):
        cur_time = time.gmtime()
        for entry in self.task_manager.task_list:
            if entry.time_to_run(cur_time):
                entry.RunFlag = True

    def schedule(self):
        #cur_time = time.localtime()
        #g_logger.debug(cur_time)
        #if cur_time.tm_min != last_min:
        #last_min = cur_time.tm_min

        self.check_run_time()  # using GMT time
        for entry in self.task_manager.task_list:
            if entry.Enabled and entry.RunFlag:
                entry.LastRunTime = time.time()
                entry.RunFlag = False
                test = test_by_id[entry.ID]()
                test.prepare(entry.Args)
                defer_ = test.execute()
                if defer_ is not None:
                    defer_.addCallback(self.report_manager.add_report)

        #test_entry = self.fetch_one_test()

        #if test_entry is None:  # no work to do, sleep until next minute
            ##tt = time.localtime()
            ##if cur_time.tm_sec < 59:
                ##tt1 = cur_time[:5] + (0,) + cur_time[6:]
                ##sleep_time = time.mktime(tt1) + 60 - time.mktime(tt)
                ##g_logger.debug("Sleep %d seconds." % sleep_time)
                ##time.sleep(sleep_time)
            ##else:
            #time.sleep(1)
        #else:
            #self.run_test(test_entry)


if __name__ == "__main__":
    #g_task_manager.add_test({'test_id':1, 'run_time':'*/2 * * * *',
                 #'args': {'url':'http://www.baidu.com'}})
    #g_task_manager.add_test({'test_id':2, 'run_time':'*/3 * * * *',
                 #'args': {'service':'ftp'}})
    #g_task_manager.add_test({'test_id':1, 'run_time':'*/5 * * * *',
                 #'args': {'url':'http://www.sina.com'}})

    ts = TestScheduler()
    ts.fetch_one_test()