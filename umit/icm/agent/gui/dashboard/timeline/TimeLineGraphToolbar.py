#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Tianwei Liu <liutainweidlut@gmail.com> 
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
Timeline graph toolbar
"""

import pygtk
pygtk.require('2.0')
import gtk, gobject

from umit.icm.agent.I18N import _
from umit.icm.agent.gui.dashboard.timeline.TimeLineGraphBase import view_mode,view_mode_order

class TimeLineGraphToolbar(gtk.Toolbar):
    """
    Build a Toolbar for controlling Interactive Timeline Graph
    """
    def __init__(self,graph,connector,graph_mode=None):
        gtk.Toolbar.__init__(self)
        
        self.graph = graph
        self.connector = connector
        self.graph_mode = graph_mode    #Year,month,day and hour
        
        self.__create_widgets()
        self.__packed_widgets()
        self.__connected_widgets()
        
    def __create_widgets(self):
        """"""
        self.tooltips = gtk.Tooltips()
        
    def __packed_widgets(self):
        """"""
        self.insert(self.graph_mode(self.graph_mode),0) #Year,month,day and hour
        self.insert(self.graph_time(),1)                #Time choice 
        self.insert(self.graph_time_apply(),2)          #Apply button
        self.insert(gtk.SeparatorToolItem(),3)          
        self.insert(self.graph_kind(),4)                #Line or Area
        self.insert(gtk.SeparatorToolItem(),5)
        self.insert(self.graph_refresh(),6)             #Refresh Button
        
    def __connected_widgets(self):
        """"""
        pass
    
    def packed(self,*widgets):
        """
        Pack Widgets in a gtk.Hbox and return a gtk.ToolItem
        """
        box = gtk.HBox()
        for w in widgets:
            box.pack_start(w,False,False,0)
            
        item = gtk.ToolItem()
        item.add(box)
        
        return item
    
    def graph_mode(self,graph_mode = None):
        """
        Graph Mode: Year, Month, Day, Hour viewing modes
        """
        self.view_mode = gtk.combo_box_new_text()
        
        for mode in view_mode_order:
            self.view_mode.append_text(view_mode[mode])
            
        if graph_mode:
            option = view_mode_order.index(graph_mode)
        else:
            option = 0
            
        self.view_mode.set_active(option)
        
        self.view_mode.connect('changed',self.change_graph_mode())
        
        return self.packed(self.view_mode)

    def change_graph_mode(self,event):
        """
        Viewing Mode Setting 
        """
        mode = view_mode_order[event.get_active()]
        self.connector.emit('data-changed',mode,None)
    
    def graph_time(self):
        """
        """
        pass
    
    def graph_time_apply(self):
        """
        """
        apply_button = gtk.Button(_("Apply"))
        apply_button.set_relief(gtk.RELIEF_NONE)
        apply_button.connect('clicked',self.change_graph_time_apply)
        
        return self.packed(apply_button)
    
    def change_graph_time_apply(self):
        """
        """
        pass

    def graph_refresh(self):
        """
        Graph refreshing controller
        """
        refresh_button = gtk.Button()
        refresh_button.set_relief(gtk.RELIEF_NONE)
        self.tooltips.set_tip(refresh_button, _("Graph Refresh"))
        
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_REFRESH,gtk.ICON_SIZE_BUTTON)
        box = gtk.HBox()
        box.pack_start(img,False,False,0)
        box.pack_end(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT), False, False, 0)
        refresh_button.add(box)
        refresh_button.connect("clicked",self.change_graph_refresh)
        
        return self.packed(refresh_button)
    
    def change_graph_refresh(self,event):
        """
        Refresh now
        """
        self.connector.emit('data-changed',None,None)
    
    def graph_kind(self):
        """
        Graph kind: Line and Area
        """
        modes = _("Line Graph"), _("Area Graph")
        self.combo_graph_kind = gtk.combo_box_new_text()
        self.combo_graph_kind.append_text(_("Select a graph style"))
        
        for mode in modes:
            self.combo_graph_kind.append_text(mode)

        self.combo_graph_kind.set_active(1)
        self.combo_graph_kind.connect('changed',self.change_graph_kind)
        
        return self.packed(self.combo_graph_kind)
        
    def change_graph_kind(self,enent):
        """
        Display possible ways on how graph may grab changes
        """
        active = event.get_active()
        if active:
            self.graph.graph_type = active-1 
        
    def udate_graph(self):
        """
        Update graph after settings new options for it
        """
        self.graph.setup_new_graph()

class TimeBox(gtk.HBox):
    """
    Gui Controls for handling Timeline data visualizations
    """        
    def __init__(self,connector,timeline_base):
        gtk.HBox.__init__(self)
        
        self.connector = connector
        self.timeline_base = timeline_base
                
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()
        
    def __create_widgets(self):
        """
        """
        cur_mode = view_mode_descr[self.timeline_base.graph_mode]
        self.select_label = gtk.Label(cur_mode)
        values = self.timeline_base.bounds_by_graphmode()
        self.date_select = gtk.SpinButton(gtk.Adjustment(value=values[2],
            lower=values[0], upper=values[1], step_incr=1), 1)
        
        self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)

        
    def __pack_widgets(self):
        """
        Layout widgets.
        """
        self.pack_start(self.select_label, False, False, 0)
        self.pack_start(self.date_select, False, False, 0)
        self.pack_start(self.apply_button, False, False, 0)
        
        
    def __connected_widgets(self):
        """
        """
        self.connector.connect('date-changed', self._update_current_date)
        self.apply_button.connect("clicked", self._date_change)
        
    def _date_change(self,event):
        """
        send new date
        """
        self.connector.emit('date-update', self.dateselect.get_value_as_int())

    def _update_current_date(self, event):
        """
        Update spinbutton and values based on new date.
        """
        cur_mode = view_mode_descr[self.tlbase.graph_mode]
        self.select_label.set_label(cur_mode)

        values = self.timeline_base.bounds_by_graphmode()
        self.dateselect.set_range(values[0], values[1])
        self.dateselect.set_value(values[2])      
        
      
        
        
        
        
        
        
        
        
    
              