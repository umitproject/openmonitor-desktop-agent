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

from umit.icm.agent.gui.dashboard.DashboardListBase import  *

class TaskTab(DashboardListBase):
    """
    TaskTab: show the statistics about the task numbers (Task sets and TaskAssign)
    """
    def __init__(self):
        """
        """
        DashboardListBase.__init__(self)
        
    def show(self,show_type=None):
        """
        Task statistics: It will show the Task Done numbers and failed numbers
        """
        self.detail_liststore.clear()
        
        self.detail_liststore.append(['Current Task Num', None,
                                      theApp.statistics.tasks_current_num])
        self.detail_liststore.append(['Tasks Done', None,
                                      theApp.statistics.tasks_done])
        self.detail_liststore.append(['Tasks Failed', None,
                                      theApp.statistics.tasks_failed])
               
    
class TaskDetailsTab(DashboardListBase):
    """
    TaskDetailsTab : Show the task details from aggregator or super agent, it will read database
    """
    def __init__(self):
        """
        """
        DashboardListBase.__init__(self)
         
    
    def show(self,show_type=TASK_ALL):
        """
        Task Details: The list store can show the different task details from database
        """
        self.detail_liststore.clear()
        
        if show_type == TASK_ALL:
            pass
        elif show_type == TASK_SUCCESSED:
            for key,value in theApp.statistics.tasks_done_by_type:
                self.detail_liststore.append([key, None, value])
        elif show_type == TASK_FAILED:
            for key,value in theApp.statistics.tasks_failed_by_type:
                self.detail_liststore.append([key, None, value])   
                
          
class TaskExecuteTab(gtk.VBox): 
    """
    TaskExecuteTab: Show the successful and failed tasks details
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)
        
        self.__create_record()
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()          

    def __create_widgets(self):
        """
        """
        self.column_names = ['SEQUENCE','TestID','URL','Type',
                             'Service_name','Service_ip','Service_port',
                             'Status',"Result","Time"] 
        
        self.store = gtk.ListStore(str,str,str,str,str,str,str,str,str,str)
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
    
    def __create_record(self):
        """
        """
        self.task_list_dict = {}
        self.task_details_dict = {
                                  "sequence":"",
                                  "test_id":"",
                                  "website_url":"",
                                  "test_type":"",
                                  "service_name":"",
                                  "service_ip":"",
                                  "service_port":"",
                                  "done_status":"",
                                  "done_result":"",
                                  "execute_time":"",
                                  }
        
    def __create_columns(self):
        """
        """
        for i in range(0,len(self.column_names)):
            rendererText = gtk.CellRendererText()
            column = gtk.TreeViewColumn(self.column_names[i],rendererText,text = i) #text attributes MUST!
            column.set_sort_column_id(i)
            self.treeview.append_column(column) 
            
    def show_details(self,task_type):
        """
        """        
        self.task_list_dict = {}
        cnt = 0

        from umit.icm.agent.gui.dashboard.DashboardListBase import TASK_ALL,TASK_SUCCESSED,TASK_FAILED        
        #########################
        #Get Task Details From DB
        rs = g_db_helper.get_task_sets(task_type=task_type)
        
        if rs == None:
            g_logger.info("Cannot load any Tasks from DB.")
            self.treeview.set_sensitive(True)
            self.store.clear()
            self.treeview.set_model(self.store) #It must be after the store update
            return
        
        for record in rs:
            self.task_list_dict[cnt] = {}
            self.task_list_dict[cnt]["sequence"]      = record[0]
            self.task_list_dict[cnt]["test_id"]       = record[1]
            self.task_list_dict[cnt]["website_url"]   = record[2]
            self.task_list_dict[cnt]["test_type"]     = record[3]
            self.task_list_dict[cnt]["service_name"]  = record[4]
            self.task_list_dict[cnt]["service_ip"]    = record[5]
            self.task_list_dict[cnt]["service_port"]  = record[6] 
            self.task_list_dict[cnt]["done_status"]   = record[7]
            self.task_list_dict[cnt]["done_result"]   = record[8]
            self.task_list_dict[cnt]["execute_time"]  = record[9]             
            cnt += 1
        
        g_logger.info("Loaded %d tasks from DB." % len(rs)) 
        
        #####################
        #Output in the Window
        self.treeview.set_sensitive(True) 
        self.store.clear()
        
        for line in self.task_list_dict.keys():
                self.store.append(
                                  [self.task_list_dict[line]["sequence"],
                                   self.task_list_dict[line]["test_id"],
                                   self.task_list_dict[line]["website_url"],
                                   self.task_list_dict[line]["test_type"],
                                   self.task_list_dict[line]["service_name"],
                                   self.task_list_dict[line]["service_ip"],
                                   self.task_list_dict[line]["service_port"],
                                   self.task_list_dict[line]["done_status"],
                                   self.task_list_dict[line]["done_result"],
                                   self.task_list_dict[line]["execute_time"]])                                                                                          
        
        self.treeview.set_model(self.store) #It must be after the store update           
                                     



