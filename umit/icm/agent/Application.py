#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com> 
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
import libcagepeers
import threading
import gtk
import re

from twisted.internet import reactor
from twisted.internet import task

from umit.icm.agent.logger import g_logger
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from umit.icm.agent.Version import VERSION

from umit.icm.agent.I18N import _

# Script found at http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
import imp
frozen = (hasattr(sys, "frozen") or # new py2exe
          hasattr(sys, "importers") # old py2exe
          or imp.is_frozen("__main__")) # tools/freeze
del(imp)

def main_is_frozen():
    return frozen

class Application(object):
    def __init__(self):
        self.cage_instance = libcagepeers
        self.peer_added = False
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
        self.is_auto_login = True        
        self.is_successful_login = False #fix the login failure, save DB problem

    def _load_from_db(self):

        self.peer_manager.load_from_db()
        # restore unsent reports
        self.report_manager.load_unsent_reports()

    def init_after_running(self, port=None, username=None, password=None, server_enabled=True):
        # Create agent service(need to add the port confilct)
        
        if server_enabled:
            self.listen_port = port if port is not None else g_config.getint('network', 'listen_port')
            try:
                from umit.icm.agent.rpc.AgentService import AgentFactory
                self.factory = AgentFactory()
                g_logger.info("Listening on port %d.", self.listen_port)
                reactor.listenTCP(self.listen_port, self.factory)
            except Exception,info:
                #There can add more information
                
                from higwidgets.higwindows import HIGAlertDialog
                print 'Exception : %s'%(info)
                if(re.findall("[Errno 98]",str(info))):
                    print "Port ", self.listen_port," is already in use. Iterating to next available port.";
                    self.listen_port = self.listen_port+1
                    print "Agent is now binding to %d" % self.listen_port
                    self.init_after_running(self.listen_port, username, password, server_enabled)
                    return
                # alter = HIGAlertDialog(primary_text = _("The Listen Port has been used by other applications"),\
                #                        secondary_text = _("Please check the Port"))
                # alter.show_all()
                # result = alter.run()
                
                # #cannot write return, if so the program cannot quit, and run in background              
                # if it is some other exception other than address conflict, then terminate
                else:
                    self.terminate()

        # Create mobile agent service
        from umit.icm.agent.rpc.mobile import MobileAgentService
        self.ma_service = MobileAgentService()

        if self.use_gui:
            # Init GUI
            from umit.icm.agent.gui.GtkMain import GtkMain
            self.gtk_main = GtkMain()
        
        self.is_auto_login = g_config.getboolean('application', 'auto_login')
           
        if  self.is_auto_login:
            #login with saved username or password, not credentials
            self.peer_info.load_from_db()
            self.login(self.peer_info.Username,self.peer_info.Password, True)
        else:
            self.gtk_main.show_login()
            g_logger.info("Auto-login is disabled. You need to manually login.")
            

    def check_software_auto(self):
        """
        check software: according the time and other configurations
        """
        if g_config.getboolean('update', 'update_detect'):
            from umit.icm.agent.gui.SoftwareUpdate import auto_check_update
            #Here can set some update attributes
            defer_ = auto_check_update()
            defer_.addErrback(self._handle_errback)
            return defer_
        
    def register_agent(self, username, password):
        defer_ = self.aggregator.register(username, password)
        # Logging for verifying flow
        g_logger.info("ENTER : register_agent since peer_info does not have username: Checking login flow")
        g_logger.info("username : %s" % username)
        g_logger.info("password : %s" % password)
        self.peer_info.Username = username
        self.peer_info.Password = password
        defer_.addCallback(self._handle_register)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_register(self, result):
        if result:
            self.peer_info.ID = result['id']
            self.peer_info.CipheredPublicKeyHash = result['hash']
            self.peer_info.is_registered = True
            self.peer_info.save_to_db()
            g_logger.debug("Register to Aggregator: %s" % result['id'])
            
        return result

    def _handle_errback(self, failure):
        failure.printTraceback()
        g_logger.error(">>> Failure from Application: %s" % failure)

    def login(self, username, password, save_login=False, login_only=False):
        if self.use_gui:
            self.gtk_main.set_to_logging_in()

        if self.is_auto_login == True:
            #auto-login, select the credentials username and password from DB
            return self._login_after_register_callback(None, username,
                                                   password, save_login,
                                                   login_only)
        else:
            #manually login, we should check whether the username and password exists in database
            #If *NOT*, we should register the username and password to aggregator
            #IF *YES*, we will use credentials in DB
            if self.check_username(username,password):
                return self._login_after_register_callback(None, username,
                                                   password, save_login,
                                                   login_only)                
            else:
                #self.peer_info.clear_db()
                deferred = self.register_agent(username, password)
                deferred.addCallback(self._login_after_register_callback,
                                 username, password, save_login, login_only)
                deferred.addErrback(self._handle_errback)
                return deferred
        
    def check_username(self,username="",password=""):
        """
        check username and password in DB, the information is got from Login-Window
        """
        rs = g_db_helper.select("select * from  peer_info where username='%s' and \
                                password='%s'"%(username,password))
        if not rs:
            g_logger.info("No matching peer info in db.\
                           icm-agent will register the username or password")
            return False
        else:
            g_logger.info("Match the username and password, \
                           we will change the default credentials")
            g_logger.debug(rs[0])
            self.peer_info.ID =  rs[0][0]
            self.peer_info.Username = rs[0][1]
            self.peer_info.Password = rs[0][2]
            self.peer_info.Email = rs[0][3]
            self.peer_info.CipheredPublicKeyHash = rs[0][4]
            self.peer_info.Type = rs[0][5]
            self.peer_info.is_registered = True   
            return True                     

    def _login_after_register_callback(self, message, username,
                                       password, save_login, login_only):
        defer_ = self.aggregator.login(username, password)
        defer_.addCallback(self._handle_login, username, password,
                           save_login, login_only)

        return defer_

    def _handle_login(self, result, username, password, save_login,
                      login_only=False):
        #login successfully
        if result:
            self.peer_info.Username = username if username !="" and username != None else self.peer_info.Username
            self.peer_info.Password = password if password !="" and password != None else self.peer_info.Password
            print self.peer_info.Username, self.peer_info.Password 
            self.peer_info.is_logged_in = True
            self.aggregator.getlocation()
            self.peer_info.save_to_db()
            g_logger.debug("Login Successfully :%s@%s" % (username,password))
            if save_login:
                g_config.set('application', 'auto_login', True)
            else:
                g_config.set('application', 'auto_login', False)

            if self.use_gui:
                self.gtk_main.set_login_status(True)

            if login_only:
                return result
            
            #Load peers and reports from DB
            self._load_from_db()
            
            #check the new software(should appear after login successfully)
            self.check_software_auto()
            
            #mark login-successful
            self.is_successful_login = True


            #After successful Login
            # 1. Get super peer list from the aggregator
            # 2. Bootstrap libcage using the first super peer.
            # 3. After successful bootstrapping, add the current peer into the aggregator (Peer / Super peer flag in the request message). Geo location service should be up for this to work in production.
            # 4. Sync "peers" table with libcage instance.

            g_logger.info("GETTING BOOTSTRAP PEERS FROM AGGREGATOR")
            if not re.match("^[A-Za-z]+$",self.peer_info.country_code):
                self.peer_info.country_code='UN';
            self.aggregator.get_bootstrapping_peers(self.peer_info.country_code)


        return result

    def bootstrap(self):
        g_logger.info("VALUE OF CAGE INSTANCE IS : %s" % self.cage_instance)
        g_logger.info("GETTING PEER AND SUPER PEER LIST FROM THE AGGREGATOR")

        # Add looping calls
        # Maintain in Peermanager takes care of get_peer_list and get_super_peer_list
        if not hasattr(self, 'peer_maintain_lc'):
            self.peer_maintain_lc = task.LoopingCall(self.peer_manager.maintain)
            self.peer_maintain_lc.start(10)

        if not hasattr(self, 'task_run_lc'):
            self.task_run_lc = task.LoopingCall(self.task_scheduler.schedule)
            self.task_run_lc.start(30)

        if not hasattr(self, 'report_proc_lc'):
            self.report_proc_lc = task.LoopingCall(self.report_uploader.process)
            self.report_proc_lc.start(30)

        #Bootstrap
        # Plug in Libcage code - Get port number from command line
        g_logger.info("List of super peers from the Aggregator : %s" % self.peer_manager.super_peers)
        g_logger.info("List of normal peers from the Aggregator : %s" % self.peer_manager.normal_peers)

        g_logger.info("BOOTSTRAPPING LIBCAGE BASED ON THE LIST OF PEERS AND SUPER PEERS")

        g_logger.info("Info about super peers : ");
        if len(self.peer_manager.super_peers)!=0:
            for superPeer in self.peer_manager.super_peers.values():
                g_logger.info(superPeer.status, " and PeerID is ",superPeer.ID);


        # if len(self.peer_manager.normal_peers==0):

        #self.cage_instance.createCage_firstnode("20000");
        #self.cage_instance.createCage_joinnode("20001","127.0.0.1","20000");
        '''
        else
            libcagepeers.createCage_joinnode()
        '''

        # Add this peer into the peerlist of aggregator
        g_logger.info("ADDING THIS PEER INTO THE AGGREGATOR'S PEERLIST")
        self.peer_manager.add_peer()

    def logout(self):
        defer_ = self.aggregator.logout()
        defer_.addCallback(self._handle_logout)

        return defer_

    def _handle_logout(self, result):
        if self.use_gui:
            self.gtk_main.set_login_status(False)

        g_config.set('application', 'auto_login', False)

        return result

    def start(self, run_reactor=True, managed_mode=False, aggregator=None):
        """
        The Main function
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)

        self._init_components(aggregator)

        

        #self.task_manager.add_test(1, '* * * * *', {'url':'http://icm-dev.appspot.com'}, 3)

        reactor.addSystemEventTrigger('before', 'shutdown', self.on_quit)

        if not managed_mode:
            # This is necessary so the bot can take over and control the agent
            reactor.callWhenRunning(self.init_after_running)

        # TODO IMPORTANT : This must be called only after successful GetPeerlist and successful completion of bootstrapping

        if run_reactor:
            # This is necessary so the bot can take over and control the agent
            reactor.run()

        thread.join();

    def terminate(self):
        print 'quit'
        reactor.callWhenRunning(reactor.stop)

    def on_quit(self):

        if hasattr(self, 'peer_info') and self.is_successful_login:
            g_logger.info("[quit]:save peer_info into DB")
            self.peer_info.save_to_db()

        if hasattr(self, 'peer_manager') and self.is_successful_login:
            g_logger.info("[quit]:save peer_manager into DB")
            self.peer_manager.save_to_db()

        #clear peer id
        m = os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'agent_restart_mark')
        if os.path.exists(m):
            os.remove(m)
        
        self.quitting = True
        
        g_logger.info("ICM Agent quit.")

theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
