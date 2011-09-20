#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
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

class NavigationBox(HIGVBox):

    def __init__(self, viewName, dashboard):
        HIGVBox.__init__(self)
        self.dashboard = dashboard
        self.set_size_request(180, 180)
        self.treestore = gtk.TreeStore(str)

        piter = self.treestore.append(None, ['Reports'])
        self.treestore.append(piter, ['Reports Sent'])
        self.treestore.append(piter, ['Reports Received'])

        piter = self.treestore.append(None, ['Tasks'])
        self.treestore.append(piter, ['Tasks Succeeded'])
        self.treestore.append(piter, ['Tasks Failed'])

        piter = self.treestore.append(None, ['Connections'])
        self.treestore.append(piter, ['Aggregator'])
        self.treestore.append(piter, ['Super Agent'])
        self.treestore.append(piter, ['Normal Agent'])
        self.treestore.append(piter, ['Mobile Agent'])

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
        self.dashboard.cur_tab = self.treestore.get_value(iter, 0)
        self.dashboard.refresh()

class DashboardWindow(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Dashboard'))
        self.set_border_width(10)
        self.set_size_request(640, 500)

        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)

        self.navigation_box = NavigationBox(_('Dashboard Menu'), self)

        self.vpaned = gtk.VPaned()
        self.line_chart = LineChart()
        self.graph = Graph("NewGraph", "Title", [(1,1),(2,2),(3,3)])
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

        self.detail_liststore.append(['Report sent to Aggregator',None, '45'])
        self.detail_liststore.append(['Report sent to Super Agent', None, '50'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])
        self.detail_liststore.append(['Report sent to Desk Agent', None, '35'])

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
        self.hpaned.add1(self.navigation_box)
        self.hpaned.add2(self.vpaned)

        self.vpaned.add1(self.line_chart)
        self.vpaned.add2(self.detail_sw)

    def refresh(self):
        print(self.cur_tab)


if __name__ == "__main__":
    wnd = DashboardWindow()
    wnd.show_all()
    gtk.main()

