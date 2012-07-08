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

from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder

class TLHoder(gtk.VBox):
    
    def __init__(self,dashboard): #maybe import some kinds(report,task,connection,Throttled,Service)
        """
        Load timeline for every report(sent or unsent), test successful or failed (website or service)
        task (done or not), Throttled details(different charts)
        """ 
        
        gtk.VBox.__init__(self)
        
        self.connector = Connector()
        self.dashboard = dashboard
        
        self.base = TimeLineBase(self.connector,self.dashboard)    #Maybe add some items
        
        self.__create_widgets()
        self.__packed_widgets()
        self.__connect_widgets()
        
    def __create_widgets(self):
        """
        """
        # startup data
        line_filter, start, evts = self.base.grab_data()
        xlabel = self.base.xlabel
        glabel = self.base.title_by_graphmode()
        dlabel = self.base.descr_by_graphmode()
        
        #Box
        self.box = HIGVBox()
        
        #graph
        self.graph_box = gtk.HBox()
        self.graph = InteractiveGraph(evts, start, x_label=xlabel,
            y_label=_('Number of events'), graph_label=glabel,
            descr_label=dlabel, vdiv_labels=self.base.labels,
            line_filter=line_filter, connector=self.connector)
        
        #graph toolbar
        self.graphtb = TimeLineGraphToolbar(self.graph, self.connector,
                                            self.base.graph_mode,self.base.graph_kind,
                                            self.base)
        
        #TODO: Add Display Bar in the further
    
    def __packed_widgets(self):
        """
        """
        self.graph_box.add(self.graph)
        
        self.box._pack_noexpand_nofill(self.graphtb)
        self.box._pack_expand_fill(self.graph_box)
        
        self.add(self.box)
                
        self.show_all()
        
    def __connect_widgets(self):
        """
        Handle the connector signals
        """
        self.connector.connect('data-update',self._update_graph)
        #TODO: we should add signals for the changes of left treeview
    
    def _update_graph(self,obj,*args):
        """
        New graph data arrived
        """    
        line_filter, start, evts, labels, xlabel, glabel, dlabel = args
        
        # new graph data
        self.graph.start_pts_data = start
        self.graph.graph_data = evts
        
        # find new max value
        self.graph.find_max_value()
        
        # update graph labels
        self.graph.xlabel = xlabel
        self.graph.graph_label = glabel
        self.graph.descr_label = dlabel
        self.graph.vdiv_labels = labels
        
        # do graph animation with new data
        self.graph.do_animation()                                        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

