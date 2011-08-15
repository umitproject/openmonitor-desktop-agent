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
        pass

    def _initialize(self):
        # Initialize components
        self._init_components()
        self._load_from_db()

        # Create agent service
        self.listen_port = g_config.getint('network', 'listen_port')
        from umit.icm.agent.rpc.AgentService import AgentFactory
        self.factory = AgentFactory()
        g_logger.info("Listening on port %d.", self.listen_port)
        reactor.listenTCP(self.listen_port, self.factory)
        # Create mobile agent service
        from umit.icm.agent.rpc.mobile import MobileAgentService
        self.ma_service = MobileAgentService()

        if self.use_gui:
            # Init GUI
            from umit.icm.agent.gui.GtkMain import GtkMain
            self.gtk_main = GtkMain()

        # Add looping calls
        self.peer_maintain_lc = task.LoopingCall(self.peer_manager.maintain)
        self.peer_maintain_lc.start(30)

        self.task_run_lc = task.LoopingCall(self.task_scheduler.schedule)
        self.task_run_lc.start(30)

        self.report_proc_lc = task.LoopingCall(self.report_uploader.process)
        self.report_proc_lc.start(30)

    def _init_components(self):
        from umit.icm.agent.core.PeerInfo import PeerInfo
        self.peer_info = PeerInfo()

        from umit.icm.agent.core.PeerManager import PeerManager
        self.peer_manager = PeerManager()

        from umit.icm.agent.core.TaskManager import TaskManager
        self.task_manager = TaskManager()

        from umit.icm.agent.core.ReportManager import ReportManager
        self.report_manager = ReportManager()

        from umit.icm.agent.core.ReportUploader import ReportUploader
        self.report_uploader = ReportUploader(self.report_manager)

        from umit.icm.agent.core.TaskScheduler import TaskScheduler
        self.task_scheduler = TaskScheduler(self.task_manager,
                                            self.report_manager)

        from umit.icm.agent.rpc.aggregator import AggregatorAPI
        self.aggregator = AggregatorAPI()

        from umit.icm.agent.core.Statistics import Statistics
        self.statistics = Statistics()

    def _load_from_db(self):
        self.peer_info.load_from_db()
        self.peer_manager.load_from_db()
        # restore unsent reports
        self.report_manager.load_unsent_reports()

    def start(self):
        """
        The Main function
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)
        open(os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running'), 'w')\
            .close()

        self._initialize()

        reactor.addSystemEventTrigger('before', 'shutdown', self.quit)
        reactor.run()

    def quit(self):
        g_logger.info("ICM Agent quit.")

        if hasattr(self, 'peer_info'):
            self.peer_info.save_to_db()

        if hasattr(self, 'peer_manager'):
            self.peer_manager.save_to_db()

        os.remove(os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'running'))


theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
