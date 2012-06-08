#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#          Alan Wang <wzj401@gmail.com>
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

update_time_str = {
                   "Every Start":1,
                   #"Every Week":2,
                   #"Every Two Weeks":3,
                   #"Every Month":4,
                   "Never":2
                   }
update_method_str = {
                     "Show right now":1,
                     "Download and Installation":2
                     }

class PreferenceWindow(HIGWindow):
    """
    User Preference
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Preference'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
                
        self.__create_widgets()
        self.__pack_widgets()
        self.load_preference()

    def __create_widgets(self):
        # Main widgets
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)
        self.vbox = HIGVBox()
        self.btn_box = gtk.HButtonBox()
        self.ok_button = gtk.Button(stock=gtk.STOCK_OK)
        self.ok_button.connect('clicked', lambda x: self.clicked_ok())
        self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        self.apply_button.connect('clicked', lambda x: self.save_preference())
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', lambda x: self.destroy())
        # notebook
        self.notebook = gtk.Notebook()
        # Preference page
        self.pref_page = PreferencePage()
        self.notebook.append_page(self.pref_page, gtk.Label(_("Preference")))
        # Tests page
        self.test_page = TestPage()
        self.notebook.append_page(self.test_page, gtk.Label(_("Tests")))
        # Feedback page
        self.feedback_page = FeedbackPage()
        self.notebook.append_page(self.feedback_page, gtk.Label(_("Feedback")))
        # Update page
        self.update_page = UpdatePage()
        self.notebook.append_page(self.update_page, gtk.Label(_("Update")))

    def __pack_widgets(self):
        # Search Notebook
        self.vbox._pack_expand_fill(self.notebook)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.ok_button)
        self.btn_box.pack_start(self.apply_button)
        self.btn_box.pack_start(self.cancel_button)
        self.vbox.pack_start(self.btn_box)

        self.notebook.set_border_width(1)
        self.vbox.set_border_width(12)

        self.hpaned.pack1(self.vbox, True, False)

    def show_super_peer_list_window(self):
        wnd = SuperPeerListWindow()
        wnd.show_all()

    def clicked_ok(self):
        self.save_preference()
        self.destroy()

    def save_preference(self):
        """"""        
        self.save_basic()
        self.save_tests()
        self.save_updates()

    def save_basic(self):
        """"""
        user_email = self.pref_page.email_entry.get_text()
        if user_email != '': # and is valid
            theApp.peer_info.Email = user_email

        startup_on_boot = self.pref_page.startup_check.get_active()
        self.pref_page.startup_set(startup_on_boot)
        g_config.set('application', 'startup_on_boot', str(startup_on_boot))

        disable_notifications = self.pref_page.notification_check.get_active()
        g_config.set('application', 'disable_notifications', str(disable_notifications))
        
        auto_login = self.pref_page.login_ckeck.get_active()        
        g_config.set('application', 'auto_login', str(auto_login))

        aggregator_url = self.pref_page.cloudagg_entry.get_text()
        theApp.aggregator.base_url = aggregator_url
        if aggregator_url != None and aggregator_url != "":
            g_config.set('network', 'aggregator_url', aggregator_url)
            g_db_helper.set_value('config','aggregator_url', aggregator_url)
    
    def load_preference(self):
        """"""
        self.load_basic()
        self.load_tests()
        self.load_updates()
        
    def load_basic(self):
        """"""
        self.pref_page.peerid_label2.set_text(str(theApp.peer_info.ID))
        self.pref_page.email_entry.set_text(theApp.peer_info.Email)

        startup_on_boot = g_config.getboolean('application', 'startup_on_boot')
        if startup_on_boot:
            self.pref_page.startup_check.set_active(True)
        else:
            self.pref_page.startup_check.set_active(False)
        
        disable_notifications = g_config.getboolean('application', 'disable_notifications')
        if disable_notifications:
            self.pref_page.notification_check.set_active(True)
        else:
            self.pref_page.notification_check.set_active(False)
        
        #auto_login = g_config.getboolean('application', 'auto_login')
        auto_login = True
        if auto_login:
            self.pref_page.login_ckeck.set_active(True)
        else:
            self.pref_page.login_ckeck.set_active(False)
            
        self.pref_page.cloudagg_entry.set_text(theApp.aggregator.base_url)
                
    def save_updates(self):
        """"""
        auto_update = self.update_page.update_check.get_active()
        g_config.set('application', 'auto_update', str(auto_update))
        
        update_time  = self.update_page.update_time_entry.get_active_text()
        if update_time != "" and update_time != None :
            g_config.set('update', 'update_time',update_time)
        
        update_method = self.update_page.update_method_entry.get_active_text()
        if update_method != "" and update_method != None :
            g_config.set('update', 'update_method',update_method)   
            
        update_detect = self.update_page.update_switch_check.get_active()
        g_config.set('update', 'update_detect',str(update_detect))

    def load_updates(self):
        """"""
        auto_update = g_config.getboolean('application', 'auto_update')
        if auto_update:
            self.update_page.update_check.set_active(True)
        else:
            self.update_page.update_check.set_active(False)
        
        update_time  = g_config.get('update', 'update_time')
        if update_time != "" and update_time != None: 
            self.update_page.update_time_entry.set_text_column(update_time_str[update_time])
        update_method = g_config.get('update', 'update_method')
        if update_method != "" and update_method != None:    
            self.update_page.update_method_entry.set_text_column(update_method_str[update_method])
        
        update_detect = g_config.getboolean('update', 'update_detect')
        if update_detect:
            self.update_page.update_switch_check.set_active(True)
        else:
            self.update_page.update_switch_check.set_active(False)
        
    def save_tests(self):
        """"""
        #The test should be stored into the DB
        SELECTED_TESTS = [ r[0] for r in self.test_page.subbox.\
                           tree_view_selected_tests.treestore ]

        if ALL_TESTS[0] not in SELECTED_TESTS:
            SELECTED_TESTS.append(ALL_TESTS[0])
            
        g_db_helper.set_value('config','selected_tests', SELECTED_TESTS)

        auto_update_test = self.test_page.checkbtn.get_active()
        g_config.set('application', 'auto_update_test', str(auto_update_test))
 
        load_http_throttled_test = self.test_page.checkbtn_throttled.get_active()
        g_config.set('application', 'load_http_throttled_test',str(load_http_throttled_test))       
  
    def load_tests(self):
        """"""
        ts = self.test_page.subbox.tree_view_installed_tests.treestore
        for tname in ALL_TESTS:
            ts.append(None, [tname])

        #SELECTED_TESTS = g_config.get('application', 'selected_tests')
        #Here, we use datebase to store the selected test
        SELECTED_TESTS = g_db_helper.get_value('config','selected_tests')
        
        if SELECTED_TESTS:
            ts = self.test_page.subbox.tree_view_selected_tests.treestore
            for tname in SELECTED_TESTS:
                ts.append(None, [tname])

        auto_update_test = g_config.getboolean('application', 'auto_update_test')
        if auto_update_test:
            self.test_page.checkbtn.set_active(True)
        else:
            self.test_page.checkbtn.set_active(False)
            
        load_http_throttled_test = g_config.getboolean('application', 'load_http_throttled_test')
        if load_http_throttled_test:
            self.test_page.checkbtn_throttled.set_active(True)
        else:
            self.test_page.checkbtn_throttled.set_active(False)        
        

#---------------------------------------------------------------------
class PreferencePage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.peerinfo_hbox = HIGHBox()
        self.cloudagg_hbox = HIGHBox()
        self.superpeers_hbox = HIGHBox()

        self.peerinfo_section = HIGSectionLabel(_("Peer Info"))
        self.peerinfo_table = HIGTable()
        self.cloudagg_section = HIGSectionLabel(_("Cloud Aggregator"))
        self.cloudagg_table = HIGTable()
        self.cloudagg_subhbox = HIGHBox()
        self.superpeers_section = HIGSectionLabel(_("Super Peers"))
        self.superpeers_table = HIGTable()

        self.peerid_label = HIGEntryLabel(_("Peer ID:"))
        self.email_label = HIGEntryLabel(_("Email Address:"))
        self.peerid_label2 = HIGEntryLabel()
        self.email_entry = gtk.Entry()
        self.startup_check = gtk.CheckButton(_("Startup on boot"))
        self.notification_check = gtk.CheckButton(_("Notification Switch"))
        self.login_ckeck = gtk.CheckButton(_("Auto login"))

        self.cloudagg_entry = gtk.Entry()
        self.cloudagg_button = HIGButton(_("Reset"))
        self.cloudagg_button.connect('clicked', lambda w:
                                      self.cloudagg_entry.set_text('http://alpha.openmonitor.org/api'))
        self.cloudagg_button.set_size_request(80, 28)

        self.superpeers_entry = gtk.Entry()
        self.superpeers_entry.set_size_request(300, 26)
        self.superpeers_subhbox = HIGHBox()
        self.btn_box = gtk.HButtonBox()
        self.superpeers_button1 = HIGButton(_("Add"))
        self.superpeers_button1.connect(
            'clicked', lambda w: reactor.connectTCP(peer_entry.IP,
                                                    peer_entry.Port,
                                                    theApp.factory))
        self.superpeers_button2 = HIGButton(_("Show all"))
        self.superpeers_button2.connect('clicked', lambda w:
                                        self.show_super_peer_list_window())

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.peerinfo_section)
        self._pack_noexpand_nofill(self.peerinfo_hbox)
        self._pack_noexpand_nofill(self.cloudagg_section)
        self._pack_noexpand_nofill(self.cloudagg_hbox)
        self._pack_noexpand_nofill(self.superpeers_section)
        self._pack_noexpand_nofill(self.superpeers_hbox)

        self.peerinfo_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.peerinfo_hbox._pack_expand_fill(self.peerinfo_table)
        self.cloudagg_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.cloudagg_hbox._pack_expand_fill(self.cloudagg_table)
        self.superpeers_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.superpeers_hbox._pack_expand_fill(self.superpeers_table)

        self.peerinfo_table.attach_label(self.peerid_label, 0, 1, 0, 1)
        self.peerinfo_table.attach_label(self.email_label, 0, 1, 1, 2)

        self.peerinfo_table.attach_label(self.peerid_label2, 1, 2, 0, 1)
        self.peerinfo_table.attach_entry(self.email_entry, 1, 2, 1, 2)
        self.peerinfo_table.attach_label(self.startup_check, 0, 2, 2, 3)
        self.peerinfo_table.attach_label(self.notification_check, 0, 3, 3, 4)
        self.peerinfo_table.attach_label(self.login_ckeck, 0, 4, 4, 5)
        
        self.cloudagg_subhbox._pack_expand_fill(self.cloudagg_entry)
        self.cloudagg_subhbox._pack_noexpand_nofill(self.cloudagg_button)
        self.cloudagg_table.attach_entry(self.cloudagg_subhbox, 0, 1, 0, 1)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(8)
        self.btn_box.pack_start(self.superpeers_button1)
        self.btn_box.pack_start(self.superpeers_button2)
        self.superpeers_subhbox._pack_expand_fill(self.superpeers_entry)
        self.superpeers_subhbox._pack_noexpand_nofill(self.btn_box)
        self.superpeers_table.attach_label(self.superpeers_subhbox, 0, 1, 0, 1)
        
    def startup_set(self,is_start_up=True):
        """"""
        start = StartUP()
        if is_start_up:
            start.set_startup()
        else:
            start.clear_startup()

#---------------------------------------------------------------------
class UpdatePage(HIGVBox):
    """"""
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self.__load_list()
        self.__connect_widgets()
        
    def __create_widgets(self):
        """"""
        
        self.update_switch_hbox = HIGHBox()
        self.update_settings_hbox = HIGHBox()

        self.update_switch_section = HIGSectionLabel(_("Update News Detect"))        
        self.update_switch_table = HIGTable()
        self.update_settings_section = HIGSectionLabel(_("Update Settings"))        
        self.update_settings_table = HIGTable()  
        
        self.update_check = gtk.CheckButton(_("Automatically update"))
        self.update_switch_check = gtk.CheckButton(_("Software Update Detect Switch"))
        self.update_times_label = HIGEntryLabel(_("Auto detect update news"))
        self.update_method_label = HIGEntryLabel(_("Update method"))       
        
        self.update_time_store = gtk.ListStore(str)
        self.update_time_entry = gtk.ComboBoxEntry(self.update_time_store, 0)
        self.update_method_store = gtk.ListStore(str)
        self.update_method_entry = gtk.ComboBoxEntry(self.update_method_store, 0)        
         
    def __pack_widgets(self):
        """"""
        self.set_border_width(12) 
        
        self._pack_noexpand_nofill(self.update_switch_section)
        self._pack_noexpand_nofill(self.update_switch_hbox)
        self._pack_noexpand_nofill(hig_box_space_holder())
        self._pack_noexpand_nofill(self.update_settings_section)
        self._pack_noexpand_nofill(self.update_settings_hbox)
        
        self.update_switch_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.update_switch_hbox._pack_expand_fill(self.update_switch_table)
        self.update_settings_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.update_settings_hbox._pack_expand_fill(self.update_settings_table)
        
        self.update_switch_table.attach_label(self.update_check, 0, 2, 0, 1)
        self.update_switch_table.attach_label(self.update_switch_check, 0, 2, 1, 2)
        self.update_settings_table.attach_label(self.update_times_label, 0, 1, 0, 1)
        self.update_settings_table.attach_entry(self.update_time_entry, 1, 2, 0, 1 )   
        self.update_settings_table.attach_label(self.update_method_label, 0, 1, 1, 2)
        self.update_settings_table.attach_entry(self.update_method_entry, 1, 2, 1, 2 ) 
    
    def __connect_widgets(self):
        """"""
        self.update_check.connect('toggled',lambda w:self.__change_widgets_status()) 
    
    def __change_widgets_status(self):
        """"""
        if self.update_check.get_active():
            self.__disable_widgets()            
        else:
            self.__enable_widgets()
    
    def __load_list(self):
        """"""
        for s in update_time_str.keys():
            #print s
            self.update_time_store.append([s])
        for s in update_method_str.keys():
            #print s
            self.update_method_store.append([s])
    
    def __disable_widgets(self):
        """"""
        self.update_switch_check.set_sensitive(False)
        self.update_method_entry.set_sensitive(False)
        self.update_time_entry.set_sensitive(False)
        
    def __enable_widgets(self):
        """"""
        self.update_switch_check.set_sensitive(True)
        self.update_method_entry.set_sensitive(True)
        self.update_time_entry.set_sensitive(True)        
            
#---------------------------------------------------------------------
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
        theApp.aggregator.check_tests()

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

#---------------------------------------------------------------------
class FeedbackPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self.__set_values()

    def __create_widgets(self):
        self.suggestion_hbox = HIGHBox()
        self.report_hbox = HIGHBox()

        self.suggestion_section = HIGSectionLabel(_("Test Suggestion"))
        self.suggestion_table = HIGTable()
        self.report_section = HIGSectionLabel(_("Bug Report"))
        self.report_table = HIGTable()

        # Website Suggestion
        self.website_suggestion_table = HIGTable()
        self.website_suggestion_slabel = HIGSectionLabel(_("Website Suggestion"))
        self.website_url_subhbox = HIGHBox()
        self.website_url_label = HIGEntryLabel(_("URL:"))
        self.website_url_entry = gtk.Entry()
        self.website_suggestion_sendbtn = HIGButton(_('Send'))
        self.website_suggestion_sendbtn.set_size_request(60, 25)
        self.website_suggestion_sendbtn.connect(
            'clicked', lambda x: self.send_website_suggestion())
        # Service Suggestion
        self.service_suggestion_table = HIGTable()
        self.service_suggestion_slabel = HIGSectionLabel(_("Service Suggestion"))
        self.service_name_subhbox = HIGHBox()
        self.service_name_label = HIGEntryLabel(_("Name:"))
        self.service_list_store = gtk.ListStore(str)
        self.service_name_entry = gtk.ComboBoxEntry(self.service_list_store, 0)
        self.service_host_subhbox = HIGHBox()
        self.service_host_label = HIGEntryLabel(_("Hostname:"))
        self.service_host_entry = gtk.Entry()
        self.service_ip_subhbox = HIGHBox()
        self.service_ip_label = HIGEntryLabel(_("IP:"))
        self.service_ip_entry = gtk.Entry()
        self.service_suggestion_sendbtn = HIGButton(_('Send'))
        self.service_suggestion_sendbtn.set_size_request(60, 25)
        self.service_suggestion_sendbtn.connect(
            'clicked', lambda x: self.send_service_suggestion())

        self.report_namelabel = HIGEntryLabel(_("Your Name:"))
        self.report_nameentry = gtk.Entry()
        #self.report_nameentry.set_has_frame(True)
        self.report_nameentry.set_size_request(100, 26)
        self.report_emaillabel = HIGEntryLabel(_("Email:"))
        self.report_emailentry = gtk.Entry()
        self.report_emailentry.set_size_request(198, 26)
        self.report_subhbox1 = HIGHBox()

        self.report_sw = gtk.ScrolledWindow()
        self.report_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.report_textview = gtk.TextView()
        self.report_textbuffer = self.report_textview.get_buffer()
        self.report_textview.set_editable(True)
        self.report_textview.set_wrap_mode(True)
        self.report_textview.set_border_width(2)
        self.report_sw.add(self.report_textview)
        self.report_sw.show()
        self.report_textview.show()
        self.report_subhbox2 = HIGHBox()
        self.report_sendbtn = HIGButton(_('Send'))
        self.report_sendbtn.set_size_request(60, 25)
        self.report_sendbtn.connect('clicked', lambda x: self.send_bug_report())
        self.report_subhbox3 = HIGHBox()

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.suggestion_section)
        self._pack_noexpand_nofill(self.suggestion_hbox)
        self._pack_noexpand_nofill(self.report_section)
        self._pack_noexpand_nofill(self.report_hbox)

        #self.suggestion_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.suggestion_hbox._pack_expand_fill(self.suggestion_table)
        #self.report_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.report_hbox._pack_expand_fill(self.report_table)


        self.suggestion_hbox._pack_expand_fill(self.suggestion_table)
        #self.suggestion_hbox._pack_expand_fill(self.service_suggestion_table)

        self.suggestion_table.attach_label(self.website_suggestion_slabel,
                                           0, 2, 0, 1)
        self.suggestion_table.attach_label(self.website_url_label,
                                           0, 1, 1, 2)
        self.suggestion_table.attach_entry(self.website_url_entry,
                                           1, 2, 1, 2)
        self.suggestion_table.attach(self.website_suggestion_sendbtn,
                                     0, 2, 2, 3, gtk.PACK_START)

        self.suggestion_table.attach_label(self.service_suggestion_slabel,
                                           2, 4, 0, 1)
        self.suggestion_table.attach_label(self.service_name_label,
                                           2, 3, 1, 2)
        self.suggestion_table.attach_entry(self.service_name_entry,
                                           3, 4, 1, 2)
        self.suggestion_table.attach_label(self.service_host_label,
                                           2, 3, 2, 3)
        self.suggestion_table.attach_entry(self.service_host_entry,
                                           3, 4, 2, 3)
        self.suggestion_table.attach_label(self.service_ip_label,
                                           2, 3, 3, 4)
        self.suggestion_table.attach_entry(self.service_ip_entry,
                                           3, 4, 3, 4)
        self.suggestion_table.attach(self.service_suggestion_sendbtn,
                                     2, 4, 4, 5, gtk.PACK_START)

        self.report_subhbox1.pack_start(self.report_namelabel, True, True, 0)
        self.report_subhbox1.pack_start(self.report_nameentry, True, True, 0)
        self.report_subhbox1.pack_start(self.report_emaillabel, True, True, 0)
        self.report_subhbox1.pack_start(self.report_emailentry)
        self.report_table.attach(self.report_subhbox1, 0, 1, 0, 1)
        self.report_subhbox2.pack_start(self.report_sw)
        self.report_table.attach(self.report_subhbox2, 0, 1, 1, 2)
        self.report_subhbox3.pack_start(self.report_sendbtn)
        self.report_table.attach(self.report_subhbox3, 0, 1, 2, 3, gtk.PACK_START)

    def __set_values(self):
        from umit.icm.agent.test import SUPPORTED_SERVICES
        for each in SUPPORTED_SERVICES:
            self.service_list_store.append([each])

    def send_website_suggestion(self):
        website_url = self.website_url_entry.get_text()
        if website_url == '':
            alert = HIGAlertDialog(message_format=_("Missing fields."),
                                   secondary_text=_("Please input all fields "
                                                    "for website suggestion."))
            alert.run()
            alert.destroy()
            return
        d = theApp.aggregator.send_website_suggestion(website_url)
        d.addCallback(self.show_result)

    def send_service_suggestion(self):
        service_name = self.service_name_entry.child.get_text()
        host_name = self.service_host_entry.get_text()
        ip = self.service_ip_entry.get_text()
        if service_name == '' or host_name == '' or ip == '':
            alert = HIGAlertDialog(message_format=_("Missing fields."),
                                   secondary_text=_("Please input all fields "\
                                                    "for service suggestion."))
            alert.run()
            alert.destroy()
            return
        d = theApp.aggregator.send_service_suggestion(service_name, host_name, ip)
        d.addCallback(self.show_result)

    def send_bug_report(self):
        pass

    def show_result(self, result):
        if result is True:
            alert = HIGAlertDialog(message_format=_("Succuss."),
                                   secondary_text=_("Send to aggregaetor successfully."))
            alert.run()
            alert.destroy()
        else:
            alert = HIGAlertDialog(message_format=_("Error."),
                                   secondary_text=_("Send to aggregaetor failed."))
            alert.run()
            alert.destroy()

class SuperPeerListWindow(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Super Peers'))
        self.__create_widgets()
        self.__pack_widgets()
        self.__load_super_peers()

    def __create_widgets(self):
        self.main_vbox = HIGVBox()
        self.add(self.main_vbox)
        self.btn_box = gtk.HButtonBox()
        self.ok_button = gtk.Button(stock=gtk.STOCK_SAVE)
        self.ok_button.connect('clicked', lambda x: self.__save_super_peers())
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', lambda x: self.destroy())

        self.SuperPeersBox_vbox = HIGVBox()
        self.SuperPeersBox_hbox1 = HIGHBox()
        self.SuperPeersBox_hbox2 = HIGHBox()
        self.SuperPeersBox_subbox = SuperPeersBox()
        self.SuperPeersBox_hbox1.add(self.SuperPeersBox_subbox)

    def __pack_widgets(self):
        self.main_vbox._pack_expand_fill(self.SuperPeersBox_hbox1)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.ok_button)
        self.btn_box.pack_start(self.cancel_button)
        self.main_vbox.pack_start(self.btn_box)
        self.main_vbox.set_border_width(12)

        self.SuperPeersBox_vbox.pack_start(self.SuperPeersBox_hbox1, True, True, 5)
        self.SuperPeersBox_vbox.pack_start(self.SuperPeersBox_hbox2, True, True, 5)

    def __save_super_peers(self):
        self.destroy()

    def __load_super_peers(self):
        text = ""
        for peer_entry in theApp.peer_manager.super_peers.values():
            text = text + "%s:%d\n" % (peer_entry.IP, peer_entry.Port)
        self.SuperPeersBox_subbox.textbuffer.set_text(text)

class SuperPeersBox(gtk.VBox):
    def __init__(self):
        super(SuperPeersBox, self).__init__()
        self.set_size_request(400, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("""\
<span size='12000'>Super Peer List: \n</span>""")

        title.set_use_markup(True)

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 0, 1, 0, 1, gtk.FILL,
                     gtk.FILL, 0, 0);

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        wins = gtk.TextView()
        self.textbuffer = wins.get_buffer()
        wins.set_editable(True)
        wins.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        wins.set_cursor_visible(True)
        wins.show()
        sw.add(wins)
        sw.show()
        table.attach(sw, 0, 1, 1, 3)
        self.add(table)


if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = PreferenceWindow()
    #wnd.set_size_request(520, 440)
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()