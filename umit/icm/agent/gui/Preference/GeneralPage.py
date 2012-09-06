#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id
from umit.icm.agent.test import ALL_TESTS
from umit.icm.agent.utils.Startup import StartUP

from twisted.internet import reactor

###################################################
#Preference basic setting Page in Preference Window
class GeneralPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self.__information_load()

    def __create_widgets(self):
        
        
        self.general_hbox = HIGHBox()    
        self.version_hbox = HIGHBox()
        
        ################
        #Version Section
        self.version_section = HIGSectionLabel(_("Version"))
        self.version_table = HIGTable()
        self.version_label  = HIGEntryLabel(_("Software Version:"))
        self.version2_label = HIGEntryLabel()
        self.testver_label  = HIGEntryLabel(_("Service Test Version:"))
        self.testver2_label = HIGEntryLabel()
        self.attribute_label = HIGEntryLabel(_("Agent Attribute:"))
        self.attribute2_label = HIGEntryLabel()
            
        ################
        #General Section
        self.general_section = HIGSectionLabel(_("General"))
        self.general_table = HIGTable()
                
        self.startup_check = gtk.CheckButton(_("Startup OpenMonitor on system startup"))
        self.notification_check = gtk.CheckButton(_("Show Desktop Notifications"))
        self.login_ckeck = gtk.CheckButton(_("Enable Auto login"))        
        
        
    def __pack_widgets(self):
        """"""
        self.set_border_width(12)
        
        self._pack_noexpand_nofill(self.version_section)
        self._pack_noexpand_nofill(self.version_hbox)
        

        self._pack_noexpand_nofill(self.general_section)
        self._pack_noexpand_nofill(self.general_hbox)
        
        self.version_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.version_hbox._pack_expand_fill(self.version_table)        
                
        self.general_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.general_hbox._pack_expand_fill(self.general_table)
        
        self.version_table.attach_label(self.version_label, 0, 2, 0, 1)
        self.version_table.attach_label(self.version2_label, 2, 4, 0, 1)
        self.version_table.attach_label(self.testver_label, 0, 2, 1, 2)  
        self.version_table.attach_label(self.testver2_label, 2, 4, 1, 2)
        self.version_table.attach_label(self.attribute_label, 0, 2, 2, 3)
        self.version_table.attach_label(self.attribute2_label, 2, 4, 2, 3)       
        
        self.general_table.attach_label(self.startup_check, 0, 2, 2, 3)
        self.general_table.attach_label(self.notification_check, 0, 3, 3, 4)
        self.general_table.attach_label(self.login_ckeck, 0, 4, 4, 5)
                                        
    def startup_set(self,is_start_up=True):
        """"""
        start = StartUP()
        if is_start_up:
            start.set_startup()
        else:
            start.clear_startup()        
        
    def __information_load(self):
        """
        """
        from umit.icm.agent.Version import VERSION
        from umit.icm.agent.test import TEST_PACKAGE_VERSION
        from umit.icm.agent.Global import *
        
        self.version2_label.set_text(str(VERSION))
        self.testver2_label.set_text(str(TEST_PACKAGE_VERSION))
        
        peer_attribute = g_db_helper.get_information(key='peer',default="Desktop Agent")
        
        self.attribute2_label.set_text(peer_attribute)
        
        
        
        
        
        
        
    

   