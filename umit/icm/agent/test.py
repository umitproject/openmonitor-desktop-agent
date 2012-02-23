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

try:
    execfile("F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py")
except:
    pass

__all__ = ['test_by_id', 'test_name_by_id', 'WebsiteTest', 'ServiceTest']

TEST_PACKAGE_VERSION = '1.0'
TEST_PACKAGE_VERSION_NUM = 1

import hashlib
import re
import sys
import time

from twisted.internet import reactor, ssl
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol, ClientCreator, ClientFactory
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

def task_done(name):
    theApp.statistics.tasks_done = theApp.statistics.tasks_done + 1
    theApp.statistics.tasks_done_by_type[name] = \
        theApp.statistics.tasks_done_by_type.get(name, 0) + 1

def task_failed(name):
    theApp.statistics.tasks_failed = theApp.statistics.tasks_failed + 1
    theApp.statistics.tasks_failed_by_type[name] = \
        theApp.statistics.tasks_failed_by_type.get(name, 0) + 1

def generate_report_id(list_):
    m = hashlib.md5()
    for item in list_:
        m.update(str(item))
    report_id = m.hexdigest()
    return report_id

#---------------------------------------------------------------------
class Test(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    def prepare(self, param):
        """Setup parameters and prepare for running"""
        raise NotImplementedError('You need to implement this method')

    def execute(self):
        raise NotImplementedError('You need to implement this method')

########################################################################
# Website Test
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
        defer_.addErrback(self._connectionFailed)
        return defer_

    def _connectionFailed(self, failure):
        task_failed(self.__class__.__name__)
        result = {'status_code': 1, 'time_end': default_timer()}
        return self._generate_report(result)

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

        HTTP_SUCCESS_CODE = (200, 302)
        if response.code in HTTP_SUCCESS_CODE:
            task_done(self.__class__.__name__)
            #if self.pattern is not None:
                #response.deliverBody(ContentExaminer(self.url,
                                                     #self.pattern))
        else:
            task_failed(self.__class__.__name__)
        return report

    def _generate_report(self):
        report = WebsiteReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())
        report.header.timeZone = 8
        report.header.testID = 1
        report.header.reportID = generate_report_id([report.header.agentID,
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
# Service Test
########################################################################

class ServiceTest(Test):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.service_name = None
        self.host = None
        self.port = 0
        self.username = ''
        self.password = ''
        self._done = False

    def prepare(self, param):
        self.host = param['host']
        if 'port' in param:
            self.port = param['port']
        if 'username' in param:
            self.username = param['username']
        if 'password' in param:
            self.password = param['password']

    def checkArgs(self):
        if not self.host or not self.port:
            g_logger.warning("%s test missing Host and Port." %
                             self.service_name)
            return False

        if not self.username or not self.password:
            g_logger.warning("%s test missing credentials. Host: %s, Port: %d" %
                             self.service_name, self.host, self.port)
            return False

        return True

    def execute(self):
        raise NotImplementedError

    def _connectionFailed(self, failure):
        task_failed(self.__class__.__name__)
        result = {'status_code': 1, 'time_end': default_timer()}
        self.reportDeferred.callback(result)

    def _generateReport(self, result):
        report = ServiceReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())
        report.header.timeZone = 8
        report.header.testID = 2
        report.header.reportID = generate_report_id([report.header.agentID,
                                                     report.header.timeUTC,
                                                     report.header.testID])
        #report.header.traceroute
        report.report.serviceName = self.service_name
        report.report.statusCode = result['status_code']
        report.report.responseTime = \
              int((result['time_end'] - self.time_start) * 1000)
        #...
        theApp.statistics.reports_generated = \
              theApp.statistics.reports_generated + 1
        return report

########################################################################
# FTP Test
########################################################################
from twisted.protocols.ftp import FTPClient, FTPClientBasic

class FTPTestProtocol(FTPClient):
    """"""
    test = None
    reportDeferred = None

    #----------------------------------------------------------------------
    def __init__(self, report_deferred=None, test=None):
        """Constructor"""
        FTPClient.__init__(self, test.username, test.password)
        self.reportDeferred = report_deferred
        self.test = test

    def lineReceived(self, line):
        print(line)
        FTPClient.lineReceived(self, line)
        if line.startswith('230'): # Logged in
            self.quit()
            task_done(self.test.__class__.__name__)
            if self.reportDeferred:
                result = {'status_code': 0, 'time_end': default_timer()}
                self.reportDeferred.callback(result)
        elif line.startswith('530'): # Login failed
            task_failed(self.test.__class__.__name__)
            if self.reportDeferred:
                result = {'status_code': 1, 'time_end': default_timer()}
                self.reportDeferred.callback(result)

class FTPTest(ServiceTest):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        ServiceTest.__init__(self)
        self.service = 'ftp'
        self.port = 21
        self.username = 'anonymous'
        self.password = 'icm-agent@umitproject.org'

    def execute(self):
        if not self.checkArgs():
            return

        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, FTPTestProtocol, self.reportDeferred, self)\
                     .connectTCP(self.host, self.port)\
                     .addErrback(self._connectionFailed)
        self.time_start = default_timer()
        self.time_end = 0
        return self.reportDeferred

########################################################################
# SMTP Test
########################################################################
from twisted.mail.smtp import SMTPClient, ESMTPClient

class SMTPTestProtocol(ESMTPClient):
    """"""
    test = None
    reportDeferred = None

    def __init__(self, report_deferred=None, test=None):
        ESMTPClient.__init__(self, test.password,
                             ssl.ClientContextFactory(),
                             test.username)
        self.reportDeferred = report_deferred
        self.test = test

    def getMailFrom(self):
        return "icmdesktopagent@umitproject.org"

    def getMailTo(self):
        return "nonexist@umitproject.org"

    def sentMail(self, code, resp, numOk, addresses, log):
        if self.reportDeferred:
            task_done(self.test.__class__.__name__)
            result = {'status_code': 0, 'time_end': default_timer()}
            self.reportDeferred.callback(result)
            self.reportDeferred = None
        self._disconnectFromServer()

    #def lineReceived(self, line):
        #print(line)
        #ESMTPClient.lineReceived(self, line)

class SMTPTest(ServiceTest):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        ServiceTest.__init__(self)
        self.service_name = 'smtp'
        self.port = 25

    def execute(self):
        if not self.checkArgs():
            return

        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, SMTPTestProtocol, self.reportDeferred, self)\
                     .connectTCP(self.host, self.port)\
                     .addErrback(self._connectionFailed)
        self.time_start = default_timer()
        self.time_end = 0
        return self.reportDeferred

########################################################################
# POP3 Test
########################################################################
from twisted.mail.pop3client import POP3Client

class POP3TestProtocol(POP3Client):
    """"""
    test = None
    reportDeferred = None

    #----------------------------------------------------------------------
    def __init__(self, report_deferred=None, test=None):
        """Constructor"""
        self.reportDeferred = report_deferred
        self.test = test

    def serverGreeting(self, greeting):
        POP3Client.serverGreeting(self, greeting)
        login = self.login(self.test.username, self.test.password)
        login.addCallback(self._loggedIn)
        login.addErrback(self._loginFailed)

    def _loggedIn(self, res):
        if self.reportDeferred:
            task_done(self.test.__class__.__name__)
            result = {'status_code': 0, 'time_end': default_timer()}
            self.reportDeferred.callback(result)
        self.quit()

    def _loginFailed(self, failure):
        if self.reportDeferred:
            task_failed(self.test.__class__.__name__)
            result = {'status_code': 1, 'time_end': default_timer()}
            self.reportDeferred.callback(result)

    #def lineReceived(self, line):
        #print(line)
        #POP3Client.lineReceived(self, line)

class POP3Test(ServiceTest):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        ServiceTest.__init__(self)
        self.service = 'pop3'
        self.port = 110

    def execute(self):
        if not self.checkArgs():
            return

        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, POP3TestProtocol, self.reportDeferred, self)\
                     .connectTCP(self.host, self.port)\
                     .addErrback(self._connectionFailed)
        self.time_start = default_timer()
        self.time_end = 0
        return self.reportDeferred

########################################################################
# IMAP Test
########################################################################
from twisted.mail.imap4 import IMAP4Client, CramMD5ClientAuthenticator

class IMAPTestProtocol(IMAP4Client):
    """"""
    test = None
    reportDeferred = None

    #----------------------------------------------------------------------
    def __init__(self, report_deferred=None, test=None):
        IMAP4Client.__init__(self, ssl.ClientContextFactory())
        self.username = username
        self.password = password
        self.reportDeferred = report_deferred
        self.test = test

    def serverGreeting(self, caps):
        IMAP4Client.serverGreeting(self, caps)
        login = self.login(self.test.username, self.test.password)
        login.addCallback(self._loggedIn)
        login.addErrback(self._loginFailed)

    def _loggedIn(self, res):
        if self.reportDeferred:
            task_done(self.test.__class__.__name__)
            result = {'status_code': 0, 'time_end': default_timer()}
            self.reportDeferred.callback(result)
        self.logout()

    def _loginFailed(self, failure):
        if self.reportDeferred:
            task_failed(self.test.__class__.__name__)
            result = {'status_code': 1, 'time_end': default_timer()}
            self.reportDeferred.callback(result)

    #def lineReceived(self, line):
        #print(line)
        #IMAP4Client.lineReceived(self, line)

class IMAPTest(ServiceTest):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        ServiceTest.__init__(self)
        self.service = 'imap'
        self.port = 143

    def execute(self):
        if not self.checkArgs():
            return

        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, IMAPTestProtocol, self.reportDeferred, self)\
                     .connectTCP(self.host, self.port)\
                     .addErrback(self._connectionFailed)
        self.time_start = default_timer()
        self.time_end = 0
        return self.reportDeferred


test_by_id = {
    0: Test,
    1: WebsiteTest,
    2: ServiceTest,
    3: FTPTest,
    4: SMTPTest,
    5: POP3Test,
    6: IMAPTest,
}

test_name_by_id = {
    0: 'Test',
    1: 'WebsiteTest',
    2: 'ServiceTest',
    3: 'FTPTest',
    4: 'SMTPTest',
    5: 'POP3Test',
    6: 'IMAPTest',
}

ALL_TESTS = ['WebsiteTest', 'FTPTest', 'SMTPTest', 'POP3Test', 'IMAPTest']
SUPPORTED_SERVICES = ['FTP', 'SMTP', 'POP3', 'IMAP']
#import inspect
#clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
#for clsname,cls in clsmembers:
    #if clsname.endswith('Test') and clsname != 'Test':
        #ALL_TESTS.append(clsname)


if __name__ == "__main__":
    #test1 = WebsiteTest()
    #test1.prepare({'url': 'http://www.baidu.com', 'pattern': 'baidu'})
    #test1.execute()
    #test2 = WebsiteTest()
    #test2.prepare({'url': 'https://www.alipay.com', 'pattern': 'baidu'})
    #test2.execute()
    #test3 = FTPTest()
    #test3.prepare({'host': 'ftp.secureftp-test.com', 'port': 21,
                   #'username': 'test', 'password': 'test'})
    #test3.execute()

    #reactor.callLater(5, reactor.stop)
    reactor.run()
    g_logger.info("finished")