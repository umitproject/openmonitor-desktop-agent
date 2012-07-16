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
import os

from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder
from umit.icm.agent.Version import PEER_ATTRIBUTE
from umit.icm.agent.gui.dashboard.timeline.TimeLine import TLHoder
from umit.icm.agent.BasePaths import *
from deps.higwidgets.higtables import HIGTable


class TimeLineGraphViewer(gtk.VBox):
    
    def __init__(self,dashboard = None,connector = None):
        """
        Load timeline for every tab in dashboard window
        """
        gtk.VBox.__init__(self)
        
        self.dashboard = dashboard
        self.connector = connector
        
        self.__create_widgets()
        self.__packed_widgets()
        self.__connected_widgets()
        
    def __create_widgets(self):
        """"""        
        #####
        #Box
        self.title_box = gtk.HBox()
        self.box = HIGVBox()
        
        self.timeline = TLHoder(self.dashboard,self.connector)
        self.timeline.show_all()
        
        #######
        #Title
        self.title = gtk.Label(
            "<span size='15000' weight='heavy'>\t\t\t\t Timeline Graph Area(%s) </span>"%(PEER_ATTRIBUTE))        
        self.title.set_use_markup(True)
        self.title.set_selectable(False)      
        
        #########
        #Type Pic
        if "desktop" in PEER_ATTRIBUTE.lower():
            peer_img_str = "normalpeer.png"
        else:
            peer_img_str = "superpeer.png"
            
        self.peer_img = gtk.Image()
        self.peer_img.set_from_file(os.path.join(IMAGES_DIR,peer_img_str))        
        
        
    def __packed_widgets(self):
        """"""
        self.box._pack_noexpand_nofill(self.title_box)
        self.box._pack_expand_fill(self.timeline)
        
        self.title_box.pack_end(self.peer_img)
        self.title_box.pack_end(self.title)
        

        
        self.add(self.box)
        
        self.show_all()
        
    def __connected_widgets(self):
        """"""
        pass
    

        
        
        
        
        
        
        
        
        
        
        
                
    
    
    