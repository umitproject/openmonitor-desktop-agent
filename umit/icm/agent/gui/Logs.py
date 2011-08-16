#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
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
import sys

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel

from umit.icm.agent.I18N import _

class LogsWindow(HIGWindow):
    """
    Logs Window
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Logs'))
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.main_vbox = HIGVBox()
        self.add(self.main_vbox)
        self.btn_box = gtk.HButtonBox()
        self.close_button = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.close_button.connect('clicked', lambda x: self.destroy())

        self.LogsGUI_vbox = HIGVBox()
        self.LogsGUI_hbox1 = HIGHBox()
        self.LogsGUI_hbox2 = HIGHBox()
        self.LogsGUI_subbox = LogsGUI()
        self.LogsGUI_hbox1.add(self.LogsGUI_subbox)

    def __pack_widgets(self):
        self.main_vbox._pack_expand_fill(self.LogsGUI_hbox1)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.close_button)
        self.main_vbox.pack_start(self.btn_box)
        self.main_vbox.set_border_width(12)

        self.LogsGUI_vbox.pack_start(self.LogsGUI_hbox1, True, True, 5)
        self.LogsGUI_vbox.pack_start(self.LogsGUI_hbox2, True, True, 5)

class LogsGUI(gtk.VBox):
    def __init__(self):
        super(LogsGUI, self).__init__()
        self.set_size_request(400, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("""\
<span size='12000'>Logs: \n</span>""")

        title.set_use_markup(True)

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 0, 1, 0, 1, gtk.FILL,
                     gtk.FILL, 0, 0);

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tv = gtk.TextView()
        tv.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 5)
        textbuffer = tv.get_buffer()
        tv.set_editable(True)
        tv.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        tv.set_cursor_visible(True)
        tv.show()
        sw.add(tv)
        sw.show()
        table.attach(sw, 0, 1, 1, 3)

        vbox = gtk.VBox()
        btnbox = gtk.VButtonBox()
        btnbox.set_border_width(5)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btnbox.set_spacing(5)
        checkbtn1 = gtk.CheckButton("ERROR")
        checkbtn2 = gtk.CheckButton("WARNING")
        checkbtn3 = gtk.CheckButton("INFO")
        checkbtn4 = gtk.CheckButton("DEBUG")

        vbox.add(checkbtn1)
        vbox.add(checkbtn2)
        vbox.add(checkbtn3)
        vbox.add(checkbtn4)
        table.attach(vbox, 3, 4, 1, 2, gtk.FILL, gtk.SHRINK, 1, 1)

        table.attach(halign, 4, 5, 0, 1, gtk.FILL,
                     gtk.FILL, 0, 0);

        halign2 = gtk.Alignment(0, 1, 0, 0)
        self.add(table)


if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = LogsWindow()
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()