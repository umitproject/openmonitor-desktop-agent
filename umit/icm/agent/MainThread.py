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

import gobject
import os
import threading
import time

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.gui.LoginDialog import LoginDialog
#from umit.icm.agent.gui.RegistrationDialog import RegistrationDialog
from umit.icm.agent.rpc.aggregator import AggregatorAPI
from umit.icm.agent.utils.DBKVPHelper import DBKVPHelper
from umit.icm.agent.BasePaths import *

########################################################################
class MainThread(threading.Thread):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name='MainThread'):
        """Constructor"""
        threading.Thread.__init__(self, name=name)
        self._stop_flag = False
        
    def run(self):
        if theApp.db_engine.get_config('login_saved'):
            ret = theApp.aggregator.authenticate()
            if ret == RET_SUCCESS:
                theApp.aggregator.available = True
                theApp.login = True
                time.sleep(1)
                gobject.idle_add(theApp.gtk_main.set_login_status, True)
            elif ret == RET_FAILURE:
                theApp.aggregator.available = True
                theApp.login = False
            else:
                theApp.aggregator.available = False
                theApp.login = False
        
        #time.sleep(5)
        #gtk.threads_enter()
        #theApp.gtk_main.set_login_status(True)
        #gtk.threads_leave()                
                
        #if not theApp.login:
            #from umit.icm.agent.gui.LoginDialog import LoginDialog
            #login_dlg = LoginDialog()
            #login_dlg.show_all()
            
        # Connect to the Aggregator and Authenticate
       
        while not self._stop_flag:  # run until the stop method is called
            time.sleep(1)
        
        g_logger.info("Main thread exited.")


    def stop(self):
        g_logger.debug("Stopping main thread...")
        self._stop_flag = True
    
    