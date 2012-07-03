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

import pygtk
pygtk.require('2.0')
import gtk, gobject

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp

################
#Task Definition
TASK           = _("Tasks")
TASK_ALL       = _("Tasks Details")
TASK_SUCCESSED = _("Tasks Succeeded")
TASK_FAILED    = _("Tasks Failed")

##################
#Report Definition
REPORT         = _("Reports")
REPORT_SENT    = _("Sent Details")
REPORT_UNSENT  = _("Unsent Details")
REPORT_RECEIVED= _("Received Details")

######################
#Connection Definition
CONNECTION    = _("Connections")
CONN_AGG      = _("Aggregator") 
CONN_SUPER    = _("Super Agent")
CONN_NORMAL   = _("Normal Agent") 
CONN_MOBILE   = _("Mobile Agent")

####################
#Capacity Definition
CAPACITY      = _("Capacity")
CAPA_THROTTLED= _("Network Throttled")
CAPA_SERVICE  = _("Network Service")


class DashboardListBase(gtk.VBox):
    """
    DashboardListBase: It can provide the basic list store details
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)

        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()  
    
    def __create_widgets(self):
        """
        """
        self.detail_liststore = gtk.ListStore(str, str, str)
        self.detail_treeview = gtk.TreeView(self.detail_liststore)
        
        catacolumn = gtk.TreeViewColumn('Catagories')
        timescolumn = gtk.TreeViewColumn('Times')      
        
        self.detail_treeview.append_column(catacolumn)
        self.detail_treeview.append_column(timescolumn)   
        
        catacell = gtk.CellRendererText()
        timecell = gtk.CellRendererText()

        catacolumn.pack_start(catacell, True)
        timescolumn.pack_start(timecell, True)
        
        catacolumn.set_attributes(catacell, text=0)
        timescolumn.set_attributes(timecell, text=2)
        self.detail_treeview.set_search_column(0)
        catacolumn.set_sort_column_id(0)
        
        self.detail_treeview.set_reorderable(True) 
    
    
    def __pack_widgets(self):   
        """
        """
        self.add(self.detail_treeview)
    
    def __connected_widgets(self):
        """
        """
        pass  
    def show(self,show_type=None):
        """
        """
        raise NotImplementedError('You need to implement this method')   
    
    
    