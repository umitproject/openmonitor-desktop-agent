#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Tianwei Liu <liutianweidlut@gmail.com>
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
import os

from higwidgets.higwindows import HIGWindow
from higwidgets.higdialogs import HIGDialog
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder
from higwidgets.higbuttons import HIGStockButton,HIGButton

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.BasePaths import IMAGES_DIR

test_software_text=[
                    ('OpenMonitor','V0.1a','2011-9-1'),
                    ('icm-agent','V0.1b','2011-11-20'),
                    ('icm-agent LTS','V1.0','2012-5-21')] 

class SoftwareUpdateDialog(HIGWindow):
    """"""
    def __init__(self):
        """Constructor"""
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_("Open Monitor Software Update Manager"))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_size_request(480,560)
        self.set_keep_above(True)
        self.set_border_width(10)
        
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets() 

    def _create_widgets(self):
        """"""        
        #vbox
        self.all_Hbox = HIGVBox()
        self.soft_update_info_box = HIGHBox()
        self.soft_update_list_box = HIGHBox()
        self.check_btn_box = HIGHBox()
        self.soft_update_detail_box = HIGHBox()
            
        #software update information title 
        self.update_icon = gtk.Image()
        self.update_icon.set_from_file(os.path.join(IMAGES_DIR,'software_update.png'))
        self.version_information_label = HIGLabel(_("The newest open monitor in your computer!"))
        self.latest_time_information_label = HIGLabel(_("The lastest update time is ***"))
        self.soft_update_table = HIGTable()
        
        self.soft_info_vbox = HIGVBox()
        self.soft_text_hbox = HIGHBox()
        self.soft_text_hbox._pack_expand_fill( self.version_information_label)
        self.soft_text_hbox._pack_expand_fill( self.latest_time_information_label)
        self.soft_info_vbox._pack_noexpand_nofill(self.update_icon)
        self.soft_info_vbox._pack_expand_fill(self.soft_text_hbox)
        self.soft_update_info_box._pack_expand_fill(self.soft_info_vbox)
        
        #software list
        self.column_names = ['Name','Version','Date']
        
        self.vbox_list = gtk.VBox(False,8)
        self.scroll_window_vbox = gtk.ScrolledWindow()
        self.scroll_window_vbox.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scroll_window_vbox.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.vbox_list.pack_start(self.scroll_window_vbox,True,True,0)
        self.store = self._create_model()
        self.treeview = gtk.TreeView(self.store)
        self.treeview.connect('row-activated',self._on_activated)
        self.treeview.set_rules_hint(True)
        self.scroll_window_vbox.add(self.treeview)
        
        self._create_colums()
        self.statusbar = gtk.Statusbar()
        
        self.vbox_list.pack_start(self.statusbar,False,False,0)
        
        
    def _pack_widgets(self):
        """"""
        self.all_Hbox._pack_noexpand_nofill(self.soft_update_info_box)
        self.all_Hbox._pack_noexpand_nofill(self.soft_update_list_box)   
        self.all_Hbox._pack_noexpand_nofill(self.check_btn_box)
        self.all_Hbox._pack_noexpand_nofill(self.soft_update_detail_box)
        
        self.soft_update_info_box._pack_noexpand_nofill(hig_box_space_holder())
        self.soft_update_info_box._pack_expand_fill(self.soft_update_table)
        self.soft_update_list_box._pack_noexpand_nofill(hig_box_space_holder())        
        self.soft_update_list_box._pack_expand_fill(self.vbox_list)
                
        self.soft_update_table.attach_label(self.update_icon,0,2,0,2)
        self.soft_update_table.attach_label(self.version_information_label,2,4,0,1)
        self.soft_update_table.attach_label(self.latest_time_information_label,2,4,1,2)
        
        self.add(self.all_Hbox)

    def _connect_widgets(self):
        """"""
        pass
        
    def _create_model(self):
        """"""
        store = gtk.ListStore(str,str,str)
        for t in test_software_text:
            store.append([t[0],t[1],t[2]])
        return store
    
    def _create_colums(self):
        """"""
        for i in range(0,len(self.column_names)):
            rendererText = gtk.CellRendererText()
            column = gtk.TreeViewColumn(self.column_names[i],rendererText)
            column.set_sort_column_id(i)
            self.treeview.append_column(column)
    
    def _on_activated(self):
        """"""
        pass
    
    def _loadupdate(self):
        """"""
        pass
        
    def _auto_update(self):
        """"""
        pass
    def _manually_update(self):
        """"""
        pass
if __name__ == "__main__":
    dialog =  SoftwareUpdateDialog()
    dialog.connect("delete-event", lambda x,y:gtk.main_quit())
    dialog.show_all()
    
    gtk.main()         
        
 