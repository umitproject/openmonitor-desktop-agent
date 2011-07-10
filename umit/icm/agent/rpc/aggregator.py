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
    execfile('E:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

import base64
import os
import sys

from twisted.web import client
from twisted.internet.defer import waitForDeferred

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.Session import Session

########################################################################
class AggregagorSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, transport):
        """Constructor"""
        Session.__init__(self, 0, transport)

    def handle_message(self, message):
        g_logger.debug("AggregatorSession - Handling %s message." %
                       message.DESCRIPTOR.name)
        if isinstance(message, AssignTask):
            pass
        elif isinstance(message, AgentUpdate):
            pass
        elif isinstance(message, TestModuleUpdate):
            pass
        elif isinstance(message, Notification):
            pass

    def close(self):
        pass

########################################################################
class AggregatorAPI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, url):
        """Constructor"""
        self.base_url = url
        self.available = False

    def _make_request_header(self, header):
        header.token = 'null' #theApp.peer_info.AuthToken
        header.agentID = 999999 #theApp.peer_info.ID

    def check_availability(self):
        url = self.base_url
        d = self._send_request('GET', url)
        d.addCallback(self._handle_check_availability)

    def _handle_check_availability(self, d):
        if d is not None:
            #if self.available == False:
            self.available = True
            g_logger.info("Aggregator is available.")
        else:
            self.available = False
            g_logger.info("Aggregator is not available.")

    """ Peer """
    #----------------------------------------------------------------------
    def register(self, username, password, email):
        g_logger.info("Sending RegisterAgent message to aggregator")
        url = self.base_url + "/registeragent/"
        request_msg = RegisterAgent()
        request_msg.ip = theApp.peer_info
        data = base64.b64encode(request_msg.SerializeToString())
        d = self._send_request('POST', url, data)

    def _handle_register(self, d):
        print(d)

    def authenticate(self):
        g_logger.info("Sending Authenticate message to aggregator")
        url = self.base_url + "/authenticate/"
        #request_msg = RegisterAgent()
        #data = base64.b64encode(request_msg.SerializeToString())
        #self._send_request('POST', url, data)
        return 'Succeeded'

    def report_peer_info(self):
        g_logger.info("Sending ReportPeerInfo message to aggregator")
        url = self.base_url + "/reportpeerinfo/"
        result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        g_logger.info("Sending GetSuperPeerList message to aggregator")
        url = self.base_url + "/getsuperpeerlist/"
        request_msg = GetSuperPeerList()
        self._make_request_header(request_msg.header)
        data = base64.b64encode(request_msg.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_get_super_peer_list)

    def _handle_get_super_peer_list(self, result):
        if result is not None:
            response_msg = GetSuperPeerListResponse()
            response_msg.ParseFromString(base64.b64decode(d))
            for speer in response_msg.knownSuperPeers:
                theApp.peer_manager.add_super_peer(speer.agentID,
                                                   speer.agentIP,
                                                   speer.agentPort,
                                                   speer.token,
                                                   speer.publicKey)
                theApp.peer_manager.connect_to_peer(speer.agentID)

    def get_peer_list(self, count):
        g_logger.info("Sending GetPeerList message to aggregator")
        url = self.base_url + "/getpeerlist/"
        request_msg = GetPeerList()
        self._make_request_header(request_msg.header)
        data = base64.b64encode(request_msg.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_get_peer_list)

    def _handle_get_peer_list(self, result):
        if result is not None:
            response_msg = GetPeerListResponse()
            response_msg.ParseFromString(base64.b64decode(d))
            for peer in response_msg.knownPeers:
                theApp.peer_manager.add_normal_peer(peer.agentID,
                                                    peer.agentIP,
                                                    peer.agentPort,
                                                    peer.token,
                                                    peer.publicKey)
                theApp.peer_manager.connect_to_peer(peer.agentID)

    """ Event """
    #----------------------------------------------------------------------
    def get_events(self):
        g_logger.info("Sending GetEvents message to aggregator")
        url = self.base_url + "/getevents/"
        d = self._send_request('POST', url, data)

    def _handle_get_events(self, d):
        print(d)

    """ Report """
    #----------------------------------------------------------------------
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.send_service_report(report)
        else:
            g_logger.debug("Log has been dropped.")

    def send_website_report(self, report):
        g_logger.debug("Sending WebsiteReport to aggregator")
        url = self.base_url + "/sendwebsitereport/"
        data = base64.b64encode(report.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_send_website_report)

    def _handle_send_website_report(self, d):
        if
        print(type(d))

    def send_service_report(self, report):
        g_logger.debug("Sending ServiceReport to aggregator")
        url = self.base_url + "/sendservicereport/"
        data = base64.b64encode(report.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_send_service_report)

    def _handle_send_service_report(self, d):
        print(type(d))

    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        g_logger.info("Sending WebsiteSuggestion message to aggregator")
        url = self.base_url + "/websitesuggestion/"
        request_msg = WebsiteSuggestion()
        self._make_request_header(request_msg.header)
        request_msg.websiteURL = website_url
        request_msg.emailAddress = 'mrbean@yahoo.com' #theApp.peer_info.Email
        data = base64.b64encode(request_msg.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_send_website_suggestion)
        #d.addErrback(g_logger.error)

    def _handle_send_website_suggestion(self, d):
        response_msg = TestSuggestionResponse()
        response_msg.ParseFromString(base64.b64decode(d))
        g_logger.info("Got a reply from aggregator for WebsiteSuggestion")
        g_logger.debug(response_msg)

    def send_service_suggestion(self, service_name, host_name, ip):
        g_logger.info("Sending ServiceSuggestion message to aggregator")
        url = self.base_url + "/servicesuggestion/"
        request_msg = ServiceSuggestion()
        self._make_request_header(request_msg.header)
        request_msg.serviceName = service_name
        request_msg.emailAddress = theApp.peer_info.Email
        request_msg.hostName = host_name
        request_msg.ip = ip
        data = base64.b64encode(request_msg.SerializeToString())
        d = self._send_request('POST', url, data)
        d.addCallback(self._handle_send_service_suggestion)

    def _handle_send_service_suggestion(self, d):
        response_msg = TestSuggestionResponse()
        response_msg.ParseFromString(base64.b64decode(d))
        g_logger.info("Got a reply from aggregator for ServiceSuggestion")
        g_logger.debug(response_msg)

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        #g_logger.info("Sending CheckVersion message to aggregator")
        url = self.base_url + "/checkversion/"

    def _handle_check_version(self, d):
        print(d)

    def check_tests(self):
        #g_logger.info("Sending CheckTests message to aggregator")
        url = self.base_url + "/checktests/"

    def _handle_check_tests(self, d):
        print(d)

    #----------------------------------------------------------------------
    def _send_request(self, method, uri, data="", mimeType=None):
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data != "":
            data = 'msg=' + data
        if data:
            headers['Content-Length'] = str(len(data))
        d = client.getPage(uri, method=method, postdata=data,
                           headers=headers)
        d.addErrback(self._handle_error)
        return d

    def _handle_error(self, failure):
        from twisted.internet import error
        if isinstance(failure.value, error.ConnectError):
            g_logger.error("Connecting to the aggregator failed.")
            self.available = False
        else:
            g_logger.error(failure)


if __name__ == "__main__":
    api = AggregatorAPI('http://icm-dev.appspot.com/api')
    #api = AggregatorAPI('http://www.baidu.com')
    #d = api.send_website_suggestion('http://www.baidu.com')
    report = WebsiteReport()
    report.header.token = theApp.peer_info.AuthToken
    report.header.agentID = theApp.peer_info.ID
    report.report.reportID = 'xw384kkre'
    report.report.agentID = 10000
    report.report.testID = 1
    report.report.timeZone = 8
    report.report.timeUTC = int(time.time())
    report.report.passedNode = theApp.peer_info.getLocalIP()

    api.send_report(report)

    from twisted.internet import reactor
    reactor.callLater(10, reactor.stop)
    reactor.run()
