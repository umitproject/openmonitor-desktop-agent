#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
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
import gobject
import os

from higwidgets import HIGWindow

#from umit.common.I18N import _
from umit.icm.agent.Basic import ICONS_DIR

class GtkMain(object):
    def __init__(self, *args, **kwargs):
        super(GtkMain, self).__init__(*args, **kwargs)
        
        # if it's first time running, register        
        
        tray_menu = gtk.Menu()

        menu_item = gtk.MenuItem("ICM Webpage")
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)

        menu_item = gtk.ImageMenuItem("Dashboard")
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)

        menu_item = gtk.ImageMenuItem("Event List")
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)

        menu_item = gtk.ImageMenuItem("Logs")
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)
        
        tray_menu.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem("Preference")
        menu_item.connect("activate", lambda w: self.prefernce_window.show())
        tray_menu.append(menu_item)

        menu_item = gtk.MenuItem("About")
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)
       
        tray_menu.append(gtk.SeparatorMenuItem())
        
        menu_item = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        menu_item.connect("activate", lambda w: gtk.main_quit())
        tray_menu.append(menu_item)
        tray_menu.show_all()
        
        tray_icon = gtk.status_icon_new_from_file(
            os.path.join(ICONS_DIR, "tray_icon_32.ico"))
        tray_icon.connect('popup-menu', self.show_menu, tray_menu)        
    
    def show_menu(self, status_icon, button, activate_time, menu):
        menu.popup(None, None, None, button, activate_time, status_icon)
    
        
        
if __name__ == "__main__":
    #splash = gtk.Window() 
    #splash.set_decorated(False)
    #splash.show()
    #gobject.timeout_add(3000, splash.hide) # 3*1000 miliseconds
    
    main = GtkMain()
    #main.show_all()
    gtk.main()
    
    