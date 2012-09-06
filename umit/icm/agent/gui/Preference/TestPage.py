#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
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

import gtk
import sys

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higboxes import HIGSpacer, hig_box_space_holder
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id
from umit.icm.agent.test import ALL_TESTS
from umit.icm.agent.utils.Startup import StartUP

###############################
#Test Page in Preference Window
class TestPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.hbox1 = HIGHBox()
        self.hbox2 = HIGHBox()
        self.subbox = Tests()
        self.hbox1.add(self.subbox)
        self.checkbtn = gtk.CheckButton(_("Update tests module automatically"))
        self.checkbtn_throttled = gtk.CheckButton(_("Load HTTP Throttled Test"))

    def __pack_widgets(self):
        #self.tests_hbox.set_border_width(12)
        self.pack_start(self.hbox1, True, True, 5)
        self.pack_start(self.hbox2, True, True, 5)

        self.checkbtn.set_border_width(8)
        self.checkbtn_throttled.set_border_width(8)
        self.hbox2.add(self.checkbtn)
        self.hbox2.add(self.checkbtn_throttled)

class Tests(gtk.VBox):
    def __init__(self):
        super(Tests, self).__init__()
        self.set_size_request(520, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        self.tree_view_installed_tests = TestsView(_("Installed Tests"))
        table.attach(self.tree_view_installed_tests, 0, 1, 0, 3,
                     gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)

        updatebtn = gtk.Button(_("Update"))
        updatebtn.connect('clicked', lambda w: self.update_test_mod())
        updatebtn.set_size_request(50, 30)
        table.attach(updatebtn, 0, 1, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK, 1, 1)

        vbox = gtk.VBox()
        btnbox = gtk.VButtonBox()
        btnbox.set_border_width(5)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btnbox.set_spacing(5)
        button = gtk.Button(_("Add"))
        button.connect('clicked', lambda w: self.add_test())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Add All"))
        button.connect('clicked', lambda w: self.add_all())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Remove"))
        button.connect('clicked', lambda w: self.remove_test())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Remove All"))
        button.connect('clicked', lambda w: self.remove_all())
        button.set_size_request(50, 30)
        btnbox.add(button)
        table.set_row_spacing(1, 3)
        vbox.add(btnbox)
        table.attach(vbox, 3, 4, 1, 2, gtk.FILL, gtk.SHRINK, 1, 1)

        self.tree_view_selected_tests = TestsView(_("Selected Tests"))
        table.attach(self.tree_view_selected_tests, 4, 5, 1, 3)

        self.add(table)

    def add_test(self):
        tree_selection = self.tree_view_installed_tests.treeview.get_selection()
        tree_iter = tree_selection.get_selected()[1]
        if tree_iter:
            tname = self.tree_view_installed_tests.treestore.\
                  get_value(tree_selection.get_selected()[1], 0)
            values = [ r[0] for r in self.tree_view_selected_tests.treestore ]
            if tname not in values:
                self.tree_view_selected_tests.treestore.append(None, [tname])

    def add_all(self):
        self.tree_view_selected_tests.treestore.clear()
        values = [ r[0] for r in self.tree_view_installed_tests.treestore ]
        for tname in values:
            self.tree_view_selected_tests.treestore.append(None, [tname])

    def remove_test(self):
        tree_selection = self.tree_view_selected_tests.treeview.get_selection()

        #The user cannot delete the website test
        selected_name = self.tree_view_selected_tests.treestore.\
                    get_value(tree_selection.get_selected()[1],0)
        print selected_name
        if selected_name == ALL_TESTS[0]:
            return
        
        tree_iter = tree_selection.get_selected()[1]
        if tree_iter:
            self.tree_view_selected_tests.treestore.remove(tree_iter)

    def remove_all(self):
        self.tree_view_selected_tests.treestore.clear()
        self.tree_view_selected_tests.treestore.append(None,[ALL_TESTS[0]])

    def update_test_mod(self):
        pass                        #It is a bug!!!
        #theApp.aggregator.check_tests()

class TestsView(HIGVBox):

    def __init__(self, viewName):
        super(TestsView, self).__init__()
        self.set_size_request(180, 180)

        self.treestore = gtk.TreeStore(str)
        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn(viewName)
        self.treeview.append_column(self.tvcolumn)

        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.add(self.treeview)
        self.show_all()

