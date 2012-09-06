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

from deps.higwidgets.higdialogs import HIGDialog
from deps.higwidgets.higlabels import HIGLabel
from deps.higwidgets.higentries import HIGTextEntry
from deps.higwidgets.higtables import HIGTable
from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder
from deps.higwidgets.higbuttons import HIGStockButton,HIGButton

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp

class SettingsDialog(HIGDialog):
    """"""
    def __init__(self,title=_('Settings')):
        """Constructor"""
        HIGDialog.__init__(self, title=title, flags=gtk.DIALOG_MODAL)
        
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.set_keep_above(True)
        self.set_size_request(480,100)
        self.set_border_width(2)
        
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets() 
        self._load_settings()
    
    def _load_settings(self):
        """"""
        aggregator_url = g_config.get('network', 'aggregator_url')
        self.aggregator_ip_entry.set_text(aggregator_url)
          
    def _create_widgets(self):
        """"""
        self.web_listen_port_label = HIGLabel(_("Web Listen PORT"))
        self.web_listen_port_entry = HIGTextEntry()
        
        self.aggregator_ip_label = HIGLabel(_("Aggregator URL"))
        self.aggregator_ip_entry = HIGTextEntry()
        
        
        self.network_listen_port_label = HIGLabel(_("Peer Listen PORT"))
        self.network_listen_port_entry = HIGTextEntry()   
        
        self.save_button =  HIGButton(title = "Save")
        self.close_button = HIGButton(title = "Close")   
        
        self.hbox = HIGHBox(False,2)
        self.table = HIGTable(4,2,False)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(10)
        self.action_area.set_homogeneous(False)
        
    def _pack_widgets(self):
        """"""
        self.hbox.set_border_width(8)
        self.table.attach(self.aggregator_ip_label,0,1,0,1,gtk.FILL,gtk.FILL,0,0)
        self.table.attach(self.aggregator_ip_entry,1,4,0,1,gtk.FILL|gtk.EXPAND,gtk.FILL|gtk.EXPAND,0,0)
                     
        self.hbox._pack_expand_fill(self.table)
        self.vbox.pack_start(self.hbox, False, False) 
        
        self.action_area.pack_end(self.save_button)    
        self.action_area.reorder_child(self.save_button,0)                             
        self.action_area.pack_end(self.close_button)    
        self.action_area.reorder_child(self.close_button,1) 
        
    def _connect_widgets(self):
        """"""
        self.save_button.connect("clicked",lambda w: self._save_settings())
        self.close_button.connect("clicked",lambda w: self._close_settings())

    def _save_settings(self):
        """"""
        aggregator_url = self.aggregator_ip_entry.get_text()
        #print aggregator_url
        if aggregator_url != None and aggregator_url != "":
            #http address check
            if 'http://' not in aggregator_url:
                aggregator_url = "http://"+ aggregator_url
            aggregator_url = aggregator_url.rstrip('/')
            theApp.aggregator.base_url = aggregator_url
            g_config.set('network', 'aggregator_url', aggregator_url)
            g_db_helper.set_value('config','aggregator_url', aggregator_url)
            
        self.destroy()
    def _close_settings(self):
        """"""
        self.destroy()      
                        
                
if __name__ == "__main__":
    dialog = SettingsDialog()
    dialog.connect("delete-event", lambda x,y:gtk.main_quit())
    dialog.show_all()
    
    gtk.main()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
