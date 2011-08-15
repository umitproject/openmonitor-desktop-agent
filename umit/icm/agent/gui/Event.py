#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#          Alan Wang <wzj401@gmail.com>
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

import os, stat, time
import pygtk
pygtk.require('2.0')
import gtk

from higwidgets.higwindows import HIGWindow

from umit.icm.agent.I18N import _


class EventWindow(HIGWindow):
    column_names = ['test type', 'event type', 'time', 'location', 'reports']

    def __init__(self, dname = None):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)

        cell_data_funcs = (None, self.event_type, self.time,
                           self.location, self.report)

        # Create a new window
        #self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Event List'))
        self.set_size_request(400, 300)

        listmodel = gtk.ListStore(None) #dname

        # create the TreeView
        self.treeview = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.tvcolumn = [None] * len(self.column_names)
        cellpb = gtk.CellRendererPixbuf()
        self.tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0], cellpb)
        cell = gtk.CellRendererText()
        self.tvcolumn[0].pack_start(cell, False)
        self.tvcolumn[0].set_cell_data_func(cell, self.test_type)
        self.treeview.append_column(self.tvcolumn[0])
        for n in range(1, len(self.column_names)):
            cell = gtk.CellRendererText()
            self.tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
            if n == 1:
                cell.set_property('xalign', 1.0)
            self.tvcolumn[n].set_cell_data_func(cell, cell_data_funcs[n])
            self.treeview.append_column(self.tvcolumn[n])

        #self.treeview.connect('row-activated', self.open_file)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.treeview.set_model(listmodel)
        self.add(self.scrolledwindow)

    def test_type(self, column, cell, model, iter):
        #cell.set_property('text', model.get_value(iter, 0))
        return

    def event_type(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', filestat.st_size)
        return

    def time(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', oct(stat.S_IMODE(filestat.st_mode)))
        return

    def location(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', time.ctime(filestat.st_mtime))
        return

    def report(self, column, cell, model, iter):
        return


if __name__ == "__main__":
    flcdexample = EventWindow()
    gtk.main()