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

import re
import sys
import time

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, HTTPDownloader
from twisted.web.http_headers import Headers
from twisted.web._newclient import ResponseDone

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

    def execute(self):
        """Need to be implemented"""

########################################################################
class WebsiteTest(Test):
    def __init__(self):
        """Constructor"""
        self.url = None
        self.status_code = 0
        self.pattern = None
        self._done = False
        self._agent = Agent(reactor)

    def prepare(self, param):
        """Prepare for the test"""
        self.url = param['url']
        if 'pattern' in param:
            self.pattern = re.compile(param['pattern'])

    def execute(self):
        """Run the test"""
        g_logger.info("Testing website: %s" % self.url)
        d = self._agent.request('GET',
                                self.url,
                                Headers({'User-Agent':
                                         ['ICM Website Test']}),
                                None)
        self.time_start = default_timer()
        d.addCallback(self.handle_response)
        d.addErrback(g_logger.error)
        #d._time_start = default_timer()

    def handle_response(self, response):
        """Result Handler (generate report)"""
        time_end = default_timer()
        self.status_code = response.code
        self.response_time = time_end - self.time_start
        print(self.url)
        print(str(self.status_code) + ' ' + response.phrase)
        print("Response time: %fs" % (self.response_time))
        print(response.headers)

        if response.code == 200:
            if self.pattern is not None:
                response.deliverBody(ContentExaminer(self.url,
                                                     self.pattern))
        self._done = True

    def isDone(self):
        return self._done

    def generate_report(self):
        report = WebsiteReportDetail()
        report.websiteURL = self.url
        report.statusCode = self.status_code
        report.responseTime = (int)(self.response_time * 1000)
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

def check_tests_done(tests):
    for each in tests:
        if each.isDone():
            print(each.url + "...done")
            print(each.generate_report())
    reactor.stop()

test_by_id = {
    0: Test,
    1: WebsiteTest,
    2: ServiceTest,
    3: Diagnose
}

test_name_by_id = {
    0: 'Test',
    1: 'WebsiteTest',
    2: 'ServiceTest',
    3: 'Diagnose'
}


if __name__ == "__main__":
    test1 = WebsiteTest()
    test1.prepare({'url': 'http://www.baidu.com', 'pattern': 'baidu'})
    test1.execute()
    test2 = WebsiteTest()
    test2.prepare({'url': 'https://www.alipay.com', 'pattern': 'baidu'})
    test2.execute()

    reactor.callLater(5, check_tests_done, [test1, test2])
    reactor.run()
    g_logger.info("finished")