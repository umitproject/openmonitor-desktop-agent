#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Tianwei Liu <liutainweidlut@gmail.com> 
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

import pygtk
pygtk.require('2.0')
import gtk, gobject


from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp

#from Dashboard import CONNECTION,CONN_AGG,CONN_SUPER,CONN_NORMAL,CONN_MOBILE
from DashboardListBase import  *

class ConnectionsTab(DashboardListBase):
    """
    ConnectionsTab: show the statistics about Connections
    """
    def __init__(self):
        """
        """
        DashboardListBase.__init__(self)
    
    def show(self,show_type=None):
        """
        """
        self.detail_liststore.clear()
        
        self.detail_liststore.append(['Aggregator Status', None,
                                      theApp.aggregator.available])
        self.detail_liststore.append(['Super Agent Connected', None,
                                      theApp.statistics.super_agents_num])
        self.detail_liststore.append(['Normal Agent Connected', None,
                                      theApp.statistics.normal_agents_num])
        self.detail_liststore.append(['Mobile Agent Connected', None,
                                      theApp.statistics.mobile_agents_num])          
    
    
class ConnectionsIndividualTab(DashboardListBase):
    """
    ConnectionsIndividualTab : Show the different kinds of connections
    """
    def __init__(self):
        """
        """
        DashboardListBase.__init__(self)
        
  
    def show(self,show_type=None):
        """
        """
        self.detail_liststore.clear()
        
        if conn_type == CONN_AGG:
            self.detail_liststore.append(['Aggregator Status', None,
                                          theApp.aggregator.available])
            self.detail_liststore.append(['Aggregator Failure Times', None,
                                          theApp.statistics.aggregator_fail_num])
        elif conn_type == CONN_SUPER:
            self.detail_liststore.append(['Super Agent Connected', None,
                                          theApp.statistics.super_agents_num])
            self.detail_liststore.append(['Super Agent Failure Times', None,
                                          theApp.statistics.super_agents_fail_num])
        elif conn_type == CONN_NORMAL:
            self.detail_liststore.append(['Normal Agent Connected', None,
                                          theApp.statistics.normal_agents_num])
            self.detail_liststore.append(['Normal Agent Failure Times', None,
                                          theApp.statistics.normal_agents_fail_num])
        elif conn_type == CONN_MOBILE:
            self.detail_liststore.append(['Mobile Agent Connected', None,
                                          theApp.statistics.mobile_agents_num])
            self.detail_liststore.append(['Mobile Agent Failure Times', None,
                                          theApp.statistics.mobile_agents_fail_num])        
         
        