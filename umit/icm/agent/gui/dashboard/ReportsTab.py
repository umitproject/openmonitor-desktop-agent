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
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.logger import g_logger

#from Dashboard import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED
from umit.icm.agent.gui.dashboard.DashboardListBase import  *

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
        
        self.__create_record()
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()    
    
    def __create_record(self):
        """
        """
        self.report_list_dict = {}
        self.report_details_dict = {
                                     "report_id":"",
                                     "test_id":"",
                                     "time_gen":"",
                                     "content":"",
                                     "source_id":"",
                                     "source_ip":"",
                                     "status":""
                                     }       
    
    def __create_widgets(self):
        """
        """
        
        self.column_names = ['ID','TestID','Time','Content',
                             'SourceID','SourceIP','Status']
        
        self.store = gtk.ListStore(str,str,str,str,str,str,str)
        self.treeview = gtk.TreeView()
       
        self.treeview.set_rules_hint(True)
        self.treeview.set_sensitive(False)
        
        self.__create_columns()
    
    def __pack_widgets(self):   
        """
        """
        self.add(self.treeview)
    
    def __connected_widgets(self):
        """
        """
        pass   
    
    def __create_columns(self):
        """
        """
        for i in range(0,len(self.column_names)):
            rendererText = gtk.CellRendererText()
            column = gtk.TreeViewColumn(self.column_names[i],rendererText,text = i) #text attributes MUST!
            column.set_sort_column_id(i)
            self.treeview.append_column(column)  
            
    def show_details(self,report_type):
        """
        Report Details: Sent and unsent
        """
        self.report_list_dict = {}
        cnt =0
        
        from umit.icm.agent.gui.dashboard.DashboardListBase import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED        
        ###########################
        #Get Report Details From DB
        rs = g_db_helper.get_report_sets(report_type=report_type)
        
        if rs == None:
            g_logger.info("Cannot load any reports from DB.")
            self.treeview.set_sensitive(True)
            self.store.clear()
            self.treeview.set_model(self.store) #It must be after the store update
            return 
        
        for record in rs:
            self.report_list_dict[cnt] = {}
            self.report_list_dict[cnt]["report_id"] = record[0]
            self.report_list_dict[cnt]["test_id"]   = record[1]
            self.report_list_dict[cnt]["time_gen"]  = record[2]
            self.report_list_dict[cnt]["content"]   = record[3]
            self.report_list_dict[cnt]["source_id"] = record[4]
            self.report_list_dict[cnt]["source_ip"] = record[5]
            self.report_list_dict[cnt]["status"]    = record[6] 
            
            cnt += 1
        
        g_logger.info("Loaded %d reports from DB." % len(rs)) 
        
        #####################
        #Output in the Window
        self.treeview.set_sensitive(True) 
        self.store.clear()
        
        for line in self.report_list_dict.keys():
                self.store.append(
                                  [self.report_list_dict[line]["report_id"],
                                   self.report_list_dict[line]["test_id"],
                                   self.report_list_dict[line]["time_gen"],
                                   self.report_list_dict[line]["content"],
                                   self.report_list_dict[line]["source_id"],
                                   self.report_list_dict[line]["source_ip"],
                                   self.report_list_dict[line]["status"]])                                                                                          
        
        self.treeview.set_model(self.store) #It must be after the store update           
                  

class ReceiveDetailsTab(gtk.VBox): 
    """
    ReceiveDetailsTab: Show the received reports from other peers
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)
        
        self.__create_record()
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()    
    
    def __create_record(self):
        """
        """
        self.report_list_dict = {}
        self.report_details_dict = {
                                     "report_id":"",
                                     "test_id":"",
                                     "time_gen":"",
                                     "time_received"
                                     "content":"",
                                     "source_id":"",
                                     "source_ip":"",
                                     "status":""
                                     }       
    
    def __create_widgets(self):
        """
        """
        
        self.column_names = ['ID','TestID','Generated Time','Received Time',
                             'Content','SourceID','SourceIP','Status']
        
        self.store = gtk.ListStore(str,str,str,str,str,str,str,str)
        self.treeview = gtk.TreeView()
       
        self.treeview.set_rules_hint(True)
        self.treeview.set_sensitive(False)
        
        self.__create_columns()
    
    def __pack_widgets(self):   
        """
        """
        self.add(self.treeview)
    
    def __connected_widgets(self):
        """
        """
        pass   
    
    def __create_columns(self):
        """
        """
        for i in range(0,len(self.column_names)):
            rendererText = gtk.CellRendererText()
            column = gtk.TreeViewColumn(self.column_names[i],rendererText,text = i) #text attributes MUST!
            column.set_sort_column_id(i)
            self.treeview.append_column(column)  
            
            
    def show_details(self,report_type):
        """
        Report Details: Sent and unsent
        """
        self.report_list_dict = {}
        cnt =0
        
        from umit.icm.agent.gui.dashboard.DashboardListBase import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED        
        ###########################
        #Get Report Details From DB
        rs = g_db_helper.get_report_sets(report_type=report_type)
        
        if rs == None:
            g_logger.info("Cannot load any reports from DB.")
            self.treeview.set_sensitive(True)
            self.store.clear()
            self.treeview.set_model(self.store) #It must be after the store update
            return 
        
        for record in rs:
            self.report_list_dict[cnt] = {}
            self.report_list_dict[cnt]["report_id"]     = record[0]
            self.report_list_dict[cnt]["test_id"]       = record[1]
            self.report_list_dict[cnt]["time_gen"]      = record[2]
            self.report_list_dict[cnt]["time_received"] = record[3] 
            self.report_list_dict[cnt]["content"]       = record[4]
            self.report_list_dict[cnt]["source_id"]     = record[5]
            self.report_list_dict[cnt]["source_ip"]     = record[6]
            self.report_list_dict[cnt]["status"]        = record[7] 

            cnt += 1
        
        g_logger.info("Loaded %d reports from DB." % len(rs)) 
        
        #####################
        #Output in the Window
        self.treeview.set_sensitive(True) 
        self.store.clear()
        
        for line in self.report_list_dict.keys():
                self.store.append(
                                  [self.report_list_dict[line]["report_id"],
                                   self.report_list_dict[line]["test_id"],
                                   self.report_list_dict[line]["time_gen"],
                                   self.report_list_dict[line]["time_received"],
                                   self.report_list_dict[line]["content"],
                                   self.report_list_dict[line]["source_id"],
                                   self.report_list_dict[line]["source_ip"],
                                   self.report_list_dict[line]["status"]])                                                                                          
        
        self.treeview.set_model(self.store) #It must be after the store update           
                          
    
    
    
    
    
    
    
    
    
    
        
