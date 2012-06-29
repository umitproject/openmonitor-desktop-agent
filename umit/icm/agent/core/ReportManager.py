#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
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

import base64
import time

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

class ReportStatus:
    UNSENT = 'Unsent'
    SENT_TO_AGGREGATOR = 'SentToAggregator'
    SENT_TO_SUPER_AGENT = 'SentToSuperAgent'
    SENT_TO_AGENT = 'SentToAgent'

class ReportEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = ''
        self.SourceID = ''
        self.TimeGen = 0
        self.TestID = ''
        self.Report = ''
        self.SourceIP = ''
        self.Status = ReportStatus.UNSENT

    def __str__(self):
        return "(id='%s', source_id='%s', time_gen='%s', test_id='%s', "\
               "report='%s', source_ip='%s', status='%s')" % \
               (self.ID,
                self.SourceID,
                time.ctime(self.TimeGen),
                self.TestID,
                self.Report,
                self.SourceIP,
                self.Status)

#---------------------------------------------------------------------
class ReportManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.cached_reports = {}

    def add_report(self, report):
        """
        Task scheduler calls this callback 
        """
        g_logger.debug("call add report is%s"%report)
        
        # check if in the cache
        if report is None:
            g_logger.critical("Received None as report. Please, investigate.")
            return

        if report.header.reportID in self.cached_reports:
            g_logger.info("ReportID '%s' already in cache." %
                          report.header.reportID)
            return
        # check if in the db
        if g_db_helper.select("select * from reports where report_id='%s'" % \
                              report.header.reportID):
            g_logger.info("ReportID '%s' already in db." %
                          report.header.reportID)
            return
        report_entry = ReportEntry()
        # required fields
        report_entry.SourceID = report.header.agentID
        report_entry.TimeGen = report.header.timeUTC
        report_entry.TestID = report.header.testID
        report_entry.ID = report.header.reportID
        report_entry.Report = report
        # optional fields
        #report_entry.SourceIP = report.header.passedNode[0]

        self.cached_reports[report_entry.ID] = report_entry
        self.save_report_to_db('unsent_reports', report_entry)
        theApp.statistics.reports_total = theApp.statistics.reports_total + 1
        theApp.statistics.reports_in_queue = \
              theApp.statistics.reports_in_queue + 1

    def remove_report(self, report_id, new_stat=ReportStatus.UNSENT):
        if report_id in self.cached_reports:
            report_entry = self.cached_reports[report_id]
            report_entry.Status = new_stat
            self.save_report_to_db('reports', report_entry)
            g_db_helper.execute(\
                "delete from unsent_reports where report_id='%s'" % report_id)
            g_db_helper.commit()
            #print("%s deleted from cache" % report_id)
            del self.cached_reports[report_id]
            theApp.statistics.reports_in_queue = \
                  theApp.statistics.reports_in_queue - 1

    def load_unsent_reports(self):
        rs = g_db_helper.select("select * from unsent_reports")
        for record in rs:
            report_entry = ReportEntry()
            report_entry.ID = record[0]
            report_entry.TestID = record[1]
            report_entry.TimeGen = record[2]
            report_entry.Report = MessageFactory.decode(base64.b64decode(record[3]))
            report_entry.SourceID = record[4]
            report_entry.SourceIP = record[5]
            report_entry.Status = record[6]
            self.cached_reports[report_entry.ID] = report_entry
        theApp.statistics.reports_in_queue = len(rs)
        g_logger.info("Loaded %d unsent reports from DB." % len(rs))

    def load_reports_from_db(self, table_name):
        rs = g_db_helper.select("select * from %s" % table_name)
        return rs

    def save_report_to_db(self, table_name, report_entry):
        sql_stmt = "insert into %s (report_id, test_id, time_gen, content, "\
                   "source_id, source_ip, status) values "\
                   "('%s', '%s', %d, '%s', '%s', '%s', '%s')" % \
                   (table_name,
                    report_entry.ID,
                    report_entry.TestID,
                    report_entry.TimeGen,
                    base64.b64encode(MessageFactory.encode(report_entry.Report)),
                    report_entry.SourceID,
                    report_entry.SourceIP,
                    report_entry.Status)

        g_db_helper.execute(sql_stmt)
        g_db_helper.commit()
        g_logger.debug("Save report '%s' to table '%s'." % (report_entry.ID,
                                                            table_name))

    def list_reports(self):
        for i in range(len(self.cached_reports)):
            print(str(i+1) + '. ' + str(self.cached_reports[i]))


if __name__ == "__main__":
    m = ReportManager()
    m._generate_report_id(['Nobody inspects',' the spammish repetition'])