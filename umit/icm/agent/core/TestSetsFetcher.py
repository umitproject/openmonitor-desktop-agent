#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Tianwei Liu <liutianweidlut@gmail.com> 
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

import random

TEST_WEB_TYPE     = "WEB"
TEST_SERVICE_TYPE = "SERVICE" 

class TestSetsFetcher(object):
    """"""
  
    implements(IConsumer)
    
    def __init__(self,task_manager,report_manager):
        
        self.task_manager   = task_manager
        self.report_manager = report_manager
        self.current_test_version = self.get_current_test_version()
    
    def execute_test(self,message):
        """
        execute this test right now or randomly timeout
        """
        if message is None:
            return 
        
        g_logger.debug("The received Test Sets are:%s"%str(message))
        
        if message.testVersionNo > self.current_test_version:
            g_logger.info("[Higher Version]Start to execute the tests(%d > %d)"%(message.testVersionNo,self.current_test_version))
            self.set_test_version(message.testVersionNo)
            for test in message.tests:  #tests is a list 
                self.parse_test_message(test)
        else:
            g_logger.info("[Lower Version]Avoid these tests(%d <= %d)"%(message.testVersionNo,self.current_test_version))
        
    
    def fetch_tests(self):
        """
        Fetch New Test Sets from Aggregator(Keep polling the aggregator)
        Agent must constantly execute it.
        """
        if theApp.aggregator.available:
            g_logger.info("Fetching new test sets from aggregator")
            
            #The real check_tests by using check_tests Aggregator API
            defer_ = theApp.aggregator.check_tests(self.current_test_version)
            defer_.addCallback(self.execute_test)
            defer_.addErrback(self._handler_error)
            
            #Test by manual
            #self.execute_test(self.test_by_manually())
           
        else:
            g_logger.info("Cannot Fetching new test sets from aggregator") 
    
    def _handler_error(self,failure):
        
        g_logger.error("Fetch new test sets error %s"%str(failure))
        
    def get_current_test_version(self):
        
        version = g_config.get("Test","test_current_version")
        return int(version)
        
    def set_test_version(self,version):
        
        self.current_test_version = version
        g_logger.info("Save current test version: %s"%(str(self.current_test_version))) 
        g_config.set('Test', 'test_current_version', str(self.current_test_version))
    
    def test_by_manually(self):
        """
        This is the test by manually, it can testify the execute_test function can work right.
        """
        from google.protobuf.text_format import MessageToString
        
        from umit.icm.agent.rpc.message import *
        from umit.icm.agent.rpc.MessageFactory import MessageFactory
        from umit.icm.agent.rpc import messages_pb2
        
        #simulate the network delay
        #time.sleep(2)
        
        #Generate NewTestsResponse(
        tests_response = NewTestsResponse()
        tests_response.testVersionNo = random.randint(1,10000)    #Random test version num 
        if tests_response.testVersionNo > 5000:
            tests_response.testVersionNo = tests_response.testVersionNo - 3000
               
        #website Test
        #test = tests_response.tests.add()
        #test.testID = 1
        #test.website.url = "http://www.baidu.com/"
        #test.testType = 'WEB'
        
        #Service Test:FTP
        #test = tests_response.tests.add()
        #test.testID = 2
        #test.service.name = 'ftp'
        #test.service.port = 21121
        #test.service.ip   = '202.118.67.200'
        #test.testType = 'Service'
        
        #Service Test:IRC,SSH
        #test = tests_response.tests.add()
        #test.testID = 4
        #test.service.name = 'ssh'
        #test.service.port = 23
        #test.service.ip   = '192.168.24.129'
        #test.testType = 'Service'   
        
        #Service Test: SMTP, POP3, IMAP
        test = tests_response.tests.add()
        test.testID = str("1186fe21-9099-4442-93ca-75705c33cb73")
        
        #test.service.name = 'pop3'
        #test.service.port = 111
        #test.service.ip   = 'pop3.sohu.com'
        
        #test.service.name = 'smtp'
        #test.service.port = 25
        #test.service.ip   = 'smtp.sohu.com'
        
        test.service.name = 'imap'
        test.service.port = 143
        test.service.ip   = 'imap.163.com3'        
        test.testType = 'Service' 
             
        return tests_response
        
        
    def parse_test_message(self,test):
        """
        parse the test message and add it into task_manager
        
        """
        from umit.icm.agent.test import *
        ##############
        ##Execute Time 
        if test.executeAtTimeUTC == None:
            executeAtTimeUTC = 0 
        else:
            executeAtTimeUTC = test.executeAtTimeUTC
        
        ####################
        ##Website Task Parse
        if test.website and test.testType == TEST_WEB_TYPE:
            args = {
                    'url':str(test.website.url),
                    'unitied_test_id':str(test.testID)
                    }
            #crontime = self.random_cron_time(executeAtTimeUTC)
            #In test.py logical , we can call the according test functions
            g_logger.debug("[Parse Test sets]:The authorized WebsiteTest from aggregator:%s"%str(test))
                        
            test_moduler = WebsiteTest()
            test_moduler.prepare(args)
            defer_website_ = test_moduler.execute()
            if defer_website_ is not None:
                defer_website_.addCallback(self.report_manager.add_report)
    
        ####################
        ##Service Task Parse        
        elif test.service and (test.testType).upper() == TEST_SERVICE_TYPE:
            args = {
                   #'service':test.service.name,
                    'host':test.service.ip,
                    'port':test.service.port,
                    'unitied_test_id':test.testID,
                    }
            #crontime = self.random_cron_time(executeAtTimeUTC)
            #In test.py logical , we can call the according test functions
            service_name = (test.service.name).upper()      #we unify the service name
            if service_name in service_name_by_id.keys():
                g_logger.debug("[Parse Test sets]:The authorized Service(%s) from aggregator:%s"%(service_name,str(test)))                
                test_moduler = test_by_id[service_name_by_id[service_name]]()
                test_moduler.prepare(args)
                defer_service_ = test_moduler.execute()
                if defer_service_ is not None:
                    defer_service_.addCallback(self.report_manager.add_report)
            else:
                g_logger.debug('Sorry, the current version cannot support %s service now'%(service_name))

    def random_cron_time(self,utc_time):
        """"""

        crontime = ""
        
        return crontime
                                    

    
    
    
    
    
    
    
    
    
      