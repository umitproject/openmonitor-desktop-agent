#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweaaidlut@gmail.com>     
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

"""
The login process is used to bind the agent with a certain account
"""

import gtk
import os
import webbrowser

from higwidgets.higdialogs import HIGDialog
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGTextEntry, HIGPasswordEntry
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, HIGVBox, hig_box_space_holder
from higwidgets.higbuttons import HIGStockButton
from higwidgets.higwindows import HIGWindow

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.gui.Registration import RegistrationDialog
from umit.icm.agent.gui.Settings import SettingsDialog
from umit.icm.agent.BasePaths import IMAGES_DIR

class LoginDialog(HIGDialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, title=_('Open Monitor 2012')):
        """Constructor"""
        HIGDialog.__init__(self, title=title, flags=gtk.DIALOG_MODAL,
                           buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.set_keep_above(True)
        self.set_size_request(480, 240)
        self.set_border_width(2)

        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets()

    def _create_widgets(self):
        
        #Username
        self.username_label = HIGLabel(_("Username"))
        self.username_entry = HIGTextEntry()
        self.username_entry.set_activates_default(True)

        #Password
        self.password_label = HIGLabel(_("Password"))
        self.password_entry = HIGPasswordEntry()
        self.password_entry.set_activates_default(True)
        
        #Logo
        self.logo_openmonitor = gtk.gdk.pixbuf_new_from_file\
                                    (os.path.join(IMAGES_DIR, 'logoOM.png'))
        self.logo_image = gtk.Image()
        self.logo_image.set_from_pixbuf(self.logo_openmonitor)
        #self.login_text = gtk.Label(_("Log into your ICM agent."))
        
        #Register
        #self.register_button = HIGStockButton(gtk.STOCK_DIALOG_INFO,_("Register"))
        self.register_label = \
            gtk.Label(_("<span foreground='blue'>" \
                        "Register id</span>"))
        self.register_label.set_use_markup(True)
        self.register_button = gtk.Button()
        self.register_button.add(self.register_label)
        self.register_button.set_relief(gtk.RELIEF_NONE)
        
        #Forget Password
        self.forgot_password_label = \
            gtk.Label(_("<span foreground='blue'>" \
                        "Forgot password?</span>"))
        self.forgot_password_label.set_use_markup(True)
        self.forgot_password = gtk.Button()
        self.forgot_password.add(self.forgot_password_label)
        self.forgot_password.set_relief(gtk.RELIEF_NONE)
        
        #Auto Login
        self.auto_login_checkbtn = gtk.CheckButton(_("Auto login"))
        
        #Settings
        self.settings_button = HIGStockButton(gtk.STOCK_DIALOG_INFO,_("settings"))
        
        #Container
        self.hbox = HIGHBox(False,2)
        self.table = HIGTable(8,4,False)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(10)
        self.action_area.set_homogeneous(False)
        
        #tab orders
        self.orders = [self.username_entry, self.password_entry, self.register_button, self.forgot_password]

    def _pack_widgets(self):

        self.hbox.set_border_width(8)
        
        self.table.set_focus_chain(self.orders)
        
        self.table.attach(self.logo_image,0,7,0,5,gtk.FILL,gtk.FILL,0,0)
        self.table.attach(self.username_label,0,1,5,6,gtk.FILL,gtk.FILL,0,0)
        self.table.attach(self.username_entry,1,5,5,6,gtk.FILL|gtk.EXPAND,gtk.FILL|gtk.EXPAND,0,0)
        self.table.attach(self.password_label,0,1,6,7,gtk.FILL,gtk.FILL,0,0)
        self.table.attach(self.password_entry,1,5,6,7,gtk.FILL|gtk.EXPAND,gtk.FILL|gtk.EXPAND,0,0) 
        self.table.attach(self.register_button,5,6,5,6,gtk.FILL,gtk.FILL,0,0)  
        self.table.attach(self.forgot_password,5,6,6,7,gtk.FILL,gtk.FILL,0,0)
        self.table.attach(self.auto_login_checkbtn,1,3,7,8,gtk.FILL,gtk.FILL,0,0)   
 
        self.hbox._pack_expand_fill(self.table)
        self.vbox.pack_start(self.hbox, False, False)                                  

        spaceholder1 = hig_box_space_holder()
        spaceholder2 = hig_box_space_holder()
        spaceholder3 = hig_box_space_holder()
        self.action_area.pack_end(spaceholder1)
        self.action_area.pack_end(spaceholder2)
        self.action_area.pack_end(spaceholder3)
        self.action_area.pack_end(self.settings_button)
        self.action_area.reorder_child(self.settings_button, 0)
        self.action_area.reorder_child(spaceholder1, 1)        
        self.action_area.reorder_child(spaceholder2, 2)
        self.action_area.reorder_child(spaceholder3, 2)
        
    def _connect_widgets(self):
        self.connect('response', self.check_response)
        self.register_button.connect('clicked', self._register)
        self.forgot_password.connect('clicked', self._forgot_password)
        self.settings_button.connect('clicked', self._settings)

    def _register(self, widget):
        #registration_form = RegistrationDialog()
        #registration_form.show_all()
        webbrowser.open(theApp.aggregator.base_url + "/accounts/register/")

    def _forgot_password(self, widget):
        webbrowser.open(theApp.aggregator.base_url + "/accounts/password/reset/")

    def check_response(self, widget, response_id):
        #There should collect the error information: help the user to check problem
        if response_id == gtk.RESPONSE_ACCEPT: # clicked on Ok btn
            username = self.username_entry.get_text()
            password = self.password_entry.get_text()
            save_login = self.auto_login_checkbtn.get_active()
            
            #Bug in this: If the user go to this window, the theApp.peer_info cannot is_registered
            
            #if not theApp.peer_info.is_registered:
            defer_ = theApp.login(username, password, save_login)   
            #    defer_ = theApp.register_agent(username, password)
            #    defer_.addCallback(
            #        lambda x: theApp.login(username, password, save_login))
            #else:
            #    defer_ = theApp.login(username, password, save_login)
            self.destroy()
            theApp.gtk_main.login_dlg = None
        elif response_id in (gtk.RESPONSE_DELETE_EVENT, gtk.RESPONSE_CANCEL,
                gtk.RESPONSE_NONE):
            self.destroy()
            theApp.gtk_main.login_dlg = None
            
    def _settings(self,widget):
        '''
        configure settings: Server IP/Port: popup a new window
        '''
        settings_form = SettingsDialog()
        settings_form.show_all()

if __name__ == "__main__":
    dialog = LoginDialog()
    dialog.connect("delete-event", lambda x, y: gtk.main_quit())
    dialog.show_all()
    
    gtk.main()
    


