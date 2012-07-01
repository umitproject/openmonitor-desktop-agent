#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#          Tianwei Liu <liutainweidlut@gmail.com> 
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

from pygtk_chart.line_chart import LineChart, Graph

from higwidgets.higboxes import HIGVBox
from higwidgets.higwindows import HIGWindow

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp

from ReportsTab import ReportsTab,ReceiveDetailsTab,ReportDetailsTab
from ConnectionTab import ConnectionsIndividualTab,ConnectionsTab
from TaskTab import TaskTab,TaskDetailsTab,TaskExecuteTab
from CapacityTab import CapacityTab,ThrottledTab,ServiceTab

from DashboardListBase import  *

class NavigationBox(HIGVBox):

    def __init__(self, viewName, dashboard):
        HIGVBox.__init__(self)
        self.dashboard = dashboard
        self.set_size_request(240, 720)
        self.treestore = gtk.TreeStore(str)

        piter = self.treestore.append(None, [CAPACITY])
        self.treestore.append(piter, [CAPA_THROTTLED])
        self.treestore.append(piter, [CAPA_SERVICE])
        
        piter = self.treestore.append(None, [REPORT])        #Report statistics
        self.treestore.append(piter, [REPORT_SENT])
        self.treestore.append(piter, [REPORT_UNSENT])
        self.treestore.append(piter, [REPORT_RECEIVED])

        piter = self.treestore.append(None, [TASK])      
        self.treestore.append(piter, [TASK_ALL])
        self.treestore.append(piter, [TASK_SUCCESSED])
        self.treestore.append(piter, [TASK_FAILED])

        piter = self.treestore.append(None, [CONNECTION])
        self.treestore.append(piter, [CONN_AGG])
        self.treestore.append(piter, [CONN_SUPER])
        self.treestore.append(piter, [CONN_NORMAL])
        self.treestore.append(piter, [CONN_MOBILE])

        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.connect('cursor-changed', self.on_cursor_changed)
        self.tvcolumn = gtk.TreeViewColumn(viewName)
        self.treeview.append_column(self.tvcolumn)
        self.treeview.set_show_expanders(True)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.treeview.expand_all()
        self.add(self.treeview)
        self.show_all()

    def on_cursor_changed(self, treeview):
        selection = self.treeview.get_selection()
        (model, iter) = selection.get_selected()
        if iter != None:
            self.dashboard.cur_tab = self.treestore.get_value(iter, 0)
            self.dashboard.refresh()

class DashboardWindow(HIGWindow):
    def __init__(self):
        """
        """
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('OpenMonitor Dashboard'))
        self.set_border_width(10)
        self.set_size_request(1280, 820)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self.switch_dict = {}
        self.conn_type = None
        self.task_type = None
        self.create_tabs = False
        
        self.__create_widgets()
        self.__pack_widgets()
        self.create_switch()
        
    def __create_widgets(self):
        """
        """        
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)

        self.navigation_box = NavigationBox(_('Dashboard Menu'), self)
        
        self.vpaned = gtk.VPaned()
        self.line_chart = LineChart()
        self.graph = Graph("NewGraph", "", [(1,1),(2,2),(3,3)])
        self.line_chart.set_xrange((0, 10))
        self.line_chart.set_yrange((0, 5))
        self.line_chart.add_graph(self.graph)
        self.line_chart.set_size_request(460, 320)

        self.detail_sw = gtk.ScrolledWindow()
        
        self.detail_sw.set_size_request(450, 180)
        
        self.box_container = gtk.VBox()

        #####
        #Task 
        self.task_tab = TaskTab()
        self.task_details_tab = TaskDetailsTab()
        self.task_execute_tab = TaskExecuteTab()
        
        ###########
        #Connection
        self.connections_tab = ConnectionsTab()
        self.connections_individual_tab = ConnectionsIndividualTab()   
        
        ########
        #Reports
        self.report_tab = ReportsTab()
        self.report_details_tab = ReportDetailsTab()
        self.report_recv_details_tab = ReceiveDetailsTab() 
        
        #########
        #Capacity
        self.capacity_tab = CapacityTab()
        self.throttled_tab = ThrottledTab()
        self.service_tab = ServiceTab()


    def __pack_widgets(self):
        """
        """
        self.hpaned.add1(self.navigation_box)
        self.hpaned.add2(self.vpaned)

        self.vpaned.add1(self.line_chart)
        self.vpaned.add2(self.detail_sw)

        self.detail_sw.add_with_viewport(self.box_container)
        
        self.add_tabs()

        self.box_container.hide_all()
        
        self.show_all()
        
    def show_all_modify(self):
        """"""
        self.hide_all_tabs()

    def add_tabs(self):
        """
        """
        self.box_container.add(self.task_tab)
        self.box_container.add(self.task_details_tab)
        self.box_container.add(self.task_execute_tab)
        self.box_container.add(self.connections_tab)
        self.box_container.add(self.connections_individual_tab)
        self.box_container.add(self.report_tab)
        self.box_container.add(self.report_details_tab)
        self.box_container.add(self.report_recv_details_tab)
        self.box_container.add(self.capacity_tab)
        self.box_container.add(self.throttled_tab)
        self.box_container.add(self.service_tab)
    
    def hide_all_tabs(self):
        self.capacity_tab.set_visible(False)
        self.throttled_tab.set_visible(False)
        self.service_tab.set_visible(False)
        self.report_tab.set_visible(False)
        self.report_details_tab.set_visible(False)
        self.report_recv_details_tab.set_visible(False)   
        self.connections_tab.set_visible(False)
        self.connections_individual_tab.set_visible(False)      
        self.task_tab.set_visible(False)
        self.task_details_tab.set_visible(False)
        self.task_execute_tab.set_visible(False)
        
    def show_one(self,show_type=None):
        """
        """
        self.hide_all_tabs()
        if show_type == TASK:
            self.task_tab.set_visible(True)
        elif show_type == TASK_ALL :
            self.task_details_tab.set_visible(True)
        elif show_type == TASK_SUCCESSED or show_type == TASK_FAILED:
            self.task_execute_tab.set_visible(True)
        elif show_type == REPORT:
            self.report_tab.set_visible(True)
        elif show_type == REPORT_SENT or show_type == REPORT_UNSENT:
            self.report_details_tab.set_visible(True)
        elif show_type == REPORT_RECEIVED:
            self.report_recv_details_tab.set_visible(True)
        elif show_type == CONNECTION:
            self.connections_tab.set_visible(True)
        elif show_type == CONN_AGG or show_type == CONN_SUPER or show_type == CONN_NORMAL or show_type == CONN_MOBILE:
            self.connections_individual_tab.set_visible(True) 
        elif show_type == CAPACITY:
            self.capacity_tab.set_visible(True)
        elif show_type == CAPA_THROTTLED:
            self.throttled_tab.set_visible(True)
        elif show_type == CAPA_SERVICE:
            self.service_tab.set_visible(True)
        
    def refresh_task_statistics(self):
        """
        Task statistics: It will show the Task Done numbers and failed numbers
        """
        self.task_tab.show()
        
    def refresh_task_details(self):
        """
        Task Details: The list store can show the different task details from database
        """
        self.task_details_tab.show(self.task_type)

    def refresh_reports_statistics(self):
        """
        Reports: It can show the report statistics
        """
        self.report_tab.show()

    def refresh_report_details(self,report_type=None):
        """
        Report Details: The list store can show the different report details(sent,unsent,received) from database
        """
        pass


    def refresh_connection(self):
        """
        """
        self.connections_tab.show()

    def refresh_connection_dividual(self):
        """
        """
        self.connections_individual_tab.show(self.conn_type)

    def refresh_capacity(self):
        """"""
        pass
    
    def refresh_throttled(self):
        """"""
        pass
    
    def refresh_service(self):
        """"""
        pass      
    
    def create_switch(self):
        """
        Switch Simulator: Use dict to simulate the switch-case
        """
        self.switch_dict = {
                            ###########
                            #Report tab
                            REPORT          : self.refresh_reports_statistics,
                            REPORT_SENT     : self.refresh_report_details,
                            REPORT_UNSENT   : self.refresh_report_details,
                            REPORT_RECEIVED : self.refresh_report_details,
                            
                            #########
                            #Task tab
                            TASK            : self.refresh_task_statistics,
                            TASK_SUCCESSED  : self.refresh_task_details,
                            TASK_FAILED     : self.refresh_task_details,
                            TASK_ALL        : self.refresh_task_details,
                            
                            #############
                            #Capacity tab
                            CAPACITY        : self.refresh_capacity,
                            CAPA_THROTTLED  : self.refresh_throttled,
                            CAPA_SERVICE    : self.refresh_service,
                            
                            ###############
                            #Connection tab
                            CONNECTION      : self.refresh_connection,
                            CONN_AGG        : self.refresh_connection_dividual,
                            CONN_SUPER      : self.refresh_connection_dividual,
                            CONN_NORMAL     : self.refresh_connection_dividual,
                            CONN_MOBILE     : self.refresh_connection_dividual,
                            }
    
    def refresh(self):
        """
        """
        self.conn_type = self.cur_tab
        self.task_type = self.cur_tab
        result = self.switch_dict[self.cur_tab]()
        self.show_one(self.cur_tab)
     

if __name__ == "__main__":
    wnd = DashboardWindow()
    wnd.show_all()
    gtk.main()
