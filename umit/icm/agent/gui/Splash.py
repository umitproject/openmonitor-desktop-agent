#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Zhongjie Wang <wzj401@gmail.com>
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
from higwidgets.higboxes import hig_box_space_holder
from umit.icm.agent.Version import VERSION

class Splash(gtk.Window):
    def __init__(self, image):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER)

        splash_img = gtk.gdk.pixbuf_new_from_file(image)
        pixmap, mask = splash_img.render_pixmap_and_mask()
        width, height = pixmap.get_size()
        del splash_img

        self.set_app_paintable(True)
        self.set_size_request(width, height)
        self.set_resizable(False)
        self.realize()

        self.vbox = gtk.VBox()
        self.label = gtk.Label("Initializing...")
        #self.label.set_use_markup(True)
        #self.label.set_markup("<span size='10000'>%s</span>" % "Initializing...")

        self.hor = gtk.HBox()
        self.hor.pack_end(self.label, True, False)
        self.hor.pack_end(hig_box_space_holder(), True, False)

        # These constants are derived from the dimensions of the open space in
        # the splash graphic. We attempt to center the version number.
        self.vbox.set_size_request(152, 56)
        self.vbox.pack_start(self.hor, True, False)

        fixed = gtk.Fixed()
        fixed.put(self.vbox, 0, 50)
        self.add(fixed)

        self.hid = self.connect("expose-event", self.set_bg, mask, pixmap)
        self.set_bg(self, None, mask, pixmap)
        self.shape_combine_mask(mask, 0, 0)
        self.show_all()

        while gtk.events_pending():
            gtk.main_iteration()

    def destroy(self):
        gtk.Window.destroy(self)
        return False

    def set_bg(self, widget, event, mask, pixmap):
        if self.window is not None:
            self.window.set_back_pixmap(pixmap, False)
        else:
            gobject.idle_add(self.set_bg, widget, event, mask, pixmap)

if __name__ == "__main__":
    import os
    pic_path = os.path.join(os.path.curdir, "..\\..\\..\\..", "share", "images", "splash.png")
    s = Splash(pic_path)
    gtk.main()
