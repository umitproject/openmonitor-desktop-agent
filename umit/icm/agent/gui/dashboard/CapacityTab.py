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

#from Dashboard import CAPACITY,CAPA_THROTTLED,CAPA_SERVICE
from umit.icm.agent.gui.dashboard.DashboardListBase import  *

class CapacityTab(gtk.VBox):
    """
    CapacityTab: show the network's Capacity  
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)

        self.set_visible(False)
                
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()  
    
    def __create_widgets(self):
        """
        """
        pass
    
    def __pack_widgets(self):   
        """
        """
        pass
    
    def __connected_widgets(self):
        """
        """
        pass   
    
class ThrottledTab(gtk.VBox):
    """
    ThrottledTab : Show the network throttled 
    """
    def __init__(self):
        """
        """
        gtk.VBox.__init__(self)
        
        self.set_visible(False)
        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connected_widgets()   
    
    def __create_widgets(self):
        """
        """
        pass
    
    def __pack_widgets(self):   
        """
        """
        pass
    
    def __connected_widgets(self):
        """
        """
        pass   
    
class ServiceTab(gtk.VBox): 
    """
    ServiceTab: Show the results of different services
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
        pass
    
    def __pack_widgets(self):   
        """
        """
        pass
    
    def __connected_widgets(self):
        """
        """
        pass          











