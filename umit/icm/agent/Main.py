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
import sys

from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()

from twisted.internet import reactor

from umit.icm.agent.Config import config
from umit.icm.agent.Logging import log
from umit.icm.agent.gui.GtkMain import GtkMain
from umit.icm.agent.rpc.AgentService import AgentFactory
from umit.icm.agent.Version import VERSION
from umit.icm.agent.core.TestThread import TestThread
from umit.icm.agent.core.ReportThread import ReportThread

class Main(object):
    def start(self):
        """
        The Main function 
        """
        log.info("Starting ICM agent. Version: %s", VERSION)
        
        # Start backend service
        port = config.getint('network', 'listen_port')
        reactor.listenTCP(port, AgentFactory())
        
        # Start Test Thread
        test_thread = TestThread()
        test_thread.start()
        
        # Start Report Thread
        report_thread = ReportThread()
        report_thread.start()
        
        # Create GUI
        gtk_main = GtkMain()
        reactor.run()
        #test = WebsiteTest('https://www.alipay.com')
        #test.prepare()
        #test.execute()
        
        test_thread.stop()
        report_thread.stop()
    
    def quit(self):
        reactor.stop()

if __name__ == "__main__":
    main = Main()
    main.start()
    