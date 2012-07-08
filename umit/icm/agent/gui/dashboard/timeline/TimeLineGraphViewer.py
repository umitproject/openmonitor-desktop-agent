#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
#          Tianwei Liu <liutainweidlut@gmail.com> 
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

"""
Time line Graph Viewer in Dashboard Window
"""

import pygtk
pygtk.require('2.0')
import gtk, gobject

from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder

from umit.icm.agent.gui.dashboard.timeline.TimeLine import TLHoder

class TimeLineGraphViewer(gtk.VBox):
    
    def __init__(self,Dashboard = None):
        """
        Load timeline for every tab in dashboard window
        """
        gtk.VBox.__init__(self)
        
        self.dashboard = Dashboard
        
        self.__create_widgets()
        self.__packed_widgets()
        self.__connected_widgets()
        
    def __create_widgets(self):
        """"""        
        self.box = HIGVBox()
        
        self.timeline = TLHoder(self.dashboard)
        self.timeline.show_all()
        
        self.test = gtk.Label("Timeline Graph Area")
        
        
    def __packed_widgets(self):
        """"""
        self.box._pack_noexpand_nofill(self.test)
        #self.box._pack_noexpand_nofill(hig_box_space_holder())
        self.box._pack_expand_fill(self.timeline)
        
        self.add(self.box)
        
        self.show_all()
        
    def __connected_widgets(self):
        """"""
        pass
    

        
        
        
        
        
        
        
        
        
        
        
                
    
    
    