#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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

import socket

from twisted.internet import reactor
from twisted.internet import task

from umit.icm.agent.logger import g_logger
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from umit.icm.agent.Version import VERSION
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

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

        from umit.icm.agent.core.TaskAssignFetch import TaskAssignFetch
        self.task_assign = TaskAssignFetch(self.task_manager)
        
        from umit.icm.agent.core.TestSetsFetcher import TestSetsFetcher
        self.test_sets = TestSetsFetcher(self.task_manager,
                                         self.report_manager)
        
        from umit.icm.agent.secure.KeyManager import KeyManager
        self.key_manager = KeyManager()

        from umit.icm.agent.core.Statistics import Statistics
        self.statistics = Statistics()

        from umit.icm.agent.rpc.aggregator import AggregatorAPI
        self.aggregator = AggregatorAPI(aggregator)

        from umit.icm.agent.super.SuperBehaviourByManual import SuperBehaviourByManual
        self.speer_by_manual = SuperBehaviourByManual(self)

        self.quitting = False
        self.is_auto_login = False        
        self.is_successful_login = False #fix the login failure, save DB problem
                       
    def _load_from_db(self):
        """
        """
        self.peer_manager.load_from_db()
        # restore unsent reports
        self.report_manager.load_unsent_reports()
        # desktop agent stats saving
        self.statistics.load_from_db()

    def init_after_running(self, port=None, username=None, password=None,
                           server_enabled=True, skip_server_check=False):
        """
        """
        #####################################################
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

                self.quit_window_in_wrong(primary_text = _("The Listen Port has been used by other applications"), \
                                          secondary_text = _("Please check the Port") )
                
        #############################
        # Create mobile agent service
        from umit.icm.agent.rpc.mobile import MobileAgentService
        self.ma_service = MobileAgentService()

        if self.use_gui:
            import gtk
            # Init GUI
            from umit.icm.agent.gui.GtkMain import GtkMain
            self.gtk_main = GtkMain()
        
        self.is_auto_login = g_config.getboolean('application', 'auto_login_swittch')
        
        ###################################################################
        #debug switch: It can show the gtkWindow without any authentication 
        if g_config.getboolean('debug','debug_switch') and self.use_gui:
            self.login_simulate()
        
        ######################################
        #check aggregator can be reached first
        if not skip_server_check:
            defer_ = self.aggregator.check_aggregator_website()
            defer_.addCallback(self.check_aggregator_success)
            defer_.addErrback(self.check_aggregator_failed)
         
    
    def check_aggregator_success(self,response):
        """
        """
        if response == True:
            self.login_window_show()
        else:
            self.speer_by_manual.peer_communication()
        
    def login_window_show(self):       
        """
        """
        if self.is_auto_login and self.use_gui :
            #######################################################
            #login with saved username or password, not credentials
            self.peer_info.load_from_db()
            
            ########################################
            #Add more condition to check login legal 
            self.login(self.peer_info.Username,self.peer_info.Password, True)
            
        else:
            if self.use_gui:
                self.gtk_main.show_login()
            else:
                self.login_without_gui()
            g_logger.info("Auto-login is disabled. You need to manually login.")        
    
    def check_aggregator_failed(self,message):
        """
        """
        self.aggregator.available = False
        
        self.speer_by_manual.peer_communication()
    
    
    def login_without_gui(self):
        """
        Users login without username or password
        """
        username = False
        password = False

        if g_config.has_section("credentials"):
            username = g_config.get("credentials", "user")
            password = g_config.get("credentials", "password")
        
        if not username:
            username  = raw_input("User Name:")

        if not password:
            password = raw_input("Password:")

        self.login(username, password, save_login=True) 
        
    def check_software_auto(self):
        """
        check software: according the time and other configurations
        """
        from umit.icm.agent.core.Updater import auto_check_update
        ##############################
        #Software update automatically
        if g_config.getboolean('application','auto_update'):
            defer_ = auto_check_update(auto_upgrade=True)
            defer_.addErrback(self._handle_errback)
        else:
            ############################
            #Detect update automatically
            if g_config.getboolean('update', 'update_detect'):
                #Here can set some update attributes
                defer_ = auto_check_update(auto_upgrade=False)
                defer_.addErrback(self._handle_errback)
                    
    def register_agent(self, username, password):
        """
        """
        defer_ = self.aggregator.register(username, password)
        defer_.addCallback(self._handle_register)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_register(self, result):
        if result:
            self.peer_info.ID = result['id']
            self.peer_info.CipheredPublicKeyHash = result['hash']
            self.peer_info.is_registered = True
            g_logger.debug("Register to Aggregator: %s" % result['id'])
            
        return result

    def _handle_errback(self, failure):
        """
        """
        failure.printTraceback()
        g_logger.error(">>> Failure from Application: %s" % failure)

    def login(self, username, password, save_login=False, login_only=False):
        """
        """
        if self.use_gui:
            self.gtk_main.set_to_logging_in()

        if self.is_auto_login and self.use_gui and self.check_username(username,password):
            #auto-login, select the credentials username and password from DB
            return self._login_after_register_callback(None, username,
                                                   password, save_login,
                                                   login_only)
        else:
            #manually login, we should check whether the username and password exists in database
            #If *NOT*, we should register the username and password to aggregator
            #IF *YES*, we will use credentials in DB
            g_config.set('application', 'auto_login_swittch', False)

            if self.check_username(username,password):
                return self._login_after_register_callback(None, username,
                                                   password, save_login,
                                                   login_only)                
            else:
                self.peer_info.clear_db()
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
        """
        """
        defer_ = self.aggregator.login(username, password)
        defer_.addCallback(self._handle_login, username, password,
                           save_login, login_only)
        defer_.addErrback(self._handle_login_errback)
        
        return defer_

    def _handle_login_errback(self,failure):
        """
        """
        print "------------------login failed!-------------------"
        failure.printTraceback()
        g_logger.error(">>> Failure from Application: %s" % failure)        
             
    def _handle_login(self, result, username, password, save_login,login_only=False):
        """
        """
        #login successfully
        if result:
            self.peer_info.Username = username if username !="" and username != None else self.peer_info.Username
            self.peer_info.Password = password if password !="" and password != None else self.peer_info.Password
            #print self.peer_info.Username, self.peer_info.Password 
            self.peer_info.is_logged_in = True
            #self.peer_info.clear_db()
            self.peer_info.save_to_db()
            g_logger.debug("Login Successfully :%s@%s" % (username,password))
            if save_login:
                g_config.set('application', 'auto_login_swittch', True)
            else:
                g_config.set('application', 'auto_login_swittch', False)

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
            
            #Task Looping manager
            self.task_loop_manager()
            
        return result
    
    def login_simulate(self):
        """
        Only test GTK features
        """
        #GTK show
        if self.use_gui == True:
            self.gtk_main.set_login_status(True)
        #Basic Information
        self.peer_info.load_from_db()
        self._load_from_db()
        #mark login-successful
        self.is_successful_login = True 
        #TASK LOOP
        self.task_loop_manager()       
    
    def task_loop_manager(self):
        """"""
        # Add looping calls
        if not hasattr(self, 'peer_maintain_lc'):
            self.peer_maintain_lc = task.LoopingCall(self.peer_manager.maintain)
            self.peer_maintain_lc.start(7200)
        
        if not hasattr(self, 'task_run_lc'):
            g_logger.info("Starting task scheduler looping ")
            self.task_run_lc = task.LoopingCall(self.task_scheduler.schedule)
            
            task_scheduler_text = g_config.get("Timer","task_scheduler_timer")
            if task_scheduler_text != "":
                indival = float(task_scheduler_text)
            else:
                indival = 30
            
            self.task_run_lc.start(indival)
        
        if not hasattr(self, 'report_proc_lc'):
            g_logger.info("Starting report upload looping ")
            self.report_proc_lc = task.LoopingCall(self.report_uploader.process)
            
            report_uploade_text = g_config.get("Timer","send_report_timer")
            if report_uploade_text != "":
                indival = float(report_uploade_text)
            else:
                indival = 30                
            
            self.report_proc_lc.start(indival)
            
        if not hasattr(self,'task_assign_lc'):
            g_logger.info("Starting get assigned task from Aggregator")
            self.task_assgin_lc = task.LoopingCall(self.task_assign.fetch_task)
            
            task_assign_text = g_config.get("Timer","task_assign_timer")
            if task_assign_text != "":
                indival = float(task_assign_text)
            else:
                indival = 30                
            
            self.task_assgin_lc.start(indival)
        
        if not hasattr(self,'test_sets_fetch_lc'):
            g_logger.info("Starting get test sets from Aggregator")
            self.test_sets_fetch_lc = task.LoopingCall(self.test_sets.fetch_tests)
            
            test_fetch_text = g_config.get("Timer","test_fetch_timer")
            if test_fetch_text != "":
                indival = float(test_fetch_text)
            else:
                indival = 30                
            
            self.test_sets_fetch_lc.start(indival)             

    def logout(self):
        defer_ = self.aggregator.logout()
        defer_.addCallback(self._handle_logout)

        return defer_

    def _handle_logout(self, result):
        if self.use_gui:
            self.gtk_main.set_login_status(False)

        g_config.set('application', 'auto_login_swittch', False)

        return result

    def start(self, run_reactor=True, managed_mode=False, aggregator=None):
        """
        The Main function
        """
        g_logger.info("Starting ICM agent. Version: %s", VERSION)
        self._init_components(aggregator)

        reactor.addSystemEventTrigger('before', 'shutdown', self.on_quit)

        if not managed_mode:
            # This is necessary so the bot can take over and control the agent
            reactor.callWhenRunning(self.init_after_running)

        if run_reactor:
            # This is necessary so the bot can take over and control the agent
            reactor.run()

    def quit_window_in_wrong(self,primary_text = "",secondary_text = ""):
        """
        """
        #There can add more information
        from higwidgets.higwindows import HIGAlertDialog
        #print 'The exception is %s'%(info)
        alter = HIGAlertDialog(primary_text = primary_text,\
                               secondary_text = secondary_text)
        alter.show_all()
        result = alter.run()
        
        #cannot write return, if so the program cannot quit, and run in background              
        self.terminate()
        
    def terminate(self):
        #print 'quit'
        reactor.callWhenRunning(reactor.stop)

    def on_quit(self):

        if hasattr(self, 'peer_info') and self.is_successful_login:
            g_logger.info("[quit]:save peer_info into DB")
            self.peer_info.save_to_db()

        if hasattr(self, 'peer_manager') and self.is_successful_login:
            g_logger.info("[quit]:save peer_manager into DB")
            self.peer_manager.save_to_db()
            
        if hasattr(self, 'statistics') and  self.is_successful_login:
            g_logger.info("[quit]:save statistics into DB") 
            self.statistics.save_to_db()           
        
        if hasattr(self,'test_sets') and self.is_successful_login \
            and os.path.exists(CONFIG_PATH):
            #store test_version id
            self.test_sets.set_test_version(self.test_sets.current_test_version)
 
        m = os.path.join(ROOT_DIR, 'umit', 'icm', 'agent', 'agent_restart_mark')
        if os.path.exists(m):
            os.remove(m)
        
        self.quitting = True
        
        g_logger.info("ICM Agent quit.")


theApp = Application()


if __name__ == "__main__":
    #theApp.start()
    pass
