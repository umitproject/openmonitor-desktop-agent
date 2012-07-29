#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
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
import os.path

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higbuttons import HIGButton
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView

from umit.icm.agent.BasePaths import IMAGES_DIR

from umit.icm.agent.Global import *

from umit.icm.agent.I18N import _


class About(HIGWindow):
    def __init__(self):
        """"""
        HIGWindow.__init__(self)
        self.set_title("About Open Monitor Desktop Agent")
        self.set_position(gtk.WIN_POS_CENTER)

        self.__create_widgets()
        self.__packing()
        self.__connect_widgets()
        self.__set_img()
        self.__set_text()

    def __create_widgets(self):
        """"""
        self.vbox = HIGVBox()
        self.vbox_content = HIGVBox()
        
        self.img_logo = gtk.Image()
        self.event_img_logo = gtk.EventBox()
        
        self.vbox.set_border_width(5)
        self.vbox.set_spacing(12)
        
        self.img = 1

        self.d = {}
        for c in (65, 97):
            for i in range(26):
                self.d[chr(i+c)] = chr((i+13) % 26 + c)
                
        self.lbl_program_version = gtk.Label(
            "<span size='15000' weight='heavy'>Open Monitor Desktop Agent</span>")

        self.lbl_program_description = gtk.Label("""\
ICM Internet Connectivity is a global monitor to
inspect the connectivity issues happened in the world.
Developer: Alan Wang<wzj401@gmail.com>
Paul Pei<paul.kdash@gmail.com>
Tianwei Liu<liutianweidlut@gmail.com>
It was sponsered by Google Summer of Code 2011-2012. 
Thanks Google!""")

        self.lbl_copyright=gtk.Label(
            "<small>Copyright (C) 2012 Adriano Monteiro Marques</small>")

        self.lbl_program_website = gtk.Label(
            "<span underline='single' foreground='blue'>"
            "http://www.umitproject.org</span>")
        self.lbl_program_website2 = gtk.Label(
            "<span underline='single' foreground='blue'>"
            "http://www.openmonitor.org</span>")
        
        self.bottom_btn_box = gtk.HButtonBox()
        self.btn_close = HIGButton(stock=gtk.STOCK_CLOSE)
        self.btn_close.grab_focus()

    def __packing(self):
        """"""        
        self.vbox._pack_expand_fill(self.vbox_content)
        self.vbox._pack_noexpand_nofill(self.bottom_btn_box)       
        
        self.bottom_btn_box.set_layout(gtk.BUTTONBOX_CENTER)
        self.bottom_btn_box.set_spacing(8)  
        self.bottom_btn_box.pack_start(self.btn_close)         
              
        self.event_img_logo.add(self.img_logo)

        self.vbox_content._pack_expand_fill(self.event_img_logo)
        self.vbox_content._pack_expand_fill(self.lbl_program_version)
        self.vbox_content._pack_expand_fill(self.lbl_program_description)
        self.vbox_content._pack_expand_fill(self.lbl_copyright)
        self.vbox_content._pack_expand_fill(self.lbl_program_website)
        self.vbox_content._pack_expand_fill(self.lbl_program_website2)        

        self.add(self.vbox)
        
    def __connect_widgets(self):
        """"""
        self.event_img_logo.connect('button-release-event', self.__set_size)
        self.btn_close.connect('clicked', lambda x: self.destroy())
        
    def __set_size(self, widget, extra = None):
        """"""
        if self.img >= 3:
            import webbrowser
            webbrowser.open("http://www.openmonitor.org")
            #print "".join([self.d.get(c, c) for c in "vzcbeg cvpxyr,om2;sebz hzvg.pber.Cnguf\
            #vzcbeg Cngu; rkrp cvpxyr.ybnq(om2.OM2Svyr(Cngu.hzvg_bcs,'e'))"])
            #exec "".join([self.d.get(c, c) for c in "vzcbeg cvpxyr,om2;sebz hzvg.pber.Cnguf\
            #vzcbeg Cngu; rkrp cvpxyr.ybnq(om2.OM2Svyr(Cngu.hzvg_bcs,'e'))"])
        else: self.img += 1

    def __set_text(self):
        """"""
        self.lbl_program_version.set_use_markup(True)
        self.lbl_copyright.set_use_markup(True)
        self.lbl_program_website.set_use_markup(True)
        self.lbl_program_website2.set_use_markup(True)        
        self.lbl_program_description.set_justify(gtk.JUSTIFY_CENTER)

        self.lbl_copyright.set_selectable(False)
        self.lbl_program_description.set_selectable(False)
        self.lbl_program_version.set_selectable(False)
        self.lbl_program_website.set_selectable(False)

    def __set_img(self):
        """"""        
        #ixmaps_dir = Path.pixmaps_dir
        #if pixmaps_dir:
        #    logo = os.path.join(pixmaps_dir,'logo.png')
        #else:
        #    logo = None
        logo = os.path.join(IMAGES_DIR, "logo.png")
        self.img_logo.set_from_file(logo)
        #logo = gtk.gdk.pixbuf_new_from_file("logo.png")
        #self.img_logo.set_from_file(logo)

if __name__ == '__main__':
    import sys
    about = About()
    about.connect('delete-event', lambda x,y:gtk.main_quit())
    about.show_all()
    gtk.main()
