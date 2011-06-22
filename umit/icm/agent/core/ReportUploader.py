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

from umit.icm.agent.Global import *

########################################################################
class ReportUploader(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, report_manager):
        """Constructor"""
        self.report_manager = report_manager
        self._failed_list = []
        self._stop_flag = False

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

    #----------------------------------------------------------------------
    def run(self):
        """"""
        while not self._stop_flag:  # run until the stop method is called
            report_entry = self.fetch_one_report()

            if report_entry is None:
                time.sleep(1)
            else:
                self.send_report(report_entry)

    def stop(self):
        self._stop_flag = True

