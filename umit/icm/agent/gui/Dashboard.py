#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
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

from pygtk_chart.line_chart import LineChart, Graph

from higwidgets.higwindows import HIGWindow

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp


########################################################################
class DashboardWindow(HIGWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Dashboard'))
        self.set_size_request(600, 400)

        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        chart = LineChart()
        graph = Graph("NewGraph", "Title", [(1,1),(2,2),(3,3)])
        chart.set_xrange((0, 10))
        chart.set_yrange((0, 5))
        chart.add_graph(graph)

        self.add(chart)
        self.show_all()

    def __pack_widgets(self):
        pass

if __name__ == "__main__":
    wnd = DashboardWindow()
    wnd.show_all()
    gtk.main()

