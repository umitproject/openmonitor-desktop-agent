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

from twisted.internet import reactor

from higwidgets import HIGWindow

from umit.icm.agent.I18N import _
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.gui.LoginDialog import LoginDialog
from umit.icm.agent.gui.PreferenceWindow import PreferenceWindow

class GtkMain(object):
    def __init__(self, *args, **kwargs):
        self.is_login = False
        self._create_widgets()

    def _create_widgets(self):
        self.tray_icon = gtk.StatusIcon()
        #
        self.tray_menu_logged_in = gtk.Menu()
        menu_item = gtk.MenuItem(_("ICM Webpage"))
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Dashboard"))
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Event List"))
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Logs"))
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        self.tray_menu_logged_in.append(menu_item)

        self.tray_menu_logged_in.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Preference"))
        menu_item.connect("activate", lambda w: self.show_preference())
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.MenuItem(_("About"))
        #menu_item.connect("activate", lambda w: gtk.main_quit())
        self.tray_menu_logged_in.append(menu_item)

        self.tray_menu_logged_in.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Logout"))
        menu_item.connect("activate", lambda w: self.logout())
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Exit"))
        menu_item.connect("activate", lambda w: reactor.stop())
        self.tray_menu_logged_in.append(menu_item)
        self.tray_menu_logged_in.show_all()
        ###
        self.tray_menu_logged_out = gtk.Menu()
        menu_item = gtk.MenuItem(_("Login"))
        menu_item.connect("activate", lambda w: self.login())
        self.tray_menu_logged_out.append(menu_item)

        self.tray_menu_logged_out.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Exit"))
        menu_item.connect("activate", lambda w: reactor.stop())
        self.tray_menu_logged_out.append(menu_item)
        self.tray_menu_logged_out.show_all()

        self.tray_menu = self.tray_menu_logged_out
        self.tray_icon.connect('popup-menu', self.show_menu, self.tray_menu)

        self.tray_icon.set_from_file(
                os.path.join(ICONS_DIR, "tray_icon_gray_32.ico"))

    def set_login_status(self, is_login):
        if self.is_login == is_login:
            return
        self.is_login = is_login
        if is_login:
            self.tray_menu.popdown()
            self.tray_menu = self.tray_menu_logged_in
            self.tray_icon.connect('popup-menu', self.show_menu, self.tray_menu)
            self.tray_icon.set_from_file(
                os.path.join(ICONS_DIR, "tray_icon_32.ico"))
        else:
            self.tray_menu.popdown()
            self.tray_menu = self.tray_menu_logged_out
            self.tray_icon.connect('popup-menu', self.show_menu, self.tray_menu)
            self.tray_icon.set_from_file(
                os.path.join(ICONS_DIR, "tray_icon_gray_32.ico"))

    def show_menu(self, status_icon, button, activate_time, menu):
        menu.popup(None, None, None, button, activate_time, status_icon)

    def show_preference(self):
        wnd = PreferenceWindow()
        wnd.show_all()
        #w.set_size_request(520, 440)
        #w.show_all()

    def show_login(self):
        login_dlg = LoginDialog()
        login_dlg.show_all()

    def login(self):
        self.show_login()

    def logout(self):
        self.set_login_status(False)


if __name__ == "__main__":
    #splash = gtk.Window()
    #splash.set_decorated(False)
    #splash.show()
    #gobject.timeout_add(3000, splash.hide) # 3*1000 miliseconds

    main = GtkMain()
    #main.show_all()
    gtk.main()

