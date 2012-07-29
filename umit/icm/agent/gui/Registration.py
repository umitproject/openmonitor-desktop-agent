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

from higwidgets.higdialogs import HIGDialog
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGPasswordEntry
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, HIGVBox

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *

from umit.icm.agent.Application import theApp


class RegistrationDialog(HIGDialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, title=_('Registration')):
        """Constructor"""
        HIGDialog.__init__(self, title=title,
                           buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self._create_widgets()
        self._pack_widgets()

        # Register callbacks
        self.connect("response", self.check_response)

    def _create_widgets(self):
        self.username_label = HIGLabel(_("Username"))
        self.username_entry = gtk.Entry()

        self.password_label = HIGLabel(_("Password"))
        self.password_entry = HIGPasswordEntry()

        self.retype_password_label = HIGLabel(_("Retype password"))
        self.retype_password_entry = HIGPasswordEntry()

        self.registration_icon = gtk.Image()
        self.registration_text = gtk.Label(_("If you don't have an ICM account,"
                "please register a new account."))

        self.hbox = HIGHBox()
        self.table = HIGTable()

    def _pack_widgets(self):
        self.registration_icon.set_from_stock(gtk.STOCK_DIALOG_INFO,
            gtk.ICON_SIZE_DIALOG)
        self.registration_icon.set_padding(10, 0)
        self.registration_text.set_line_wrap(True)

        self.hbox.set_border_width(12)
        self.hbox._pack_noexpand_nofill(self.registration_icon)
        self.hbox._pack_expand_fill(self.registration_text)

        self.vbox.pack_start(self.hbox, False, False)
        self.table.attach_label(self.username_label, 0, 1, 0, 1)
        self.table.attach_entry(self.username_entry, 1, 2, 0, 1)
        self.table.attach_label(self.password_label, 0, 1, 1, 2)
        self.table.attach_entry(self.password_entry, 1, 2, 1, 2)
        self.table.attach_label(self.retype_password_label, 0, 1, 2, 3)
        self.table.attach_entry(self.retype_password_entry, 1, 2, 2, 3)
        self.vbox.pack_start(self.table)

    def check_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_ACCEPT: # clicked on Ok btn
            self.register()
        elif response_id in (gtk.RESPONSE_DELETE_EVENT, gtk.RESPONSE_CANCEL,
                gtk.RESPONSE_NONE):
            self.destroy()

    def register(self):
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()
        theApp.aggregator.register(username, password)

if __name__ == "__main__":
    dialog = RegistrationDialog()
    dialog.connect("delete-event", lambda x, y: gtk.main_quit())
    dialog.show_all()

    gtk.main()


