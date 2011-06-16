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
    execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

import os
import sys
import time

from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()
from twisted.internet import reactor

from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from umit.icm.agent.Version import VERSION

class Application(object):
    def __init__(self):
        self.login = False
        
    def _initialize(self):
        from umit.icm.agent.MainThread import MainThread
        from umit.icm.agent.TestThread import TestThread
        from umit.icm.agent.ReportThread import ReportThread
        self.main_thread = MainThread()
        self.test_thread = TestThread()
        self.report_thread = ReportThread()        
        
        from umit.icm.agent.ICMConfig import ICMConfig
        self.config = ICMConfig(
            os.path.join(CONFIG_DIR, 'agent_config.txt'))
        
        from umit.icm.agent.DBEngine import DBEngine
        self.db_engine = DBEngine()
        self.db_engine.start()
        
        from umit.icm.agent.core.TestManager import TestManager
        self.test_manager = TestManager()
        
        from umit.icm.agent.core.ReportManager import ReportManager
        self.report_manager = ReportManager()
        
        from umit.icm.agent.core.PeerManager import PeerManager
        self.peer_manager = PeerManager()
        
        from umit.icm.agent.core.PeerInfo import PeerInfo
        self.peer_info = PeerInfo()
        
        from umit.icm.agent.rpc.aggregator import AggregatorAPI
        self.aggregator = AggregatorAPI(
            self.db_engine.get_config('aggregator_url'))
   
    def start(self):
        """
        The Main function 
        """
        # Initialize members
        self._initialize()
        
        g_logger.info("Starting ICM agent. Version: %s", VERSION)
        
        # Start backend service
        port = self.config.getint('network', 'listen_port')
        from umit.icm.agent.rpc.AgentService import AgentFactory
        reactor.listenTCP(port, AgentFactory())
        
        # Init GUI
        from umit.icm.agent.gui.GtkMain import GtkMain
        self.gtk_main = GtkMain()
        
        self.main_thread.start()
        self.test_thread.start()
        self.report_thread.start()

        reactor.run()
    
    def quit(self):
        g_logger.info("ICM Agent quit.")
        
        if self.main_thread.is_alive():
            self.main_thread.stop()
            
        if self.test_thread.is_alive():
            self.test_thread.stop()
            
        if self.report_thread.is_alive():
            self.report_thread.stop()

        if reactor.running:            
            reactor.stop()
            self.peer_info.save()
        
        while self.main_thread.is_alive() or \
              self.test_thread.is_alive() or \
              self.report_thread.is_alive():
            time.sleep(0.1)
        self.db_engine.stop()
                    
theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
    