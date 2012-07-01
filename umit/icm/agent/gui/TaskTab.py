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

#from Dashboard import TASK,TASK_ALL,TASK_SUCCESSED,TASK_FAILED
from DashboardListBase import  *

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







