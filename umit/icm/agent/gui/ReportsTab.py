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

#from Dashboard import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED
from DashboardListBase import  *

class ReportsTab(DashboardListBase):
    """
    ReportsTab: show the statistics about the report numbers
    """
    def __init__(self):
        """
        """
        DashboardListBase.__init__(self)
        
    def show(self,show_type=None):
        """
        Reports: It can show the report statistics
        """
        self.detail_liststore.clear()
        
        self.detail_liststore.append(['Reports Total', None,
                                      theApp.statistics.reports_total])
        self.detail_liststore.append(['Reports In Queue', None,
                                      theApp.statistics.reports_in_queue])
        self.detail_liststore.append(['Reports Generated', None,
                                      theApp.statistics.reports_generated])        
        self.detail_liststore.append(['Reports Sent', None,
                                      theApp.statistics.reports_sent])
        self.detail_liststore.append(['Reports Sent To Aggregator', None,
                                      theApp.statistics.reports_sent_to_aggregator])
        self.detail_liststore.append(['Reports Sent To Super Agent', None,
                                      theApp.statistics.reports_sent_to_super_agent])
        self.detail_liststore.append(['Reports Sent To Normal Agent', None,
                                      theApp.statistics.reports_sent_to_normal_agent])
        self.detail_liststore.append(['Reports Sent To Mobile Agent', None,
                                      theApp.statistics.reports_sent_to_mobile_agent]) 
        self.detail_liststore.append(['Reports Received', None,
                                      theApp.statistics.reports_received])
        self.detail_liststore.append(['Reports Received From Aggregator', None,
                                      theApp.statistics.reports_received_from_aggregator])
        self.detail_liststore.append(['Reports Received From Super Agent', None,
                                      theApp.statistics.reports_received_from_super_agent])
        self.detail_liststore.append(['Reports Received From Normal Agent', None,
                                      theApp.statistics.reports_received_from_normal_agent])
        self.detail_liststore.append(['Reports Received From Mobile Agent', None,
                                      theApp.statistics.reports_received_from_mobile_agent])         
        
    
class ReportDetailsTab(gtk.VBox):
    """
    SentDetailsTab : Show the sent end unsent reports from database
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)

        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()    
    
    def __create_widgets(self):
        """
        """
        pass
    
    def __pack_widgets(self):   
        """
        """
        pass
    
    def __connected_widgets(self):
        """
        """
        pass   
    
class ReceiveDetailsTab(gtk.VBox): 
    """
    ReceiveDetailsTab: Show the received reports from other peers
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)

        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()   
    
    def __create_widgets(self):
        """
        """
        pass
    
    def __pack_widgets(self):   
        """
        """
        pass
    
    def __connected_widgets(self):
        """
        """
        pass          
    
    
    
    
    
    
    
    
    
    
        
