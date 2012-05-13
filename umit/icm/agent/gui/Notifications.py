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
"""
notifications about new software released, system information etc
"""
import gtk
import gobject
import os

from higwidgets.higboxes import hig_box_space_holder
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.logger import g_logger
from umit.icm.agent.I18N import _

new_release_mode = 1
report_mode = 2

class Notifications(gtk.Window):
    def __init__(self,mode=new_release_mode,text=None,timeout=10000):
        gtk.Window.__init__(self,gtk.WINDOW_POPUP)
        
        self.mode = mode
        self.text = text
        self.timeout = timeout
        
        self.screen_x = 0
        self.screen_y = 0
        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connect_widgets()
        
        g_logger.info(_("new desktop agent version released! "))
        
    def __create_widgets(self):
        """"""
        if self.mode == new_release_mode:
            self.image = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_DIR,'new_release.png'))
            self.pixmap, self.mask = self.image.render_pixmap_and_mask()
            width,height = self.pixmap.get_size()
        else:
            width = 200
            height = 200
            self.pixmap = None
        
        self.set_events(self.get_events() | gtk.gdk.BUTTON_PRESS_MASK)
        
        screen = gtk.gdk.Screen()
        self.screen_x = gtk.gdk.Screen.get_width(screen)
        self.screen_y = gtk.gdk.Screen.get_height(screen) 
                
        self.move(self.screen_x - width- 30 ,30) 
        self.set_app_paintable(True)
        self.set_size_request(width,height)
        self.set_resizable(False)
        self.realize()
        
        self.fixed = gtk.Fixed()
        self.fixed.set_size_request(width,height)
        self.vbox = gtk.VBox()
        self.hbox = gtk.HBox()
        
        self.label = gtk.Label(self.text)
            
    def __pack_widgets(self):
        """"""
        self.hbox.pack_end(self.label,False,False)
        self.hbox.pack_end(hig_box_space_holder(),True,False)
        
        self.vbox.pack_start(self.hbox,True,False)
        
        self.fixed.put(self.vbox,0,0)
        self.add(self.fixed)
        self.set_background(self, None, self.mask, self.pixmap)
        self.shape_combine_mask(self.mask,0,0)
        self.show_all()
        
        gobject.timeout_add(self.timeout,self.destroy)
    
    def __connect_widgets(self):
        """"""
        self.connect("expose-event",self.set_background,self.mask,self.pixmap)
        self.connect("delete_event",self.destory)
        if self.mode == new_release_mode:
            self.connect("button_press_event",self._navigator_to_update)
        else:
            self.connect("button_press_event",self.destory)            
            
    def _navigator_to_update(self, widget, event, data=None):
        """"""
        theApp.gtk_main.show_software_update()
        self.destory()
    
    def destory(self):
        """"""
        gtk.Window.destroy(self)
        return False

    def set_background(self, widget, event, mask, pixmap):
        """"""
        if self.window is not None:
            self.window.set_back_pixmap(pixmap, False)
        else:
            gobject.idle_add(self.set_bg, widget, event, mask, pixmap)          
        
if __name__ == "__main__":
    t = Notifications(mode=new_release_mode,text="test",timeout=3000)
    gtk.main()
    
    