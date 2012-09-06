#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:    Paul Pei <paul.kdash@gmail.com>
#            Alan Wang <wzj401@gmail.com>
#            Tianwei Liu <liutianweidlut@gmail.com>
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

###################################################
#SuperPeer Settings Page in Preference Window
class  SuperPeerListWindow(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Super Peers List'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
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
        self.main_vbox.set_border_width(8)

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
        self.set_size_request(480, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("""\
<span size='12000'>Super Peers List: \n</span>""")

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
