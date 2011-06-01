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

from umit.icm.agent.comm.report_pb2 import ICMReport

class Report:
    """"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
if __name__ == "__main__":
    report = ICMReport()
    report.reportID = 89734
    report.senderID = 10000
    report.timestamp = long(time.time() * 1000)
    report.testID = 100
    report.passedNode.append("219.223.222.99:6060")
    report.passedNode.append("219.223.192.198:6060")
    wr = report.websiteReport.add()
    wr.websiteURL = "http://www.baidu.com"
    wr.statusCode = 200
    wr = report.websiteReport.add()
    wr.websiteURL = "https://www.alipay.com"
    wr.statusCode = 200
    print(report.__str__())
    