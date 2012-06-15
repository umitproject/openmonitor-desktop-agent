#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:    Alan Wang <wzj401@gmail.com>
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
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGTextEntry, HIGPasswordEntry

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id
from umit.icm.agent.test import ALL_TESTS
from umit.icm.agent.utils.Startup import StartUP

from twisted.internet import reactor

###################################################
#Peer Information Page in Preference Window
class PeerInfoPage(HIGVBox):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        
    def __create_widgets(self):
        """"""
        self.peerinfo_hbox      = HIGHBox()
        self.cloudagg_hbox      = HIGHBox()
        self.superpeers_hbox    = HIGHBox()
        self.pref_location_hbox = HIGHBox()

        self.peerinfo_section = HIGSectionLabel(_("Peer Info"))
        self.peerinfo_table = HIGTable()
        
        self.pref_location_section = HIGSectionLabel(_("Preferred Locations"))
        self.pref_location_table = HIGTable()
        
        self.cloudagg_section = HIGSectionLabel(_("Cloud Aggregator"))
        self.cloudagg_table = HIGTable()
        self.cloudagg_subhbox = HIGHBox()
        self.superpeers_section = HIGSectionLabel(_("Super Peers"))
        self.superpeers_table = HIGTable()

        self.peerid_label = HIGEntryLabel(_("Peer ID:"))
        self.email_label = HIGEntryLabel(_("Email Address:")) 
        self.test_version_label = HIGEntryLabel(_("Test Sets Version:")) 
        self.peerid_label2 = HIGEntryLabel()
        self.email_entry = gtk.Entry()
        self.test_version_label2 = HIGEntryLabel()        

        self.longitude_label = HIGLabel(_("longitude:"))
        self.longitude_entry = gtk.Entry()
        self.latitude_label = HIGLabel(_("latitude:"))
        self.latitude_entry = gtk.Entry()                  

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
        self.superpeers_button1.connect('clicked',lambda w:self.add_superpeer())
                        
        self.superpeers_button2 = HIGButton(_("Show all"))
        self.superpeers_button2.connect('clicked', lambda w:
                                        self.show_super_peer_list_window())

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.peerinfo_section)
        self._pack_noexpand_nofill(self.peerinfo_hbox)
        self._pack_noexpand_nofill(self.pref_location_section)
        self._pack_noexpand_nofill(self.pref_location_hbox)
        self._pack_noexpand_nofill(self.cloudagg_section)
        self._pack_noexpand_nofill(self.cloudagg_hbox)
        self._pack_noexpand_nofill(self.superpeers_section)
        self._pack_noexpand_nofill(self.superpeers_hbox)

        self.peerinfo_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.peerinfo_hbox._pack_expand_fill(self.peerinfo_table)
        self.pref_location_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.pref_location_hbox._pack_expand_fill(self.pref_location_table)        
        self.cloudagg_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.cloudagg_hbox._pack_expand_fill(self.cloudagg_table)
        self.superpeers_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.superpeers_hbox._pack_expand_fill(self.superpeers_table)

        self.peerinfo_table.attach_label(self.peerid_label, 0, 1, 0, 1)
        self.peerinfo_table.attach_label(self.email_label, 0, 1, 2, 3)

        self.peerinfo_table.attach_label(self.test_version_label, 0, 1, 1, 2)
        self.peerinfo_table.attach_label(self.test_version_label2, 1, 2, 1, 2)

        self.peerinfo_table.attach_label(self.peerid_label2, 1, 2, 0, 1)
        self.peerinfo_table.attach_entry(self.email_entry, 1, 2, 2, 3)

        self.pref_location_table.attach(self.longitude_label,0,1,0,1)
        self.pref_location_table.attach(self.longitude_entry,1,2,0,1)
        self.pref_location_table.attach(self.latitude_label,2,3,0,1)
        self.pref_location_table.attach(self.latitude_entry,3,4,0,1)
        
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
        

    def add_superpeer(self):
        if self.superpeers_entry:
            return
        
            
    def show_super_peer_list_window(self):
        from umit.icm.agent.gui.SuperPeerSetting import SuperPeerListWindow,SuperPeersBox
        wnd = SuperPeerListWindow()
        wnd.show_all()
    





























