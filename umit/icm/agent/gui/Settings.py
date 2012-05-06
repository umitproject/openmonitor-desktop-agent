#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
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
from deps.higwidgets.higbuttons import HIGStockButton

class SettingsDialog(HIGDialog):
    """"""
    def __init__(self,title=_('Settings')):
        """Constructor"""
        HIGDialog.__init__(self, title=title, flags=gtk.DIALOG_MODAL,
                           buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                    gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.set_keep_above(True)
        self.set_size_request(240,120)
        self.set_border_width(2)
        
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets() 
        
    def _create_widgets(self):
        """"""
        pass
    def _pack_widgets(self):
        """"""
        pass
    def _connect_widgets(self):
        """"""
        pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
