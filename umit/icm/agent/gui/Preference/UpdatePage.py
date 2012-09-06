#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Tianwei Liu <liutianweidlut@gmail.com>
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


##########################################
#Software update Page in Preference Window
class UpdatePage(HIGVBox):
    """"""
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self.__load_list()
        self.__connect_widgets()
        self.__init_db_text()
        
    def __create_widgets(self):
        """"""
        
        self.update_switch_hbox = HIGHBox()
        self.update_settings_hbox = HIGHBox()
        self.update_db_hbox = HIGHBox()

        self.update_switch_section = HIGSectionLabel(_("Update News Detect"))        
        self.update_switch_table = HIGTable()
        self.update_settings_section = HIGSectionLabel(_("Update Settings"))        
        self.update_settings_table = HIGTable()  
        self.update_db_section = HIGSectionLabel(_("Update Database"))        
        self.update_db_table = HIGTable()
        
        self.update_check = gtk.CheckButton(_("Automatically update"))
        self.update_switch_check = gtk.CheckButton(_("Software Update Detect Switch"))
        self.update_times_label = HIGEntryLabel(_("Auto detect update news"))
        self.update_method_label = HIGEntryLabel(_("Update method"))       
        
        self.update_time_store = gtk.ListStore(str)
        self.update_time_entry = gtk.ComboBoxEntry(self.update_time_store, 0)
        self.update_method_store = gtk.ListStore(str)
        self.update_method_entry = gtk.ComboBoxEntry(self.update_method_store, 0)  
        
        self.update_db_label =  HIGEntryLabel()
        self.update_db_clear_button = gtk.Button(_("Clear Update Information")) 
         
    def __pack_widgets(self):
        """"""
        self.set_border_width(12) 
        
        self._pack_noexpand_nofill(self.update_switch_section)
        self._pack_noexpand_nofill(self.update_switch_hbox)
        self._pack_noexpand_nofill(hig_box_space_holder())
        self._pack_noexpand_nofill(self.update_settings_section)
        self._pack_noexpand_nofill(self.update_settings_hbox)
        self._pack_noexpand_nofill(self.update_db_section)
        self._pack_noexpand_nofill(self.update_db_hbox)        
        
        
        self.update_switch_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.update_switch_hbox._pack_expand_fill(self.update_switch_table)
        self.update_settings_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.update_settings_hbox._pack_expand_fill(self.update_settings_table)
        self.update_db_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.update_db_hbox._pack_expand_fill(self.update_db_table)
        
        self.update_switch_table.attach_label(self.update_check, 0, 2, 0, 1)
        self.update_switch_table.attach_label(self.update_switch_check, 0, 2, 1, 2)
        self.update_settings_table.attach_label(self.update_times_label, 0, 1, 0, 1)
        self.update_settings_table.attach_entry(self.update_time_entry, 1, 2, 0, 1)   
        self.update_settings_table.attach_label(self.update_method_label, 0, 1, 1, 2)
        self.update_settings_table.attach_entry(self.update_method_entry, 1, 2, 1, 2) 
        
        self.update_db_table.attach_label(self.update_db_label, 1, 3, 0, 1)
        self.update_db_table.attach(self.update_db_clear_button, 0, 1, 0, 1)
        
    
    def __init_db_text(self):
        """"""
        rs = g_db_helper.select("select * from updates")
        count = len(rs)
        self.update_db_label.set_text(str(_("%d records in update database now."%(count))))        
    
    def __connect_widgets(self):
        """"""
        self.update_check.connect('toggled',lambda w:self.__change_widgets_status()) 
        self.update_db_clear_button.connect("clicked", lambda w:self.__clear_update_db())
    
    def __clear_update_db(self):
        """"""
        g_db_helper.execute("delete from updates")
        g_db_helper.commit()
        self.update_db_label.set_text(str(_("Clear software update database!")))
    
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
         