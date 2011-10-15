#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
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
import webbrowser

from higwidgets.higdialogs import HIGDialog
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGTextEntry, HIGPasswordEntry
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, HIGVBox, hig_box_space_holder
from higwidgets.higbuttons import HIGStockButton

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.gui.Registration import RegistrationDialog

########################################################################
class LoginDialog(HIGDialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, title=_('Login')):
        """Constructor"""
        HIGDialog.__init__(self, title=title, flags=gtk.DIALOG_MODAL,
                           buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        #self.set_size_request(400, 200)
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets()

    def _create_widgets(self):
        self.username_label = HIGLabel(_("Username"))
        self.username_entry = HIGTextEntry()

        self.password_label = HIGLabel(_("Password"))
        self.password_entry = HIGPasswordEntry()

        self.login_icon = gtk.Image()
        self.login_text = gtk.Label(_("Log into your ICM agent."))

        self.register_button = HIGStockButton(gtk.STOCK_DIALOG_INFO,
                                       _("Register"))

        #hbox = gtk.HBox(False)
        #box.pack_start(hbox, True, True, 0)
        self.forgot_password_label = \
            gtk.Label(_("<span foreground='blue' underline='low'>" \
                        "Forgot password?</span>"))
        self.forgot_password_label.set_use_markup(True)
        self.forgot_password = gtk.Button()
        self.forgot_password.add(self.forgot_password_label)
        self.forgot_password.set_relief(gtk.RELIEF_NONE)

        self.checkbtn = gtk.CheckButton(_("Save login credentials"))
        self.hbox = HIGHBox()
        self.table = HIGTable()
        self.action_area.set_homogeneous(False)

    def _pack_widgets(self):
        self.login_icon.set_from_stock(gtk.STOCK_DIALOG_INFO,
            gtk.ICON_SIZE_DIALOG)
        self.login_icon.set_padding(10, 0)
        self.login_text.set_line_wrap(True)

        self.hbox.set_border_width(12)
        self.hbox._pack_noexpand_nofill(self.login_icon)
        self.hbox._pack_expand_fill(self.login_text)

        self.vbox.pack_start(self.hbox, False, False)
        self.table.attach_label(self.username_label, 0, 1, 0, 1)
        self.table.attach_entry(self.username_entry, 1, 2, 0, 1)
        self.table.attach_label(self.password_label, 0, 1, 1, 2)
        self.table.attach_entry(self.password_entry, 1, 2, 1, 2)
        self.vbox.pack_start(self.table)
        self.vbox.pack_start(self.checkbtn)

        spaceholder = hig_box_space_holder()
        self.action_area.pack_end(spaceholder)
        self.action_area.pack_end(self.register_button)
        self.action_area.pack_end(self.forgot_password)
        self.action_area.reorder_child(self.register_button, 0)
        self.action_area.reorder_child(self.forgot_password, 1)
        self.action_area.reorder_child(spaceholder, 2)

    def _connect_widgets(self):
        self.connect('response', self.check_response)
        self.register_button.connect('clicked', self._register)
        self.forgot_password.connect('clicked', self._forgot_password)

    def _register(self, widget):
        #registration_form = RegistrationDialog()
        #registration_form.show_all()
        aggregator_url = g_db_helper.get_value('aggregator_url')
        webbrowser.open(aggregator_url + "/accounts/register/")

    def _forgot_password(self, widget):
        webbrowser.open(aggregator_url + "/accounts/register/")

    def check_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_ACCEPT: # clicked on Ok btn
            self._login1()
        elif response_id in (gtk.RESPONSE_DELETE_EVENT, gtk.RESPONSE_CANCEL,
                gtk.RESPONSE_NONE):
            self.destroy()
            theApp.gtk_main.login_dlg = None

    def _login1(self):
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()
        if not theApp.peer_info.registered:
            d = theApp.aggregator.test_register()
            #d = theApp.aggregator.register(username, password)
            d.addCallback(self._login2)
        else:
            d = theApp.aggregator.login(username, password)

    def _login2(self, data):
        if data is not None:
            username = self.username_entry.get_text()
            password = self.password_entry.get_text()
            d = theApp.aggregator.login(username, password)

    def _login_response(self, data):
        if data is not None:
            if self.save_login_checkbtn.get_active():
                g_db_helper.set_value('login_saved', True)
        theApp.logged_in()


if __name__ == "__main__":
    dialog = LoginDialog()
    dialog.connect("delete-event", lambda x, y: gtk.main_quit())
    dialog.show_all()

    gtk.main()


