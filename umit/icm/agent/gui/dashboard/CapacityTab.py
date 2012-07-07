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

#from Dashboard import CAPACITY,CAPA_THROTTLED,CAPA_SERVICE
from umit.icm.agent.gui.dashboard.DashboardListBase import  *

class CapacityTab(gtk.VBox):
    """
    CapacityTab: show the network's Capacity  
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)

        self.set_visible(False)
                
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
    
class ThrottledTab(gtk.VBox):
    """
    ThrottledTab : Show the network throttled 
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)
        
        self.set_visible(False)
        
        self.__create_record()
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()   

    def __create_record(self):
        """
        """
        self.throttled_list_dict = {}
        self.throttled_details_dict = {
                                  "sequence":"",
                                  "test_id":"",
                                  "website_url":"",
                                  "test_type":"",
                                  "done_status":"",
                                  "done_result":"",
                                  "execute_time":"",
                                  }
    
    def __create_widgets(self):
        """
        """
        self.column_names = ['SEQUENCE','TestID','URL','Type','Status',"Result","Time"] 
        
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

    def show_details(self):
        """
        """
        self.throttled_list_dict = {}
        cnt = 0
        
        from umit.icm.agent.gui.dashboard.DashboardListBase import CAPA_THROTTLED,CAPACITY,CAPA_SERVICE
        from umit.icm.agent.gui.dashboard.DashboardListBase import TASK_ALL,TASK_SUCCESSED,TASK_FAILED        
        #########################
        #Get Task Details From DB
        rs = g_db_helper.get_test_sets(test_type = CAPA_THROTTLED)

        if rs == None:
            g_logger.info("Cannot load any WebsiteTest from DB.")
            self.treeview.set_sensitive(True)
            self.store.clear()
            self.treeview.set_model(self.store) #It must be after the store update
            return        
        
        for record in rs:
            self.throttled_list_dict[cnt] = {}
            self.throttled_list_dict[cnt]["sequence"]      = record[0]
            self.throttled_list_dict[cnt]["test_id"]       = record[1]
            self.throttled_list_dict[cnt]["website_url"]   = record[2]
            self.throttled_list_dict[cnt]["test_type"]     = record[3]
            self.throttled_list_dict[cnt]["done_status"]   = record[4] 
            self.throttled_list_dict[cnt]["done_result"]   = record[5]
            self.throttled_list_dict[cnt]["execute_time"]  = record[6]         
            cnt += 1
        
        g_logger.info("Loaded %d tasks(Website) from DB." % len(rs)) 
        
        #####################
        #Output in the Window
        self.treeview.set_sensitive(True) 
        self.store.clear()
        
        for line in self.throttled_list_dict.keys():
                self.store.append(
                                  [self.throttled_list_dict[line]["sequence"],
                                   self.throttled_list_dict[line]["test_id"],
                                   self.throttled_list_dict[line]["website_url"],
                                   self.throttled_list_dict[line]["test_type"],
                                   self.throttled_list_dict[line]["done_status"],
                                   self.throttled_list_dict[line]["done_result"],
                                   self.throttled_list_dict[line]["execute_time"]])                                                                                          
        
        self.treeview.set_model(self.store) #It must be after the store update 
    
class ServiceTab(gtk.VBox): 
    """
    ServiceTab: Show the results of different services
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
        self.service_list_dict = {}
        self.service_details_dict = {
                                  "sequence":"",
                                  "test_id":"",
                                  "test_type":"",
                                  "service_name":"",
                                  "service_ip":"",
                                  "service_port":"",
                                  "done_status":"",
                                  "done_result":"",
                                  "execute_time":"",
                                  }
    
    def __create_widgets(self):
        """
        """
        self.column_names = ['SEQUENCE','TestID','ServiceName','Port',
                             'IP','Type','Status',"Result","Time"] 
        
        self.store = gtk.ListStore(str,str,str,str,str,str,str,str,str)
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

    def show_details(self):
        """
        """
        self.service_list_dict = {}
        cnt = 0
        
        from umit.icm.agent.gui.dashboard.DashboardListBase import CAPA_THROTTLED,CAPACITY,CAPA_SERVICE
        from umit.icm.agent.gui.dashboard.DashboardListBase import TASK_ALL,TASK_SUCCESSED,TASK_FAILED        
        #########################
        #Get Task Details From DB
        rs = g_db_helper.get_test_sets(test_type = CAPA_SERVICE)
        
        if rs == None:
            g_logger.info("Cannot load any ServiceTest from DB.")
            self.treeview.set_sensitive(True)
            self.store.clear()
            self.treeview.set_model(self.store) #It must be after the store update
            return        
        
        for record in rs:
            self.service_list_dict[cnt] = {}
            self.service_list_dict[cnt]["sequence"]      = record[0]
            self.service_list_dict[cnt]["test_id"]       = record[1]
            self.service_list_dict[cnt]["service_name"]  = record[2]
            self.service_list_dict[cnt]["service_port"]  = record[3]
            self.service_list_dict[cnt]["service_ip"]    = record[4]
            self.service_list_dict[cnt]["test_type"]     = record[5]
            self.service_list_dict[cnt]["done_status"]   = record[6] 
            self.service_list_dict[cnt]["done_result"]   = record[7]
            self.service_list_dict[cnt]["execute_time"]  = record[8]         
            cnt += 1
        
        g_logger.info("Loaded %d tasks(Service) from DB." % len(rs)) 
        
        #####################
        #Output in the Window
        self.treeview.set_sensitive(True) 
        self.store.clear()
        
        for line in self.service_list_dict.keys():
                self.store.append(
                                  [self.service_list_dict[line]["sequence"],
                                   self.service_list_dict[line]["test_id"],
                                   self.service_list_dict[line]["service_name"],
                                   self.service_list_dict[line]["service_port"],
                                   self.service_list_dict[line]["service_ip"],
                                   self.service_list_dict[line]["test_type"],
                                   self.service_list_dict[line]["done_status"],
                                   self.service_list_dict[line]["done_result"],
                                   self.service_list_dict[line]["execute_time"]])                                                                                          
        
        self.treeview.set_model(self.store) #It must be after the store update           
                                     








