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

import os
import threading
import time

from twisted.internet import reactor

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
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
        g_logger.info("Main thread started.")
        #if theApp.db_engine.get_config('login_saved'):
            #ret = theApp.aggregator.authenticate()
            #if ret == RET_SUCCESS:
                #theApp.aggregator.available = True
                #theApp.login = True
                #gobject.idle_add(theApp.gtk_main.set_login_status, True)
            #elif ret == RET_FAILURE:
                #theApp.aggregator.available = True
                #theApp.login = False
            #else:
                #theApp.aggregator.available = False
                #theApp.login = False

        #time.sleep(3)
        #from twisted.internet import reactor
        #reactor.callFromThread(theApp.gtk_main.set_login_status, True)

        #ret = theApp.aggregator.authenticate()
        #if ret == 'Succeeded':
            #theApp.auth = True
            #ret = theApp.aggregator.report_peer_info()
            #if ret == 'Succeeded':
                #g_logger.info("Reported peer info to aggregator when started.")

        max_speer_num = g_config.getint('network', 'max_speer_num')
        max_peer_num = g_config.getint('network', 'max_peer_num')
        peer_manager = theApp.peer_manager

        while not self._stop_flag:  # run until the stop method is called
            try:
                if peer_manager.super_peer_num < max_speer_num:
                    required_num = max_speer_num - peer_manager.super_peer_num
                    if theApp.aggregator.available:
                        d = theApp.aggregator.get_super_peer_list(required_num)
                        #for each in speer_list:
                            #peer_manager.add_super_peer(each)
                    else:
                        for peer_id in peer_manager.super_peers:
                            if peer_id in peer_manager.sessions:
                                peer_manager.sessions[peer_id].\
                                            get_super_peer_list(required_num)

                if peer_manager.normal_peer_num < max_peer_num:
                    required_num = max_peer_num - peer_manager.normal_peer_num
                    if theApp.aggregator.available:
                        d = theApp.aggregator.get_peer_list(required_num)
                        #for each in peer_list:
                            #peer_manager.add_normal_peer(each)
                    else:
                        for peer_id in peer_manager.super_peers:
                            if peer_id in peer_manager.sessions:
                                peer_manager.sessions[peer_id].\
                                            get_peer_list(required_num)

                peer_manager.connect_all()
            except BaseException, e:
                print(e)
                break
            time.sleep(5)



        #if not theApp.login:
            #from umit.icm.agent.gui.LoginDialog import LoginDialog
            #login_dlg = LoginDialog()
            #login_dlg.show_all()

        # Connect to the Aggregator and Authenticate

        g_logger.info("Main thread exited.")


    def stop(self):
        g_logger.debug("Stopping main thread...")
        self._stop_flag = True
