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

#single file test
from utils.importertest import import_debug
import_debug() 

__all__ = ['test_by_id', 'test_name_by_id', 'WebsiteTest', 'ServiceTest','ThrottledTest']

TEST_PACKAGE_VERSION = '1.0'
TEST_PACKAGE_VERSION_NUM = 1

import hashlib
import re
import sys
import time
import struct

from twisted.internet import reactor, ssl
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol, ClientCreator, ClientFactory
from twisted.web.client import Agent, HTTPDownloader,downloadPage
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
import tempfile

benchmark_url_dict={
                    1:'http://www.baidu.com/',
                    2:'http://www.bing.com/',
                    3:'http://www.google.com/',
                    4:'http://www.sohu.com/',
                    5:'http://www.yahoo.com/',
                    6:'http://www.people.com.cn/'}

class WebsiteTest():
    def __init__(self):
        """Constructor"""
        self.url = None
        self.status_code = 0
        self.pattern = None
        self.benchmark_num = len(benchmark_url_dict)
        self.benchmark_bandwidth = self.info_dict()  #benchmark speed
        self.test_id = self.benchmark_num + 1
        
        self.bandwidth = 0
        self.report = None
        self.finished_num = 0
        self._agent = Agent(reactor)

    def info_dict(self):
        """"""
        tmp_dict = {}
        for i in range(1,self.benchmark_num+2):
            tmp_dict[i] = {"start_time":0,
                           "end_time":0,
                           "size":0,
                           "bandwidth":0}
            
        return tmp_dict
    
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
        
        g_logger.error("[WebsiteTest]connection failed:%s"%failure)
        
        task_failed(self.__class__.__name__)

        result = {'status_code': 1, 'time_end': default_timer()}
        
        self.status_code = 1
        
        return self._generate_report(result)

    def _handle_response(self, response):
        """Result Handler (generate report)"""
        time_end = default_timer()
        self.status_code = response.code
        self.response_time = time_end - self.time_start
        
        g_logger.debug(self.url)
        g_logger.debug((str(self.status_code) + ' ' + response.phrase))
        g_logger.debug("Response time: %f" % (self.response_time))
        g_logger.debug(response.headers)
        
        result = {'status_code': 0, 'time_end': time_end}
        
        self.report = self._generate_report(result)
        
        HTTP_SUCCESS_CODE = (200,302)
        if int(response.code) in HTTP_SUCCESS_CODE:
            
            g_logger.debug('task done %s'%response.code)
            
            #if self.pattern is not None:
                #response.deliverBody(ContentExaminer(self.url,self.pattern))
            
            #Here we can test the HTTP throttled 
            self._throttled_http_test()
        else:
            task_failed(self.__class__.__name__)
            g_logger.error("task failed!")
            
        return self.report

    def _throttled_http_test(self):
        """
        HTTP throttled test
        """
        throttled_test = g_config.getboolean('application', 'load_http_throttled_test')
        if throttled_test:
            g_logger.info("start HTTP download throttled test!")
            
            #benchmark test
            new_index = self.benchmark_num +1
            benchmark_url_dict[new_index] = self.url
            
            for key in benchmark_url_dict.keys():
                defer_ = self.download_page_to_tmp(key)
                defer_.addCallback(self.store_bandwidth,key)
                defer_.addCallback(self.handle_count)
                defer_.addErrback(self.handler_err)
            
    def handle_count(self,result):
        self.finished_num = self.finished_num + 1
        if self.finished_num == self.test_id:
            self.calculate_different()
            
    def store_bandwidth(self,result,key):
        
        g_logger.debug('finish %s'%benchmark_url_dict[key])
        
        start_time = self.benchmark_bandwidth[key]['start_time']
        end_time = self.benchmark_bandwidth[key]['end_time']
        size = self.benchmark_bandwidth[key]['size']
        if size == 0 or size == None:
            raise Exception("Error in filesize!!!")
        
        self.benchmark_bandwidth[key]['bandwidth'] =(float)((end_time - start_time) / size)
        
        g_logger.debug(key+':'+self.benchmark_bandwidth[key])
        
    
    def calculate_different(self):
        """
        calculate the different http download: sum, average, variance
        We can add more complicated algorithm
        """
        g_logger.debug("finish all benchmark http download throttled test")
        
        diff_value = 0
        sum = 0
        
        for key in range(1,self.benchmark_num+1):
            sum = sum + self.benchmark_bandwidth[key]['bandwidth']
        
        
        diff_value = self.benchmark_bandwidth[self.test_id]['bandwidth'] - sum/(self.benchmark_num)
        
        self.report.report.bandwidth = diff_value
        
    def _generate_report(self,result):
        """"""
        
        report = WebsiteReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(default_timer())    #here should UTC clock?
        report.header.timeZone =  -(time.timezone/3600)  #8
        report.header.testID = 1
        report.header.reportID = generate_report_id([report.header.agentID,
                                                     report.header.timeUTC,
                                                     report.header.testID])
        #report.header.traceroute
        report.report.websiteURL = self.url
        report.report.statusCode = self.status_code
        
        report.report.responseTime = \
              int((result['time_end'] - self.time_start) * 1000)
        
        report.report.bandwidth = None
              
        #...
        theApp.statistics.reports_generated = \
              theApp.statistics.reports_generated + 1
        return report
    
    def download_page_to_tmp(self,key):
        """"""
        url = benchmark_url_dict[key]
        tmpfd,tmpname = tempfile.mkstemp()
        os.close(tmpfd)
        
        self.benchmark_bandwidth[key]['start_time'] = time.time()
        defer_ = client.downloadPage(url, tmpname)
        defer_.addCallback(self.finish_page_download,key,tmpname)
        defer_.addErrback(self.handler_err)
        
        return defer_
    
    def finish_page_download(self,result,key,filename):
        
        #end time
        self.benchmark_bandwidth[key]['end_time'] = time.time() 
        #calculate the file size
        self.benchmark_bandwidth[key]['size'] = os.path.getsize(filename)
        #delete the file
        os.unlink(filename)
        
        return key
        
    def handler_err(self,failure):
        g_logger.error("[WebsiteTest]bench handle failed:%s"%failure)        

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
                    print ("Content unchanged.")
                else:
                    print ("Content changed.")
            else:
                print ("The connection was broken. [%s]" % self.url)


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
        raise NotImplementedError('You need to implement this method')

    def _connectionFailed(self, failure):
        task_failed(self.__class__.__name__)
        result = {'status_code': 1, 'time_end': default_timer()}
        self.reportDeferred.callback(result)

    def _generateReport(self, result):
        report = ServiceReport()
        report.header.agentID = theApp.peer_info.ID
        report.header.timeUTC = int(time.time())    #here should UTC clock?
        report.header.timeZone = -(time.timezone/3600)  #8
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
# Throttling  Test
########################################################################

class ThrolledTest(Test):
    """"""
    def __init__(self):
        """Constructor"""
        self.service_name = None
        self.host = None
        self.port = None
        self.website_url = None
    
    def prepare(self):
        pass
    
    def execute(self):
        raise NotImplementedError('You need to implement this method')

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

########################################################################
# SSH Test
########################################################################
from twisted.conch.ssh.transport import SSHClientTransport
from twisted.conch.ssh import userauth, connection, common, keys, channel,transport
from getpass import getpass
SSH_USER = 'umitgit'
SSH_HOST = "dev.umitproject.org"

class SSHTestProtocol(SSHClientTransport):
    
    def verifyHostKey(self,host_key,fingerprint=""):
        g_logger.info("host key fingerprint %s" % fingerprint)
        return defer.succeed(1)
         
    def connectionSecure(self):
        self.requestService(SSHUserAuth(SSH_USER,SSHConnection()))

class SSHUserAuth(userauth.SSHUserAuthClient):
    def getPassword(self):
        return defer.succeed( getpass("password: ") )    
    def getPublicKey(self):
        return #empty implement

class SSHConnection(connection.SSHConnection):
    def serviceStarted(self):
        self.openChannel(TrueChannel(2**16, 2**15, self))

class Channel(channel.SSHChannel):
    name = 'session'    # needed for commands

    def openFailed(self, reason):
        print 'open channel failed', reason
    
    def channelOpen(self, ignoredData):
        self.conn.sendRequest(self, 'exec', common.NS('true'))

    def request_exit_status(self, data):
        status = struct.unpack('>L', data)[0]
        print 'true status was: %s' % status
        self.loseConnection()
        
    def closed(self):
        self.loseConnection()

class SSHTest(ServiceTest):
    def __init__(self):
        """Constructor"""
        ServiceTest.__init__(self)
        self.service_name = 'ssh'
        self.username = SSH_USER
        self.host = SSH_HOST
        self.port = 22
        
    def execute(self):
        if not self.checkArgs():
            return
        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, SSHTestProtocol, self.reportDeferred, self)\
                     .connectTCP(self.host, self.port)\
                     .addErrback(self._ssh_failure_process)        
        self.time_start = default_timer()
        self.time_end = 0
        return self.reportDeferred     
    
    #process the failure result: check the reason for SSH
    def _ssh_failure_process(self,failure):
        from twisted.internet import error as SSHError
        #there may be some bugs in here, we should test it in different network environment
        if isinstance(failure,SSHError.TimeoutError) or isinstance(failure,SSHError.DNSLookupError)  or\
        isinstance(failure, SSHError.NoRouteError):
            g_logger.info("SSH cannot access %s" % failure)
            self._connectionFailed(failure)
        else:
            #we cannot provide the key, so we should check the failure to decide the result
            if self.reportDeferred:
                task_done(self.__class__.__name__)
                result = {'status_code': 0, 'time_end': default_timer()}
                self.reportDeferred.callback(result)
            g_logger.info("SSH can access %s, some clues below:" % failure)  
        
########################################################################
# IRC Test
########################################################################
from twisted.words.protocols.irc import IRCClient

IRC_nickname = "icmagent_" + str(theApp.peer_info.ID)
IRC_channel = "umit"
IRC_host = "irc.freenode.net"

class IRCTestProtocol(IRCClient):
    """
    An automatical IRC bot
    """
    test = None
    reportDeferred = None        
    
    def __init__(self,reportDeferred = None ,test = None):
        self.reportDeferred = reportDeferred
        self.nick_name = test.username
        self.channel = test.channel
    
    def connectionMade(self):
        IRCClient.connectionMade(self)
    
    def connectionLost(self):
        IRCClient.connectionLost(self,reason)    
        
    #callbacks for events
    def signedOn(self):
        """
        call when irc bot has successfully signed on to server
        """
        if self.reportDeferred:
            task_done(self.test.__class__.__name__)
            result = {'status_code': 0, 'time_end': default_timer()}
            self.reportDeferred.callback(result)
        self.quit()
    
    def joined(self,channel):
        g_logger.info("[ServiceTest:IRC]The icm-agent has joined:" % (channel))  
      
    #IRC callback    
    def irc_NICK(self,prefix,params):
        """
        called when an IRC user changes their nickname
        """
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        g_logger.info("[ServiceTest:IRC]%s is now known as %s:" % (old_nick,new_nick))  
                
    def alterCollidedNick(self,nickname):
        """
        same nickname in irc server channel
        """
        return nickname + "^"

class IRCTest(ServiceTest):
    def __init__(self):
       ServiceTest.__init__(self)
       self.service_name = 'irc'
       self.host = IRC_host
       self.port = 6667
       self.channel = IRC_channel
       self.username = IRC_nickname
        
    def execute(self):
        if not self.checkArgs():
            return
        self.reportDeferred = Deferred().addCallback(self._generateReport)
        ClientCreator(reactor, IRCTestProtocol, self.reportDeferred, self)\
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
    7: IRCTest,
    8: SSHTest,
    9: ThrolledTest,
  #  10: HTTPThrottledTest,
}

test_name_by_id = {
    0: 'Test',
    1: 'WebsiteTest',
    2: 'ServiceTest',
    3: 'FTPTest',
    4: 'SMTPTest',
    5: 'POP3Test',
    6: 'IMAPTest',
    7: 'IRCTest',
    8: 'SSHTest',
    9:'ThrolledTest',
   # 10: 'HTTPThrottledTest',
}

ALL_TESTS = ['WebsiteTest', 'FTPTest', 'SMTPTest', 'POP3Test', 'IMAPTest',
             'IRCTest','SSHTest']
SUPPORTED_SERVICES = ['FTP', 'SMTP', 'POP3', 'IMAP','IRC','SSH']
SUPPORTED_THROTTLED = ['HTTP']

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