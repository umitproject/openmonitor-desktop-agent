#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
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

import time

from zope.interface import implements
from twisted.internet.interfaces import IConsumer

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *

"""
It upload the reports to the Aggregator in a direct or indirect way (i.e. via agent)
"""
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

    def send_report(self, report_key):
        """
        Different priorities of sending report: Aggregator -> Super agent -> desktop normal agent 
        """
        from umit.icm.agent.core.ReportManager import ReportStatus
        
        send_status = False
        report_entry = self.report_manager.cached_reports[report_key]
        #print report_entry
        if theApp.aggregator.send_report(report_entry.Report):
            report_entry.Status = ReportStatus.SENT_TO_AGGREGATOR
            send_status = True
        
        #############################################
        #We should add more mechanisms to send report    
        #elif DesktopSuperAgentRPC.sendReport(report_entry.Report):
        #    report_entry.Status = ReportStatus.SENT_TO_SUPER_AGENT
        #    send_status = True
        #elif DesktopAgentRPC.sendReport(report_entry.Report):
        #    report_entry.Status = ReportStatus.SENT_TO_AGENT
        #    send_status = True
        #else MobileAgentRPC.sendReport(report_entry.Report):
            #report.status = ReportStatus.SENT_TO_AGGREGATOR
            #return True
        #_retry_list.append
 
        #if send_status:
        #    del self.report_manager.cached_reports[report_key]
    
        return send_status

    """
    Upload reports
    """
    def process(self):
        # Upload Report
        if theApp.aggregator.available:
            g_logger.info("Sending %d reports to the aggregator." % \
                          len(self.report_manager.cached_reports))
            for report_key in self.report_manager.cached_reports.keys():    
                self.send_report(report_key)
                #theApp.aggregator.send_report(report_entry.Report)
        else:
            # Later, We should implement other upload path: super peer, normal peer 
            # Choose a random super peer to upload
            g_logger.info("Cannot connect to aggregator, so send report to super peer first!")
            speer_id = theApp.peer_manager.get_random_speer_connected()
            if speer_id is not None:
                g_logger.info("Sending %s reports to the super agent %s." % \
                              (len(self.report_manager.cached_reports),
                               str(speer_id)))
                for report_entry in self.report_manager.cached_reports.values():
                    theApp.peer_manager.sessions[speer_id].\
                          send_report(report_entry.Report)
            elif theApp.peer_info.Type == 2:
                g_logger.info("Cannot connect to aggregator and super peer ,so send report to normal peers!")
                cnt = 0
                sessions = []
                for peer_id in theApp.peer_manager.normal_peers:
                    if theApp.peer_manager.normal_peers[peer_id].status == \
                       'Connected':
                        cnt = cnt + 1
                        sessions.append(theApp.peer_manager.sessions[peer_id])
                if cnt != 0:
                    g_logger.info("Sending %d reports to %d normal agents." % \
                                  (len(self.report_manager.cached_reports), cnt))
                    for report_entry in self.report_manager.cached_reports.values():
                        for session in sessions:
                            session.send_report(report_entry.Report)
                else:
                    g_logger.info("No available peers.")

            



