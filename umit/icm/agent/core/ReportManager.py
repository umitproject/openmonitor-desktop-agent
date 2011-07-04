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

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

class ReportStatus:
    UNSENT = 'Unsent'
    SENT_TO_AGGREGATOR = 'SentToAggregator'
    SENT_TO_SUPER_AGENT = 'SentToSuperAgent'
    SENT_TO_AGENT = 'SentToAgent'

########################################################################
class ReportEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = None
        self.SourceID = 0
        self.TimeGen = 0
        self.TestID = 0
        self.Report = None
        self.SourceIP = None
        self.Status = ReportStatus.UNSENT

    def __str__(self):
        return "(id=%s, source_id=%d, time_gen='%s', test_id=%d, "\
               "report='%s', source_ip=%s, status=%s)" % \
               (self.ID,
                self.SourceID,
                time.ctime(self.TimeGen),
                self.TestID,
                self.Report,
                self.SourceIP,
                self.Status)

########################################################################
class ReportManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.report_list = []

    def add_report(self, report):
        report_entry = ReportEntry()
        # required fields
        report_entry.SourceID = report.header.agentID
        report_entry.TimeGen = report.header.timeUTC
        report_entry.TestID = report.header.testID
        report_entry.ID = report.header.reportID
        report_entry.Report = report
        # optional fields
        report_entry.SourceIP = report.header.passedNode[0]

        self.report_list.append(report_entry)

    def _insert_into_db(self, report_entry):
        sql_stmt = "insert into reports (report_id, \
                                         test_id, \
                                         time_gen, \
                                         content, \
                                         source_id, \
                                         source_ip, \
                                         status) \
                    values (%s, %s, )" % \
                    report.ID, \
                    report.TestID, \
                    report.TimeGen, \
                    MessageFactory.encode(report.Detail), \
                    report.SourceID, \
                    report.SourceIP, \
                    report.Status

        g_db_helper.execute(sql_stmt)

    def list_reports(self):
        for i in range(len(self.report_list)):
            print(str(i+1) + '. ' + str(self.report_list[i]))


if __name__ == "__main__":
    m = ReportManager()
    m._generate_report_id(['Nobody inspects',' the spammish repetition'])