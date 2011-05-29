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

import re
import sys
import time

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web._newclient import ResponseDone

from umit.icm.tests.BaseTest import BaseTest
from umit.icm.Logging import log

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

class WebsiteTest(BaseTest):
    def __init__(self):
        """Constructor"""
        self.targets = [];
        self._agent = Agent(reactor)
        
    def add_target(self, url, pattern=None):
        """Add a website target"""
        target = {'url': url, 'pattern_str': pattern, 'pattern': None, 
                  'done': False}
        if pattern is not None:
            target['pattern'] = re.compile(pattern)
        self.targets.append(target)
        
    def set_targets(targets):
        """Set the website targets"""
        self.targets = targets
        
    def prepare(self):
        """Prepare for the test"""
           
    def execute(self):
        """Run the test"""        
        for target in self.targets:
            log.info("Testing website: %s" % target['url'])
            d = self._agent.request('GET', 
                                    target['url'], 
                                    Headers({'User-Agent': 
                                             ['ICM Website Test']}), 
                                    None)
            target['time_start'] = default_timer()
            d.addCallback(self.handle_response, target)
            d.addErrback(log.error)
            #d._time_start = default_timer()            
    
    def handle_response(self, response, target):
        """Result Handler (generate report)"""
        time_end = default_timer()
        print(target['url'])
        print(str(response.code) + ' ' + response.phrase)
        print("Response time: %fs" % (time_end - target['time_start']))        
        print(response.headers)
        if response.code == 200:
            if target['pattern'] is not None:
                response.deliverBody(ContentExaminer(target['url'], 
                                                     target['pattern']))
        target['done'] = True
        
    def check_targets_done(self):
        flag = False
        while not flag:
            flag = True
            for target in self.targets:
                if not target['done']:
                    flag = False
            time.sleep(1)
        reactor.stop()        
        
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
                log.info("Content unchanged.")
            else:
                log.info("Content changed.")
        else:
            log.error("The connection was broken. [%s]" % self.url)
        

if __name__ == "__main__":
    test = WebsiteTest()
    test.add_target('http://www.baidu.com', 'baidu')
    test.add_target('https://www.alipay.com')
    test.execute()
    reactor.callInThread(test.check_targets_done)
    reactor.run()
    log.info("finished")
    
    