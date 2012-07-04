#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
#          Tianwei Liu <liutainweidlut@gmail.com> 
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

import datetime

from umit.icm.agent.gui.dashboard.timeline.Calendar  import CalendarManager
from umit.icm.agent.gui.dashboard.timeline.Calendar  import months
from umit.icm.agent.gui.dashboard.timeline.Calendar  import monthname
from umit.icm.agent.gui.dashboard.timeline.Calendar  import startup_calendar_opts
from umit.icm.agent.gui.dashboard.timeline.DataGrabber import DataGrabber
from umit.icm.agent.gui.dashboard.timeline.DataGrabber import DATA_GRAB_MODES

from umit.icm.agent.I18N import _

view_mode = {
    "yearly": _("Yearly View"),
    "monthly": _("Monthly View"),
    "daily": _("Daily View"),
    "hourly": _("Hourly View")
    }

view_mode_order = ["yearly", "monthly", "daily", "hourly"]

view_mode_descr = {
    "yearly": _("Year"),
    "monthly": _("Month"),
    "daily": _("Day"),
    "hourly": _("Hour")
    }

xlabels = {
    "yearly": _("Months"),
    "monthly": _("Days"),
    "daily": _("Hours"),
    "hourly": _("Minutes")
    }

#Define the task,report,test
changes_in_db = {
        'successful': _("Successful"),      #Test
        'failed': _("Failed"),              #Test
        'done': _("Done"),                  #Task
        'wait': _("Wait"),                  #Task
        'sent': _("Sent"),                  #Report
        'unsent': _("unsent")               #report
        }
categories = dict(changes_in_db)
categories['changes_sum'] = _("Changes Sum")

changes_list = changes_in_db.keys()

def colors_from_file_gdk():
    """
    Retrieve colors from timeline settings file and convert to gdk format.
    """
    colors = colors_from_file()

    for key, value in colors.items():
        colors[key] = [int(65535 * v) for v in value]

    return colors

def colors_from_file():
    """
    Retrieve colors from timeline settings file.    
    """
    colors = {
              "inventory":[0.188, 0.659, 0.282],
              "availability":[0.847, 0.016, 0.016],
              "ports":[0.988, 0.82, 0.157],
              "fingerprint":[0.369, 0.008, 0.353],
              "several":[0.133, 0.361, 0.706],
              "nothing":[0.545, 0.502, 0.514],
              "changes_sum" :[0, 0.4, 1],
              }
    
    return colors

def gradient_colors_from_file():
    """
    Retrieve gradient from timeline settings file.
    """
    gradient = {
                "inventory":[0.69, 0.859, 0.722] ,
                "availability":[0.847, 0.57, 0.57],
                "ports":[0.988, 0.949, 0.604],
                "fingerprint":[0.588, 0.008, 0.549],
                "several":[0.624, 0.737, 0.906],
                "nothing":[0.784, 0.784, 0.784],
                }
    return gradient


class TimeLineBase(CalendarManager, DataGrabber):
    """
    This class does the necessary Timeline management.
    """
    
    def __init(self,connector):
        # using current date at startup
        CalendarManager.__init__(self)
        DataGrabber.__init__(self)        
        
        self.connector = connector
        self.grabber_method = None
        self.grabber_params = None
        self.labels = None
        self.xlabel = None
        
        self.selection = -1
        self.selected_range = (None, None)
        self.graph_mode = "daily"
        self.update_grabber()
        
        self.connector.connect('selection-changed', self._handle_selection)
        self.connector.connect('data-changed', self._update_graph_data)
        self.connector.connect('date-update', self._update_date)
        
    def _handle_selection(self,obj,selection):
        """
        Handles TimeLine selection, detect the selected time range
        """
        self.selection = selection
        
        if selection == -1 :
            start = end = None
        
        elif self.graph_mode == "yearly":   #months
            selection += 1  # months starting at 1
            start = datetime.datetime(self.year, selection, 1)
            end   = start + datetime.timedelta(days=self.get_monthrange(
                self.year, selection)[1])
        elif self.graph_mode == "monthly":   # days
            selection += 1  # days starting at 1
            start = datetime.datetime(self.year, self.month, selection)
            end = start + datetime.timedelta(days=1)
        elif self.graph_mode == "daily":   # hours
            start = datetime.datetime(self.year, self.month, self.day,
                selection)
            end = start + datetime.timedelta(seconds=3600)
        elif self.graph_mode == "hourly": # minutes
            start = datetime.datetime(self.year, self.month, self.day,
                self.hour, selection)
            end = start + datetime.timedelta(seconds=60)    
            
        self.selected_range = (start,end)
        
        self.connector.emit('selection-update', start, end)                   
    
    def grab_data(self):
        """
        Grab data for graph using current settings.
        """
        return (None,None,None)         
    
    def update_grabber(self):
        """
        Updates grabber method, params and graph vlabels.
        """
        
        labels = [ ]
        if self.graph_mode == "yearly":
            params = (self.year, )
            for m in months:
                labels.append(m[:3])

        elif self.graph_mode == "monthly":
            params = (self.year, self.month)
            for i in range(self.get_current_monthrange()[1]):
                labels.append("%d" % (i + 1))

        elif self.graph_mode == "daily":
            params = (self.year, self.month, self.day)
            for i in range(24):
                labels.append("%d" % i)

        elif self.graph_mode == "hourly":
            params = (self.year, self.month, self.day, self.hour)
            for i in range(60):
                labels.append("%d" % i)

        self.grabber_params = params  
        self.labels = labels
        self.xlabel = xlabels[self.graph_mode]                      
    
    def descr_by_graphmode(self):
        """
        Returns a description with graph meaning.
        """
        graph_descr = [
            _("end of a week"), _("end of 12 hours period"),
            _("end of half hour period"), _("end of a minute")
            ]

        return _("Each point break represents ") + \
               graph_descr[view_mode_order.index(self.graph_mode)]
                      
    def title_by_graphmode(self, useselection=False):
        """
        Returns a formatted date based on current graph mode (Yearly,
        Monthly, .. ).
        """
        def adjust(date):
            # prepends a 0 in cases where a date is minor than 10,
            # so (example) hour 2 displays as 02.
            if date < 10:
                date = "0%s" % date

            return date


        if useselection and self.selection != -1:
            fmtddate = [
                  "%s, %s" % (monthname((self.selection + 1) % 12),
                              # % 12 above is used so we don't have
                              # problems in case self.selection > 12,
                              # that is, when someone is viewing in
                              # other mode different than "Yearly".
                              self.year),

                  "%s, %s %s, %s" % (self.get_weekday(self.year,
                                      self.month, (self.selection+1)%\
                                      (self.get_current_monthrange()[1]+1))[1],
                                     monthname(self.month), self.selection+1,
                                     self.year),

                  "%s, %s %s, %s (%s:00)" % (self.get_current_weekday_name(),
                                             monthname(self.month),
                                             self.day, self.year,
                                             adjust(self.selection % 23)),

                  "%s, %s %s, %s (%s:%s)" % (self.get_current_weekday_name(),
                                             monthname(self.month), self.day,
                                             self.year, adjust(self.hour),
                                             adjust(self.selection))
                       ]
        else:
            fmtddate = [

                  _("Year %(year)s") % {'year': self.year},

                  "%s, %s" % (monthname(self.month), self.year),

                  "%s, %s %s, %s" % (self.get_current_weekday_name(),
                                        monthname(self.month), self.day,
                                        self.year),

                  "%s, %s %s, %s (%s:00)" % (self.get_current_weekday_name(),
                                             monthname(self.month),
                                             self.day, self.year, self.hour)
                       ]

        return fmtddate[view_mode_order.index(self.graph_mode)]    
                    
    def bounds_by_graphmode(self):
        """
        Return min, max and current value for graph mode.
        """

        values = [
            (self.year_range[0], self.year_range[1], self.year),
            (1, 12, self.month),
            (1, self.get_current_monthrange()[1], self.day),
            (0, 23, self.hour)
            ]

        return values[view_mode_order.index(self.graph_mode)]
    
    def _update_graph_data(self,obj,*args):
        """
        Received a request to perform graph data update
        """ 
        
        self.connector.emit('data-changed')
    
    def _update_date(self,obj,arg):
        """
        Update date based on current mode.        
        """
        modes = {
            "yearly": "year",
            "monthly": "month",
            "daily": "day",
            "hourly": "hour" }
        
        if self.graoh_mode in modes:
            self.modes[self.graoh_mode] = arg
        
        self.connector.emit('data-changed',None,None)
        
        
        
        
        
         
            
