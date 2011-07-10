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

import time

from zope.interface import implements
from twisted.internet.interfaces import IConsumer

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *

########################################################################
class ReportUploader(object):
    """"""

    implements(IConsumer)

    #----------------------------------------------------------------------
    def __init__(self, report_manager):
        """Constructor"""
        self.report_manager = report_manager
        self._failed_list = []

    def fetch_one_report(self):
        report_list = self.report_manager.get_report_list()
        if len(report_list) > 0:
            return report_list.remove(0)
        else:
            return None

    def send_report(self, report):
        #if AggregatorAPI.sendReport(report):
            #report.status = ReportStatus.SENT_TO_AGGREGATOR
            #return True
        #elif DesktopSuperAgentRPC.sendReport(report):
            #report.status = ReportStatus.SENT_TO_SUPER_AGENT
            #return True
        #elif DesktopAgentRPC.sendReport(report):
            #report.status = ReportStatus.SENT_TO_AGENT
            #return True
        #else MobileAgentRPC.sendReport(report):
            #report.status = ReportStatus.SENT_TO_AGGREGATOR
            #return True
        #_retry_list.append
        pass

    def process(self):
        for report_entry in self.report_manager.report_list:
            # Upload Report
            if theApp.aggregator.available:
                theApp.aggregator.send_report(report_entry.report)
            else:
                # Choose a random super peer to upload
                speer_id = theApp.peer_manager.get_random_speer_connected()
                if speer_id is not None:
                    theApp.peer_manager.sessions[speer_id].\
                          send_report(report_entry.Report)
                    # do further things in callback
                else:
                    g_logger.debug("There's no connected super peer.")

            #self.send_report(report_entry)
            # Store Report locally


