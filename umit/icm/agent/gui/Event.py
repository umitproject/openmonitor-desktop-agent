#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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

import os, stat, time
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from higwidgets.higwindows import HIGWindow
from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder
from higwidgets.higlabels import HIGLabel
from higwidgets.higentries import HIGTextEntry, HIGPasswordEntry

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp

from google.protobuf.text_format import MessageToString
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.proto import messages_pb2


class EventWindow(HIGWindow):
    column_names = ['Event Type',
                    'Test Type',
                    'Time',
                    'Since Time',
                    'Locations']

    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        
        self.location_user = Location() #user location information
        self.location_user.longitude = 0.0
        self.location_user.latitude  = 0.0
         
        self.set_title(_('Events List'))
        self.set_size_request(720, 580)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connect_widgets()
        
        self.__load_events()

    def __connect_widgets(self):
        
        self.get_event_btn.connect("clicked",lambda w:self._get_event())
        self.refresh_btn.connect("clicked",lambda w:self._refresh_list())
        
    def __create_widgets(self):
        
        #box
        self.all_box = HIGVBox()
        self.input_box = HIGHBox()
        self.buttom_box = HIGHBox()
        self.check_btn_box = gtk.HButtonBox()
        
        #Add input
        self.title_text = HIGLabel(_("Locations"))
        self.longitude_text = HIGLabel(_("longitude:"))
        self.longitude_entry = HIGTextEntry()
        self.latitude_text = HIGLabel(_("latitude:"))
        self.latitude_entry = HIGTextEntry()         
        
        #Add buttons
        self.get_event_btn = gtk.Button(_("Get Events"))
        self.refresh_btn = gtk.Button(_("Refresh"))
          
        #status bar
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0,'Events in Database')        
                                
        self.listmodel = gtk.ListStore(str, str, str, str, str)

        # create the TreeView
        self.treeview = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.tvcolumn = [None] * len(self.column_names)
        cellpb = gtk.CellRendererText()

        self.tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0], cellpb)
        self.tvcolumn[0].add_attribute(cellpb, 'text', 0)
        #cell = gtk.CellRendererText()
        #self.tvcolumn[0].set_cell_data_func(cell, self.test_type)
        self.treeview.append_column(self.tvcolumn[0])

        for n in range(1, len(self.column_names)):
            cell = gtk.CellRendererText()
            self.tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
            self.tvcolumn[n].add_attribute(cell, 'text', n)
            if n == 1:
                cell.set_property('xalign', 1.0)
            #self.tvcolumn[n].set_cell_data_func(cell, cell_data_funcs[n])
            self.treeview.append_column(self.tvcolumn[n])

        #self.treeview.connect('row-activated', self.open_file)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.treeview.set_model(self.listmodel)
        
    def __pack_widgets(self):
        
        self.all_box._pack_noexpand_nofill(self.input_box)
        self.all_box._pack_expand_fill(self.scrolledwindow) 
        self.all_box._pack_noexpand_nofill(self.buttom_box)  
                
        self.input_box.pack_start(self.title_text)
        self.input_box.pack_start(self.longitude_text)
        self.input_box.pack_start(self.longitude_entry)
        self.input_box.pack_start(self.latitude_text)
        self.input_box.pack_start(self.latitude_entry)
       
        self.buttom_box.pack_start(self.statusbar,True,True,0)
        self.buttom_box.pack_end(self.check_btn_box,False,False,0)
        
        self.check_btn_box.set_layout(gtk.BUTTONBOX_END)
        self.check_btn_box.set_spacing(8)       
        self.check_btn_box.pack_start(self.get_event_btn)
        self.check_btn_box.pack_start(self.refresh_btn)   
        
        self.add(self.all_box)
        
    def __load_events(self):
        for event_entry in theApp.event_manager.event_repository:
            if event_entry.EventType == 'CENSOR':
                pass
            elif event_entry.EventType == 'THROTTLING':
                pass
            elif event_entry.EventType == 'OFF_LINE':
                pass
            self.listmodel.append(
                [event_entry.EventType,
                 event_entry.TestType,
                 time.strftime("%Y-%m-%d %H:%M:%S",
                               time.gmtime(event_entry.TimeUTC)),
                 time.strftime("%Y-%m-%d %H:%M:%S",
                               time.gmtime(event_entry.SinceTimeUTC)),
                 event_entry.Locations])

    
    def _get_event(self):
        """
        get events from aggregator by using Aggregator API:get_events
        """
        longtitude = self.longitude_entry.get_text()
        latitude   = self.latitude_entry.get_text()
        
        if longtitude != "" and latitude != "":
            self.location_user.longitude = float(longtitude)
            self.location_user.latitude  = float(latitude)
        else:
            #There we should add user preference logitude
            self.location_user.longitude = 0.0
            self.location_user.latitude  = 0.0
        
        defer_ = theApp.aggregator.get_events(self.location_user)
        defer_.addCallback(self.finish_get_events)
        defer_.addErrback(self.handler_error)
    
    def _refresh_list(self):
        """
        clear and load
        """
        self.listmodel.clear()
        self.__load_events()
        self.statusbar.push(0,_("Refresh the Events List!"))  
     
    def handler_error(self,failure):
        g_logger.error("Error in get events %s"%str(failure))
        self.statusbar.push(0,_("Error in Get Events From Aggregator!"))         
            
    def finish_get_events(self,message):
        if message is None:
            self.statusbar.push(0,_("No new Events from Aggregator!"))  
            return
        
        self.statusbar.push(0,_("Get %d Events from Aggregator"%(len(message.events))))  
        

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
    wnd = EventWindow()
    gtk.main()
