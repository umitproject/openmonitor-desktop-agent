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

__all__ = ['test_by_id', 'test_name_by_id', 'WebsiteTest', 'ServiceTest']

TEST_PACKAGE_VERSION = '0.0'
TEST_PACKAGE_VERSION_INT = 1

import hashlib
import re
import sys
import time

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPDownloader
from twisted.web.http_headers import Headers
from twisted.web._newclient import ResponseDone

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.message import *

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

########################################################################
class Test(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    def prepare(self, param):
        """Setup parameters and prepare for running"""
        raise NotImplementedError

    def execute(self):
        """Need to be implemented"""
        raise NotImplementedError

########################################################################
class WebsiteTest(Test):
    def __init__(self):
        """Constructor"""
        self.url = None
        self.status_code = 0
        self.pattern = None
        self._agent = Agent(reactor)

    def prepare(self, param):
        """Prepare for the test"""
        self.url = param['url']
        if 'pattern' in param:
            self.pattern = re.compile(param['pattern'])

    def execute(self):
        """Run the test"""
        g_logger.info("Testing website: %s" % self.url)
        defer_ = self._agent.request('GET',
                                    self.url,
                                    Headers({'User-Agent':
                                             ['ICM Website Test']}),
                                    None)
        self.time_start = default_timer()
        defer_.addCallback(self._handle_response)
        defer_.addErrback(g_logger.error)
        return defer_

    def _handle_response(self, response):
        """Result Handler (generate report)"""
        time_end = default_timer()
        self.status_code = response.code
        self.response_time = time_end - self.time_start
        #print(self.url)
        #print(str(self.status_code) + ' ' + response.phrase)
        #print("Response time: %fs" % (self.response_time))
        #print(response.headers)
        report = self._generate_report()

        theApp.statistics.tests_done = theApp.statistics.tests_done + 1
        if 1 in theApp.statistics.tests_done_by_type:
            theApp.statistics.tests_done_by_type[1] = \
                  theApp.statistics.tests_done_by_type[1] + 1
        else:
            theApp.statistics.tests_done_by_type[1] = 0

        if response.code == 200:
            if self.pattern is not None:
                response.deliverBody(ContentExaminer(self.url,
                                                     self.pattern))
        return report

    def _generate_report_id(self, list_):
        m = hashlib.md5()
        for item in list_:
            m.update(str(item))
        report_id = m.hexdigest()
        return report_id

    def _generate_report(self):
        report = WebsiteReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())
        report.header.timeZone = 8
        report.header.testID = 1
        report.header.reportID = self._generate_report_id(\
            [report.header.agentID,
             report.header.timeUTC,
             report.header.testID])
        #report.header.traceroute
        report.report.websiteURL = self.url
        report.report.statusCode = self.status_code
        report.report.responseTime = (int)(self.response_time * 1000)
        #...
        theApp.statistics.reports_generated = \
              theApp.statistics.reports_generated + 1
        return report

class ContentExaminer(Protocol):
    def __init__(self, url, pattern):
        """Constructor"""
        self.url = url
        self.content = ""
        self.pattern = pattern

    def dataReceived(self, bytes):
        self.content = ''.join((self.content, bytes))

    def connectionLost(self, reason):
        if reason.check(ResponseDone):
            match = self.pattern.search(self.content)
            if (match is not None):
                g_logger.info("Content unchanged.")
            else:
                g_logger.info("Content changed.")
        else:
            g_logger.error("The connection was broken. [%s]" % self.url)

########################################################################
class ServiceTest(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service = None
        self._done = False

    def prepare(self, param):
        self.service = param['service']

    def execute(self):
        g_logger.info("Testing service: %s" % self.service)
        self.defer_ = defer.Deferred()
        return self.defer_

test_by_id = {
    0: Test,
    1: WebsiteTest,
    2: ServiceTest,
}

test_name_by_id = {
    0: 'Test',
    1: 'WebsiteTest',
    2: 'ServiceTest',
}


if __name__ == "__main__":
    test1 = WebsiteTest()
    test1.prepare({'url': 'http://www.baidu.com', 'pattern': 'baidu'})
    test1.execute()
    test2 = WebsiteTest()
    test2.prepare({'url': 'https://www.alipay.com', 'pattern': 'baidu'})
    test2.execute()

    reactor.callLater(5, reactor.stop)
    reactor.run()
    g_logger.info("finished")