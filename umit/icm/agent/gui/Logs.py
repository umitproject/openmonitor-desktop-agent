#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#          Tianwei Liu <liutianweidl>
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
import sys

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.BasePaths import LOG_DIR

class LogsWindow(HIGWindow):
    """
    Logs Window
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Logs'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_size_request(720,480)
        self.set_border_width(10)
        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connect_widgets()
        
        #test
        #from umit.icm.agent.gui.Notifications import *
        #t = NotificationUpdate(mode=new_release_mode,text="test",timeout=10000)

    def __create_widgets(self):
        """"""
        #box
        self.main_vbox = HIGVBox()
        self.btn_box = gtk.HButtonBox()
        self.LogsGUI_vbox = HIGHBox()        
        
        self.main_vbox.set_border_width(2)
        #close button
        self.close_button = gtk.Button(stock=gtk.STOCK_CLOSE)

        #log information box
        self.LogsGUI_hbox1 = HIGHBox()
        self.LogsGUI_hbox2 = HIGHBox()
        self.LogsGUI_subbox = LogsGUI()


    def __pack_widgets(self):
        self.main_vbox._pack_expand_fill(self.LogsGUI_vbox)
        self.main_vbox._pack_noexpand_nofill(self.btn_box)
                
        self.LogsGUI_vbox._pack_expand_fill(self.LogsGUI_hbox1)
        self.LogsGUI_vbox._pack_noexpand_nofill(self.LogsGUI_hbox2)
        
        self.LogsGUI_hbox1._pack_expand_fill(self.LogsGUI_subbox)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(8)
        self.btn_box.pack_start(self.close_button)
                
        self.add(self.main_vbox)
    
    def __connect_widgets(self):
        """"""    
        self.close_button.connect('clicked', lambda x: self.destroy())
         
class LogsGUI(gtk.VBox):
    def __init__(self):
        super(LogsGUI, self).__init__()
        self.log_mask = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

        #self.set_size_request(400, 300)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("""\
<span size='12000'>Open Monitor Desktop Agent Logs: \n</span>""")

        title.set_use_markup(True)

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 0, 1, 0, 1, gtk.FILL, gtk.FILL, 0, 0);

        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textview.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 5)
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_editable(True)
        self.textview.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        self.textview.set_cursor_visible(True)
        self.textview.show()
        self.sw.add(self.textview)
        self.sw.show()
        table.attach(self.sw, 0, 1, 1, 3)

        vbox = gtk.VBox()
        btnbox = gtk.VButtonBox()
        btnbox.set_border_width(5)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btnbox.set_spacing(5)
        self.checkbtn_error = gtk.CheckButton("ERROR")
        self.checkbtn_warning = gtk.CheckButton("WARNING")
        self.checkbtn_info = gtk.CheckButton("INFO")
        self.checkbtn_debug = gtk.CheckButton("DEBUG")
        self.checkbtn_error.set_active(True)
        self.checkbtn_warning.set_active(True)
        self.checkbtn_info.set_active(True)
        self.checkbtn_debug.set_active(True)
        self.checkbtn_error.connect('toggled', lambda x: self.change_mask())
        self.checkbtn_warning.connect('toggled', lambda x: self.change_mask())
        self.checkbtn_info.connect('toggled', lambda x: self.change_mask())
        self.checkbtn_debug.connect('toggled', lambda x: self.change_mask())

        vbox.add(self.checkbtn_error)
        vbox.add(self.checkbtn_warning)
        vbox.add(self.checkbtn_info)
        vbox.add(self.checkbtn_debug)
        table.attach(vbox, 3, 4, 1, 2, gtk.FILL, gtk.SHRINK, 1, 1)

        halign2 = gtk.Alignment(0, 1, 0, 0)
        table.attach(halign2, 4, 5, 0, 1, gtk.FILL, gtk.FILL, 0, 0)

        self.add(table)
        self.refresh()
        gobject.timeout_add(5000, self.refresh)

    def refresh(self):
        #hadjustment = self.textview.get_hadjustment()
        #vadjustment = self.textview.get_vadjustment()
        text = ""
        f = open(os.path.join(LOG_DIR, 'icm-desktop.log'))
        for line in f:
            words = line.split()
            if len(words) == 0:
                continue;
            log_type = (words[0]).strip("[").strip("]")
            if log_type in self.log_mask:
                text = text + line
        f.close()
        self.textbuffer.set_text(text)
        #self.textview.set_scroll_adjustments(hadjustment, vadjustment)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0.0)
        return True

    def change_mask(self):
        self.log_mask = []
        if self.checkbtn_error.get_active():
            self.log_mask.append('ERROR')
        if self.checkbtn_warning.get_active():
            self.log_mask.append('WARNING')
        if self.checkbtn_info.get_active():
            self.log_mask.append('INFO')
        if self.checkbtn_debug.get_active():
            self.log_mask.append('DEBUG')
        self.refresh()


if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = LogsWindow()
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()