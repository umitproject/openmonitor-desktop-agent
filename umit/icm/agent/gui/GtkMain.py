#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
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

from higwidgets.higwindows import HIGWindow

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.I18N import _
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Application import theApp

from umit.icm.agent.gui.Splash import Splash

appindicator = None
try:
    import appindicator
except ImportError:
    pass


class GtkMain(object):
    def __init__(self, *args, **kwargs):
        self.is_login = False
        self.login_dlg = None
        self._create_tray()
        self._create_widgets()
        self.set_login_status(False)

    def _create_tray(self):
        
        self.tray_menu_logged_in = gtk.Menu()
        self.tray_menu_logged_out = gtk.Menu()

        if appindicator is not None:
            g_logger.info("APP INDICATOR!")
            # This means we're running on unity and we need a different tray
            self.tray_indicator = appindicator.Indicator("open-monitor", # APP ID
                                     "internet-feed-reader", # ICON NAME
                                     appindicator.CATEGORY_APPLICATION_STATUS) # APP CATEGORY
            self.tray_indicator.set_status(appindicator.STATUS_ACTIVE)
            self.tray_indicator.set_attention_icon("indicator-messages-new")
            self.tray_indicator.set_menu(self.tray_menu_logged_out)

        else:
            self.tray_icon = gtk.StatusIcon()
            self.tray_icon.connect('popup-menu', self.show_menu)
            self.tray_icon.set_tooltip("Open Monitor")
            self.tray_icon.set_from_file(
                            os.path.join(ICONS_DIR, "tray_icon_gray_32.ico"))

    def _create_widgets(self):
        menu_item = gtk.MenuItem(_("ICM Webpage"))
        menu_item.connect("activate", lambda w: self.show_web_map())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Dashboard"))
        menu_item.connect("activate", lambda w: self.show_dashboard())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Event List"))
        menu_item.connect("activate", lambda w: self.show_event_list())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Logs"))
        menu_item.connect("activate", lambda w: self.show_logs())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        self.tray_menu_logged_in.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Preferences..."))
        menu_item.connect("activate", lambda w: self.show_preference())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.MenuItem(_("Software Update"))
        menu_item.connect("activate", lambda w: self.show_software_update())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)
        
        menu_item = gtk.MenuItem(_("About"))
        menu_item.connect("activate", lambda w: self.show_about())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        self.tray_menu_logged_in.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Logout"))
        menu_item.connect("activate", lambda w: theApp.logout())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)

        menu_item = gtk.ImageMenuItem(_("Exit"))
        menu_item.connect("activate", lambda w: reactor.stop())
        menu_item.show()
        self.tray_menu_logged_in.append(menu_item)
        self.tray_menu_logged_in.show_all()
        ###

        menu_item = gtk.MenuItem(_("Login"))
        menu_item.connect("activate", lambda w: self.show_login())
        menu_item.show()
        self.tray_menu_logged_out.append(menu_item)

        self.tray_menu_logged_out.append(gtk.SeparatorMenuItem())

        menu_item = gtk.MenuItem(_("Exit"))
        menu_item.connect("activate", lambda w: reactor.stop())
        menu_item.show()
        self.tray_menu_logged_out.append(menu_item)
        self.tray_menu_logged_out.show_all()

        self.tray_menu = self.tray_menu_logged_out

        # Show splash window
        splash = Splash(os.path.join(IMAGES_DIR, 'splash.png'))

    def set_login_status(self, is_login):
        if self.is_login == is_login:
            return
        self.is_login = is_login
        if is_login:
            if appindicator is not None:
                self.tray_indicator.set_menu(self.tray_menu_logged_in)
            else:
                self.tray_menu.popdown()
            self.tray_menu = self.tray_menu_logged_in

            if appindicator is None:
                self.tray_icon.set_from_file(
                    os.path.join(ICONS_DIR, "tray_icon_32.ico"))
        else:
            if appindicator is not None:
                self.tray_indicator.set_menu(self.tray_menu_logged_out)
            else:
                self.tray_menu.popdown()
            self.tray_menu = self.tray_menu_logged_out

            if appindicator is None:
                self.tray_icon.set_from_file(
                    os.path.join(ICONS_DIR, "tray_icon_gray_32.ico"))

    def show_menu(self, status_icon, button, activate_time):
        self.tray_menu.popup(None, None, None, button, activate_time,
                             status_icon)

    def hide_menu(self, *args, **kwargs):
        self.tray_menu.popdown()

    def show_web_map(self):
        import webbrowser, urlparse
        url = urlparse.urljoin(theApp.aggregator.base_url, '/map/')
        webbrowser.open(url)

    def show_dashboard(self):
        from umit.icm.agent.gui.Dashboard import DashboardWindow
        wnd = DashboardWindow()
        wnd.show_all_modify()

    def show_event_list(self):
        from umit.icm.agent.gui.Event import EventWindow
        wnd = EventWindow()
        wnd.show_all()

    def show_logs(self):
        from umit.icm.agent.gui.Logs import LogsWindow
        wnd = LogsWindow()
        wnd.show_all()

    def show_preference(self):
        from umit.icm.agent.gui.Preference import PreferenceWindow
        wnd = PreferenceWindow()
        wnd.show_all()
        
    def show_software_update(self):
        from umit.icm.agent.gui.SoftwareUpdate import SoftwareUpdateDialog
        self.update_dialog = SoftwareUpdateDialog()
        self.update_dialog.show_all()

    def show_about(self):
        from umit.icm.agent.gui.About import About
        about = About()
        about.show_all()

    def show_login(self):
        if not self.login_dlg:
            from umit.icm.agent.gui.Login import LoginDialog
            self.login_dlg = LoginDialog()
            self.login_dlg.show_all()

    def set_to_logging_in(self):
        if appindicator is None:
            self.tray_icon.set_tooltip("Logging in...")
        self.tray_menu.get_children()[0].set_sensitive(False)
        #self.tray_menu.children()[0].set_sensitive(False)

if __name__ == "__main__":
    #splash = gtk.Window()
    #splash.set_decorated(False)
    #splash.show()
    #gobject.timeout_add(3000, splash.hide) # 3*1000 miliseconds

    main = GtkMain()
    #main.show_all()
    gtk.main()

