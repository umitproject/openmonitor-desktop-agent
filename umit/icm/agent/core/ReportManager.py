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

import hashlib
import time

from umit.icm.agent.Global import g_logger, g_db_helper

########################################################################
class ReportEntry(object):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = 0
        self.Type = None
        self.TimeGen = None
        self.Detail = None
        self.SourceID = None
        self.SourceIP = None
        self.Status = ReportStatus.UNSENT
        
class ReportStatus:
    UNSENT = 0
    SENT_TO_AGGREGATOR = 1
    SENT_TO_SUPER_AGENT = 2
    SENT_TO_AGENT = 3    
        
########################################################################
class ReportManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self._report_list = []        
        
    def add_report(self, param):        
        report_entry = ReportEntry()
        # required fields
        report_entry.Type = param['type']
        report_entry.SourceID = param['source_id']
        report_entry.Detail = param['detail']
        # optional fields
        report_entry.SourceIP = param.get('source_ip', '')
        report_entry.TimeGen = param.get('time_gen', int(time.time()))
        # get report ID or generate one
        report_entry.ID = param.get('report_id', 
                                    generate_report_id([report_entry.SourceID, 
                                                        report_entry.Type,
                                                        report_entry.TimeGen]))
        self._report_list.append(report_entry)
        
    def get_report_list(self):
        return self._report_list
        
    def generate_report_id(self, list_):
        m = hashlib.md5()
        for item in list_:
            m.update(item)
        report_id = m.hexdigest()
        return report_id
    
    def insert_into_db(self, report):
        sql_stmt = "insert into reports (report_id, \
                                         report_type, \
                                         time_gen, \
                                         content, \
                                         source_id, \
                                         source_ip, \
                                         status) \
                    values (%s, %s, )" % \
                    report.ID, \
                    report.Type, \
                    report.TimeGen, \
                    g_message_factory.encode(report.detail), \
                    report.SourceID, \
                    report.SourceIP, \
                    report.Status
        
        helper.execute(sql_stmt)
 
if __name__ == "__main__":
    m = ReportManager()
    m.generate_report_id(['Nobody inspects',' the spammish repetition'])