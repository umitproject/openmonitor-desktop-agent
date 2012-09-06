#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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
from higwidgets.higbuttons import HIGStockButton

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id
from umit.icm.agent.test import ALL_TESTS
from umit.icm.agent.utils.Startup import StartUP

from umit.icm.agent.gui.Preference.TestPage import TestPage,Tests,TestsView
from umit.icm.agent.gui.Preference.SuperPeerSetting import SuperPeerListWindow,SuperPeersBox
from umit.icm.agent.gui.Preference.GeneralPage import GeneralPage
from umit.icm.agent.gui.Preference.UpdatePage import update_time_str,update_method_str,UpdatePage
from umit.icm.agent.gui.Preference.FeedbackPage import FeedbackPage
from umit.icm.agent.gui.Preference.PeerPage import PeerInfoPage
from umit.icm.agent.gui.Preference.AdvancedPage import AdvancedPage

class PreferenceWindow(HIGWindow):
    """
    User Preference
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('OpenMonitor Preferences'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
                
        self.__create_widgets()
        self.__pack_widgets()
        self.load_preference()

    def __create_widgets(self):
        # Main widgets
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)
        
        self.vbox = HIGVBox()
        self.btn_box  = gtk.HButtonBox()
        self.btn_box1 = gtk.HButtonBox()
        self.btn_box2 = gtk.HButtonBox()
        
        self.ok_button = gtk.Button(stock=gtk.STOCK_OK)
        self.ok_button.connect('clicked', lambda x: self.clicked_ok())
        self.help_button   = HIGStockButton(gtk.STOCK_DIALOG_INFO,_("help"))
        self.help_button.connect('clicked', lambda x: self.help_direct())
        #self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        #self.apply_button.connect('clicked', lambda x: self.save_preference())
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', lambda x: self.destroy())
        # notebook
        self.notebook = gtk.Notebook()
        # General Preference page
        self.general_page = GeneralPage()
        self.notebook.append_page(self.general_page, gtk.Label(_("General")))
        # Peer Info Page
        self.peer_page = PeerInfoPage()
        self.notebook.append_page(self.peer_page, gtk.Label(_("PeerInfo")))
        # Tests page
        self.test_page = TestPage()
        self.notebook.append_page(self.test_page, gtk.Label(_("Tests")))
        # Feedback page
        self.feedback_page = FeedbackPage()
        self.notebook.append_page(self.feedback_page, gtk.Label(_("Feedback")))
        # Update page
        self.update_page = UpdatePage()
        self.notebook.append_page(self.update_page, gtk.Label(_("Update")))
        # Advanced Page
        self.advanced_page = AdvancedPage()
        self.notebook.append_page(self.advanced_page, gtk.Label(_("Advanced")))        
        

    def __pack_widgets(self):
        # Search Notebook
        self.vbox._pack_expand_fill(self.notebook)

        self.btn_box.set_layout(gtk.BUTTONBOX_EDGE)
        self.btn_box.set_spacing(3)
        
        self.btn_box.pack_start(self.btn_box1) 
        self.btn_box.pack_end(self.btn_box2)
        
        self.btn_box1.set_layout(gtk.BUTTONBOX_START)
        self.btn_box1.set_spacing(3)
        self.btn_box1.pack_start(self.help_button)
        
        self.btn_box2.set_layout(gtk.BUTTONBOX_END)
        self.btn_box2.set_spacing(3)
        self.btn_box2.pack_end(self.ok_button) 
        #self.btn_box.pack_start(self.apply_button)
        self.btn_box2.pack_end(self.cancel_button)
        
        
        self.vbox.pack_start(self.btn_box)

        self.notebook.set_border_width(1)
        self.vbox.set_border_width(12)

        self.hpaned.pack1(self.vbox, True, False)


    def clicked_ok(self):
        self.save_preference()
        self.destroy()

    def save_preference(self):
        """"""        
        self.save_peer()
        self.save_general()
        self.save_tests()
        self.save_updates()
        self.save_advanced()

    def load_preference(self):
        """"""
        self.load_peer()
        self.load_general()
        self.load_tests()
        self.load_updates()
        self.load_advanced()

    def save_peer(self):
        """"""
        user_email = self.peer_page.email_entry.get_text()
        if user_email != '': # and is valid
            theApp.peer_info.Email = user_email

        aggregator_url = self.peer_page.cloudagg_entry.get_text()
        theApp.aggregator.base_url = aggregator_url
        if aggregator_url != None and aggregator_url != "":
            g_config.set('network', 'aggregator_url', aggregator_url)
            g_db_helper.set_value('config','aggregator_url', aggregator_url)
        
        longitude_text = self.peer_page.longitude_entry.get_text()
        if longitude_text != "":
            g_config.set('Location', 'longitude', str(longitude_text))
        
        latitude_text = self.peer_page.latitude_entry.get_text()
        if latitude_text != "":
            g_config.set('Location', 'latitude', str(latitude_text))        
    
    def save_general(self):
        """"""
        startup_on_boot = self.general_page.startup_check.get_active()
        self.general_page.startup_set(startup_on_boot)
        g_config.set('application', 'startup_on_boot', str(startup_on_boot))

        disable_notifications = self.general_page.notification_check.get_active()
        g_config.set('application', 'disable_notifications', str(disable_notifications))
        
        auto_login = self.general_page.login_ckeck.get_active()        
        g_config.set('application', 'auto_login_swittch', str(auto_login))
    
    def load_general(self):
        """"""
        startup_on_boot = g_config.getboolean('application', 'startup_on_boot')
        if startup_on_boot:
            self.general_page.startup_check.set_active(True)
        else:
            self.general_page.startup_check.set_active(False)
        
        disable_notifications = g_config.getboolean('application', 'disable_notifications')
        if disable_notifications:
            self.general_page.notification_check.set_active(True)
        else:
            self.general_page.notification_check.set_active(False)
        
        #auto_login = g_config.getboolean('application', 'auto_login_swittch')
        auto_login = False
        if auto_login:
            self.general_page.login_ckeck.set_active(True)
        else:
            self.general_page.login_ckeck.set_active(False)        
    
    def save_advanced(self):
        """"""
        task_assign_text = self.advanced_page.task_assign_entry.get_text()
        if task_assign_text != "":
             g_config.set('Timer', 'task_assign_timer', str(task_assign_text))
             theApp.task_assgin_lc.stop()
             theApp.task_assgin_lc.start(float(task_assign_text))
             
        task_scheduler_text = self.advanced_page.task_scheduler_entry.get_text()
        if task_scheduler_text != "":
             g_config.set('Timer', 'task_scheduler_timer', str(task_scheduler_text))
             theApp.task_run_lc.stop()
             theApp.task_run_lc.start(float(task_scheduler_text))
             
        report_uploade_text = self.advanced_page.report_uploader_entry.get_text()
        if report_uploade_text != "":
             g_config.set('Timer', 'send_report_timer', str(report_uploade_text))
             theApp.report_proc_lc.stop()
             theApp.report_proc_lc.start(float(report_uploade_text))
             
        test_fetch_text = self.advanced_page.test_fetch_entry.get_text()
        if test_fetch_text != "":
             g_config.set('Timer', 'test_fetch_timer', str(test_fetch_text))
             theApp.test_sets_fetch_lc.stop()
             theApp.test_sets_fetch_lc.start(float(test_fetch_text))     
             
        language_text  = self.advanced_page.language_entry.get_active_text()
        if language_text != "" and language_text != None :
            g_config.set('Language', 'current_language',language_text)   
                 
    def load_advanced(self):
        """"""
        task_assign_text = g_config.get("Timer","task_assign_timer")
        self.advanced_page.task_assign_entry.set_text(task_assign_text)

        task_scheduler_text = g_config.get("Timer","task_scheduler_timer")
        self.advanced_page.task_scheduler_entry.set_text(task_scheduler_text)        

        report_uploade_text = g_config.get("Timer","send_report_timer")
        self.advanced_page.report_uploader_entry.set_text(report_uploade_text)        
        
        test_fetch_text = g_config.get("Timer","test_fetch_timer")
        self.advanced_page.test_fetch_entry.set_text(test_fetch_text)   
    
        language_text = g_config.get("Language","current_language")
        #self.advanced_page.language_entry.set_text_column(1)
        
    def load_peer(self):
        """"""
        self.peer_page.peerid_label2.set_text(str(theApp.peer_info.ID))
        self.peer_page.email_entry.set_text(theApp.peer_info.Email)
        self.peer_page.cloudagg_entry.set_text(theApp.aggregator.base_url)
        self.peer_page.test_version_label2.set_text(str(theApp.test_sets.current_test_version))


        longitude_text  = g_config.get('Location', 'longitude')
        latitude_text  = g_config.get('Location', 'latitude')
                
        self.peer_page.longitude_entry.set_text(longitude_text)
        self.peer_page.latitude_entry.set_text(latitude_text)
                
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
   
    def help_direct(self):
        """"""
        import webbrowser
        url = "http://www.openmonitor.org/faq/"
        webbrowser.open(url)             

if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = PreferenceWindow()
    #wnd.set_size_request(520, 440)
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()