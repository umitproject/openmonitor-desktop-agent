#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:    Tianwei Liu <liutianweidlut@gmail.com>
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

from twisted.internet import reactor

Language_store = {
                  "English(Default)":1,
                  "中文(Chinese)":2,
                  "Portuguese(Portuguese)":3,
                  "日文(Japanese)":4,
                  "System Language":5,
                 }

###################################################
#Peer Information Page in Preference Window
class AdvancedPage(HIGVBox):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self._load_list_()
        
    def __create_widgets(self):
        """"""
        self.timer_hbox = HIGHBox()
        self.timer_section = HIGSectionLabel(_("Timeout Setting (seconds)"))
        self.timer_table = HIGTable()
        self.other_hbox = HIGHBox()
        self.other_section = HIGSectionLabel(_("Others"))
        self.other_table = HIGTable()
        
        self.task_assign_label      = HIGEntryLabel(_("Task Assign"))        
        self.task_scheduler_label   = HIGEntryLabel(_("Task Scheduler")) 
        self.report_uploader_label  = HIGEntryLabel(_("Report Uploader")) 
        self.test_fetch_label  = HIGEntryLabel(_("Test sets Fetch"))         

        
        self.task_assign_entry      = gtk.Entry()
        self.task_scheduler_entry   = gtk.Entry()
        self.report_uploader_entry  = gtk.Entry()
        self.test_fetch_entry       = gtk.Entry()    
        
        self.language_label = HIGEntryLabel(_("Language"))
        self.language_store = gtk.ListStore(str)
        self.language_entry = gtk.ComboBoxEntry(self.language_store,0)                    
        
    def __pack_widgets(self):
        self.set_border_width(12)
 
        self._pack_noexpand_nofill(self.timer_section)
        self._pack_noexpand_nofill(self.timer_hbox)  
        self._pack_noexpand_nofill(self.other_section)
        self._pack_noexpand_nofill(self.other_hbox)         
        
        self.timer_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.timer_hbox._pack_expand_fill(self.timer_table)   
        
        self.other_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.other_hbox._pack_expand_fill(self.other_table)     
        
        self.timer_table.attach_label(self.task_assign_label,0,1,0,1)             
        self.timer_table.attach_label(self.task_assign_entry,1,3,0,1)                   
        self.timer_table.attach_label(self.task_scheduler_label,0,1,1,2)             
        self.timer_table.attach_label(self.task_scheduler_entry,1,3,1,2)     
        self.timer_table.attach_label(self.report_uploader_label,0,1,2,3)             
        self.timer_table.attach_label(self.report_uploader_entry,1,3,2,3) 
        self.timer_table.attach_label(self.test_fetch_label,0,1,3,4)
        self.timer_table.attach_label(self.test_fetch_entry,1,3,3,4)

        self.other_table.attach_label(self.language_label,0,2,0,1)
        self.other_table.attach_label(self.language_entry,2,4,0,1)

    def _load_list_(self):
        """"""
        for s in Language_store.keys():
            self.language_store.append([s])
            
        #self.language_entry.set_model(self.language_store)
        #self.language_entry.set_text_column(1)
























