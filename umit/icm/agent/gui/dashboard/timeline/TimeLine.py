# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Tianwei Liu <liutianweidlut@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
TimeLine Part in Dashboard Window
"""
import gtk

from umit.icm.agent.I18N import _

from umit.icm.agent.gui.dashboard.timeline.TimeLineGraph import InteractiveGraph
from umit.icm.agent.gui.dashboard.timeline.TimeLineConnector import Connector
from umit.icm.agent.gui.dashboard.timeline.TimeLineGraphToolbar import TimeLineGraphToolbar
from umit.icm.agent.gui.dashboard.timeline.TimeLineGraphBase import TimeLineBase

class TLHoder(gtk.VBox):
    def __init__(self): #maybe import some kinds(report,task,connection,Throttled,Service)
        """
        Load timeline for every report(sent or unsent), test successful or failed (website or service)
        task (done or not), Throttled details(different charts)
        """ 
        
        gtk.VBox.__init__(self)
        
        self.connector = Connector()
        self.base = TimeLineBase(self.connector)    #Maybe add some items
        
        self.__create_widgets()
        
    def __create_widgets(self):
        """
        """
        # startup data
        line_filter, start, evts = self.base.grab_data()
        xlabel = self.base.xlabel
        glabel = self.base.title_by_graphmode()
        dlabel = self.base.descr_by_graphmode()
        
        #graph
        self.graph_box = gtk.HBox()
        self.graph = InteractiveGraph(evts, start, x_label=xlabel,
            y_label=_('Number of events'), graph_label=glabel,
            descr_label=dlabel, vdiv_labels=self.base.labels,
            line_filter=line_filter, connector=self.connector)
        
        #graph toolbar
        self.graphtb = TimeLineGraphToolbar(self.graph, self.connector,
                                            self.base.graph_mode)
        
        #TODO: Add Display Bar in the further
    
    def __packed_widgets(self):
        """
        """
        self.graph_box.pack_start(elf.graph, True, True, 3)
        
        self.pack_start(self.graphtb, False, False, 0)
        self.pack_start(self.graph_box, False, False, 3)
        
    def __connect_widgets(self):
        """
        Handle the connector signals
        """
        self.connector.connect('data-update',self._update_graph)
        
        #TODO: we should add signals for the changes of left treeview
         
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

