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
Entrance of ICM Desktop Agent
"""

try:
    execfile('E:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

import os
import signal
import sys
import time

from twisted.internet import reactor
from twisted.internet import task

from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from umit.icm.agent.Version import VERSION

class Application(object):
    def __init__(self):
        self._auth = False

    def _initialize(self):
        from umit.icm.agent.core.TaskManager import TaskManager
        self.task_manager = TaskManager()

        from umit.icm.agent.core.ReportManager import ReportManager
        self.report_manager = ReportManager()

        from umit.icm.agent.core.PeerManager import PeerManager
        self.peer_manager = PeerManager()

        from umit.icm.agent.core.ReportUploader import ReportUploader
        self.report_uploader = ReportUploader(self.report_manager)

        from umit.icm.agent.core.TaskScheduler import TaskScheduler
        self.task_scheduler = TaskScheduler(self.task_manager,
                                            self.report_manager)

        from umit.icm.agent.core.PeerInfo import PeerInfo
        self.peer_info = PeerInfo()

        from umit.icm.agent.rpc.aggregator import AggregatorAPI
        self.aggregator = AggregatorAPI(
            g_db_helper.get_config('aggregator_url'))

    def start(self):
        """
        The Main function
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)

        # Initialize components
        self._initialize()

        open(os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running'), \
             'w').close()

        # Start backend service
        self.listen_port = g_config.getint('network', 'listen_port')
        from umit.icm.agent.rpc.AgentService import AgentFactory
        self.factory = AgentFactory()
        g_logger.info("Listening on port %d.", self.listen_port)
        reactor.listenTCP(self.listen_port, self.factory)

        if self.use_gui:
            # Init GUI
            from umit.icm.agent.gui.GtkMain import GtkMain
            self.gtk_main = GtkMain()

        # for test
        self.task_manager.add_test({'test_id':1, 'run_time':'*/2 * * * *',
                     'args': {'url':'http://www.baidu.com'}, 'priority':3})
        self.task_manager.add_test({'test_id':2, 'run_time':'*/3 * * * *',
                     'args': {'service':'ftp'}})
        self.task_manager.add_test({'test_id':1, 'run_time':'*/5 * * * *',
                     'args': {'url':'http://www.sina.com'}, 'priority':2})

        self.peer_maintain_lc = task.LoopingCall(self.peer_manager.maintain)
        self.peer_maintain_lc.start(30)

        self.task_run_lc = task.LoopingCall(self.task_scheduler.schedule)
        self.task_run_lc.start(30)

        self.report_proc_lc = task.LoopingCall(self.report_uploader.process)
        self.report_proc_lc.start(5)

        reactor.addSystemEventTrigger('before', 'shutdown', self.quit)
        reactor.run()

    def quit(self):
        g_logger.info("ICM Agent quit.")

        if hasattr(self, 'peer_info'):
            self.peer_info.save()

        if hasattr(self, 'peer_manager'):
            self.peer_manager.save_to_db()

        os.remove(os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running'))
        #self.db_engine.stop()

theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
