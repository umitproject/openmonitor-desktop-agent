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

    def _init_components(self, aggregator):
        from umit.icm.agent.core.PeerInfo import PeerInfo
        self.peer_info = PeerInfo()

        from umit.icm.agent.core.PeerManager import PeerManager
        self.peer_manager = PeerManager()

        from umit.icm.agent.core.EventManager import EventManager
        self.event_manager = EventManager()

        from umit.icm.agent.core.TaskManager import TaskManager
        self.task_manager = TaskManager()

        from umit.icm.agent.core.ReportManager import ReportManager
        self.report_manager = ReportManager()

        from umit.icm.agent.core.ReportUploader import ReportUploader
        self.report_uploader = ReportUploader(self.report_manager)

        from umit.icm.agent.core.TaskScheduler import TaskScheduler
        self.task_scheduler = TaskScheduler(self.task_manager,
                                            self.report_manager)

        from umit.icm.agent.secure.KeyManager import KeyManager
        self.key_manager = KeyManager()

        from umit.icm.agent.core.Statistics import Statistics
        self.statistics = Statistics()

        from umit.icm.agent.rpc.aggregator import AggregatorAPI
        self.aggregator = AggregatorAPI(aggregator)
        
        self.quitting = False

    def _load_from_db(self):
        self.peer_info.load_from_db()
        self.peer_manager.load_from_db()
        # restore unsent reports
        self.report_manager.load_unsent_reports()

    def init_after_running(self, port=None, username=None, password=None, server_enabled=True):
        # Create agent service
        if server_enabled:
            self.listen_port = port if port is not None else g_config.getint('network', 'listen_port')
        
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

        if g_db_helper.get_value('auto_login'):
            # login with saved credentials
            self.login(username if username is not None else self.peer_info.Username,
                       password if password is not None else self.peer_info.Password, True)
        else:
            g_logger.info("Auto-login is disabled. You need to manually login.")

    def register_agent(self, username, password):
        defer_ = self.aggregator.register(username, password)
        defer_.addCallback(self._handle_register)
        
        return defer_

    def _handle_register(self, result):
        if result:
            self.peer_info.ID = result['id']
            self.peer_info.CipheredPublicKeyHash = result['hash']
            self.peer_info.is_registered = True
            self.peer_info.save_to_db()
        
        return result
    
    def _handle_errback(self, failure):
        failure.printTraceback()
        g_logger.error(">>> Failure from Application: %s" % failure)

    def login(self, username, password, save_login=False, login_only=False):
        if self.use_gui:
            self.gtk_main.tray_icon.set_tooltip("Logging in...")
            self.gtk_main.tray_menu.children()[0].set_sensitive(False)
        
        if not theApp.peer_info.is_registered:
            deferred = self.register_agent(username, password)
            deferred.addCallback(self._login_after_register_callback,
                                 username, password, save_login, login_only)
            deferred.addErrback(self._handle_errback)
            
            return deferred
        
        return self._login_after_register_callback(None, username,
                                                   password, save_login,
                                                   login_only)

    def _login_after_register_callback(self, message, username,
                                       password, save_login, login_only):
        defer_ = self.aggregator.login(username, password)
        defer_.addCallback(self._handle_login, username, password,
                           save_login, login_only)
        
        return defer_

    def _handle_login(self, result, username, password, save_login, login_only=False):
        if result:
            self.peer_info.Username = username
            self.peer_info.Password = password
            self.peer_info.is_logged_in = True
            self.peer_info.save_to_db()

            if save_login:
                g_db_helper.set_value('auto_login', True)
            else:
                g_db_helper.set_value('auto_login', False)

            if self.use_gui:
                self.gtk_main.set_login_status(True)
            
            if login_only:
                return result

            # Add looping calls
            if not hasattr(self, 'peer_maintain_lc'):
                self.peer_maintain_lc = task.LoopingCall(self.peer_manager.maintain)
                self.peer_maintain_lc.start(30)

            if not hasattr(self, 'task_run_lc'):
                self.task_run_lc = task.LoopingCall(self.task_scheduler.schedule)
                self.task_run_lc.start(30)

            if not hasattr(self, 'report_proc_lc'):
                self.report_proc_lc = task.LoopingCall(self.report_uploader.process)
                self.report_proc_lc.start(30)
        
        return result

    def logout(self):
        defer_ = self.aggregator.logout()
        defer_.addCallback(self._handle_logout)
        
        return defer_

    def _handle_logout(self, result):
        if self.use_gui:
            self.gtk_main.set_login_status(False)
        
        g_db_helper.set_value('auto_login', False)
        
        return result
    

    def start(self, run_reactor=True, managed_mode=False, aggregator=None):
        """
        The Main function
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)
        self._init_components(aggregator)
        self._load_from_db()

        #self.task_manager.add_test(1, '* * * * *', {'url':'http://icm-dev.appspot.com'}, 3)

        reactor.addSystemEventTrigger('before', 'shutdown', self.on_quit)
        
        if not managed_mode:
            # This is necessary so the bot can take over and control the agent
            reactor.callWhenRunning(self.init_after_running)
        
        if run_reactor:
            # This is necessary so the bot can take over and control the agent
            reactor.run()

    def terminate(self):
        reactor.callWhenRunning(reactor.stop)

    def on_quit(self):
        g_logger.info("ICM Agent quit.")

        if hasattr(self, 'peer_info'):
            self.peer_info.save_to_db()

        if hasattr(self, 'peer_manager'):
            self.peer_manager.save_to_db()

        m = os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'agent_restart_mark')
        if os.path.exists(m):
            os.remove(m)
        
        self.quitting = True


theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
