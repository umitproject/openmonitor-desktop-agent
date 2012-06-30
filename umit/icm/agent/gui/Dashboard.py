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

################
#Task Definition
TASK           = _("Tasks")
TASK_ALL       = _("Tasks Details")
TASK_SUCCESSED = _("Tasks Succeeded")
TASK_FAILED    = _("Tasks Failed")

##################
#Report Definition
REPORT         = _("Reports")
REPORT_SENT    = _("Sent Details")
REPORT_UNSENT  = _("Unsent Details")
REPORT_RECEIVED= _("Received Details")

######################
#Connection Definition
CONNECTION    = _("Connections")
CONN_AGG      = _("Aggregator") 
CONN_SUPER    = _("Super Agent")
CONN_NORMAL   = _("Normal Agent") 
CONN_MOBILE   = _("Mobile Agent")

####################
#Capacity Definition
CAPACITY      = _("Capacity")
CAPA_THROTTLED= _("Network Throttled")
CAPA_SERVICE  = _("Network Service")

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
        self.set_size_request(920, 720)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self.switch_dict = {}
        self.conn_type = None
        self.task_type = None
        
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

        self.detail_liststore = gtk.ListStore(str, str, str)
        self.detail_treeview = gtk.TreeView(self.detail_liststore)

        catacolumn = gtk.TreeViewColumn('Catagories')
        timescolumn = gtk.TreeViewColumn('Times')

        self.detail_treeview.append_column(catacolumn)
        self.detail_treeview.append_column(timescolumn)

        catacell = gtk.CellRendererText()
        timecell = gtk.CellRendererText()

        catacolumn.pack_start(catacell, True)
        timescolumn.pack_start(timecell, True)

        catacolumn.set_attributes(catacell, text=0)
        timescolumn.set_attributes(timecell, text=2)
        self.detail_treeview.set_search_column(0)
        catacolumn.set_sort_column_id(0)
        self.detail_treeview.set_reorderable(True)
        self.detail_sw.add(self.detail_treeview)


    def __pack_widgets(self):
        """
        """
        self.hpaned.add1(self.navigation_box)
        self.hpaned.add2(self.vpaned)

        self.vpaned.add1(self.line_chart)
        self.vpaned.add2(self.detail_sw)

    def refresh_task_statistics(self):
        """
        Task statistics: It will show the Task Done numbers and failed numbers
        """
        self.detail_liststore.append(['Current Task Num', None,
                                      theApp.statistics.tasks_current_num])
        self.detail_liststore.append(['Tasks Done', None,
                                      theApp.statistics.tasks_done])
        self.detail_liststore.append(['Tasks Failed', None,
                                      theApp.statistics.tasks_failed])
    
    def refresh_task_details(self):
        """
        Task Details: The list store can show the different task details from database
        """
        if self.task_type == TASK_ALL:
            pass
        elif self.task_type == TASK_SUCCESSED:
            for key,value in theApp.statistics.tasks_done_by_type:
                self.detail_liststore.append([key, None, value])
        elif self.task_type == TASK_FAILED:
            for key,value in theApp.statistics.tasks_failed_by_type:
                self.detail_liststore.append([key, None, value])
    
    def refresh_reports_statistics(self):
        """
        Reports: It can show the report statistics
        """
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
        
    def refresh_report_details(self,report_type=None):
        """
        Report Details: The list store can show the different report details(sent,unsent,received) from database
        """
        pass


    def refresh_connection(self):
        """
        """
        self.detail_liststore.append(['Aggregator Status', None,
                                      theApp.aggregator.available])
        self.detail_liststore.append(['Super Agent Connected', None,
                                      theApp.statistics.super_agents_num])
        self.detail_liststore.append(['Normal Agent Connected', None,
                                      theApp.statistics.normal_agents_num])
        self.detail_liststore.append(['Mobile Agent Connected', None,
                                      theApp.statistics.mobile_agents_num])      
        
    def refresh_connection_dividual(self):
        """
        """
        if self.conn_type == CONN_AGG:
            self.detail_liststore.append(['Aggregator Status', None,
                                          theApp.aggregator.available])
            self.detail_liststore.append(['Aggregator Failure Times', None,
                                          theApp.statistics.aggregator_fail_num])
        elif self.conn_type == CONN_SUPER:
            self.detail_liststore.append(['Super Agent Connected', None,
                                          theApp.statistics.super_agents_num])
            self.detail_liststore.append(['Super Agent Failure Times', None,
                                          theApp.statistics.super_agents_fail_num])
        elif self.conn_type == CONN_NORMAL:
            self.detail_liststore.append(['Normal Agent Connected', None,
                                          theApp.statistics.normal_agents_num])
            self.detail_liststore.append(['Normal Agent Failure Times', None,
                                          theApp.statistics.normal_agents_fail_num])
        elif self.conn_type == CONN_MOBILE:
            self.detail_liststore.append(['Mobile Agent Connected', None,
                                          theApp.statistics.mobile_agents_num])
            self.detail_liststore.append(['Mobile Agent Failure Times', None,
                                          theApp.statistics.mobile_agents_fail_num])
    
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
        self.detail_liststore.clear()
        self.conn_type = self.cur_tab
        self.task_type = self.cur_tab
        result = self.switch_dict[self.cur_tab]()
        

if __name__ == "__main__":
    wnd = DashboardWindow()
    wnd.show_all()
    gtk.main()
