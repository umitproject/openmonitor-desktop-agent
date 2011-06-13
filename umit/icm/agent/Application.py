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

from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import g_logger, g_db_helper
from umit.icm.agent.Version import VERSION

class Application(object):
    from twisted.internet import gtk2reactor # for gtk-2.0
    gtk2reactor.install()
    from twisted.internet import reactor
    
    def __init__(self):
        from umit.icm.agent.ICMConfig import ICMConfig
        from umit.icm.agent.core.TestManager import TestManager
        from umit.icm.agent.core.ReportManager import ReportManager
        from umit.icm.agent.core.PeerManager import PeerManager
        from umit.icm.agent.core.PeerInfo import PeerInfo
        from umit.icm.agent.utils.DBKVPHelper import DBKVPHelper
        
        self.config = ICMConfig(os.path.join(CONFIG_DIR, 'agent_config.txt'))
        self.test_manager = TestManager()
        self.report_manager = ReportManager()
        self.peer_manager = PeerManager()
        self.peer_info = PeerInfo()
        self.db_config = DBKVPHelper(os.path.join(DB_DIR, 'storage.db3'),
                                     'config')
    
    def start(self):
        """
        The Main function 
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)
        
        from umit.icm.agent.MainThread import MainThread
        from umit.icm.agent.TestThread import TestThread
        from umit.icm.agent.ReportThread import ReportThread
        from umit.icm.agent.rpc.AgentService import AgentFactory
        from umit.icm.agent.gui.GtkMain import GtkMain
        
        # Start backend service
        port = self.config.getint('network', 'listen_port')
        self.reactor.listenTCP(port, AgentFactory())

        # Start Main Thread
        self.main_thread = MainThread()
        self.main_thread.start()
        
        # Start Test Thread
        self.test_thread = TestThread()
        self.test_thread.start()
        
        # Start Report Thread
        self.report_thread = ReportThread()
        self.report_thread.start()
        
        # Create GUI
        gtk_main = GtkMain()
        self.reactor.run()
        #test = WebsiteTest('https://www.alipay.com')
        #test.prepare()
        #test.execute()
        
        self.test_thread.stop()
        self.report_thread.stop()
        self.test_thread.join()
        g_logger.info("Test thread exited.")
        self.report_thread.join()
        g_logger.info("Report thread exited.")
    
    def quit(self):
        g_logger.info("ICM Agent quit.")
        self.peer_info.save()
        self.reactor.stop()
            
theApp = Application()

if __name__ == "__main__":
    #theApp.start()
    pass
    