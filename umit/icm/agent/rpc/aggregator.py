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

import base64
import os
import sys

from twisted.web import client

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.core.ReportManager import ReportStatus

########################################################################
class AggregagorSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, transport):
        """Constructor"""
        Session.__init__(self, 0, transport)

    def _handle_assign_task(self, message):
        pass

    def _handle_agent_update(self, message):
        pass

    def _handle_test_mod_update(self, message):
        pass

    def _handle_notification(self, message):
        pass

    def handle_message(self, message):
        g_logger.debug("AggregatorSession - Handling %s message." %
                       message.DESCRIPTOR.name)
        if isinstance(message, AssignTask):
            self._handle_assign_task(message)
        elif isinstance(message, AgentUpdate):
            self._handle_assign_task(message)
        elif isinstance(message, TestModuleUpdate):
            self._handle_assign_task(message)
        elif isinstance(message, Notification):
            self._handle_notification(message)

    def close(self):
        pass


aggregator_api_url = {
    'CheckAggregator': '/checkaggregator/',
    'RegisterAgent': '/registeragent/',
    'Login': '/login/',
    'Logout': '/logout/',
    'GetSuperPeerList': '/getsuperpeerlist/',
    'GetPeerList': '/getpeerlist/',
    'GetEvents': '/getevents/',
    'SendWebsiteReport': '/sendwebsitereport/',
    'SendServiceReport': '/sendservicereport/',
    'WebsiteSuggestion': '/websitesuggestion/',
    'ServiceSuggestion': '/servicesuggestion/',
    'NewVersion': '/checkversion/',
    'NewTests': '/checktests/',
}

########################################################################
class AggregatorAPI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.base_url = g_db_helper.get_config('aggregator_url')
        self.available = False
        self.pending_report_ids = []

    def _make_request_header(self, header):
        header.token = theApp.peer_info.AuthToken
        header.agentID = theApp.peer_info.ID

    def check_availability(self):
        g_logger.info("Sending CheckAggregator message to aggregator")
        request_msg = CheckAggregator()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_check_availability)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_availability(self, message):
        if message.status == "ON":
            self.available = True
        else:
            self.available = False
        g_logger.info("Aggregator status: %s" % message.status)

    """ Peer """
    #----------------------------------------------------------------------
    def register(self):
        g_logger.info("Sending RegisterAgent message to aggregator")
        request_msg = RegisterAgent()
        from umit.icm.agent.Version import VERSION_INT
        request_msg.versionNo = VERSION_INT
        request_msg.agentType = 'DESKTOP'
        if theApp.peer_info.props['internet_ip']:
            request_msg.ip = theApp.peer_info.props['internet_ip']
        defer_ = self._send_message(request_msg, True)
        defer_.addCallback(self._handle_register)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_register(self, message):
        g_logger.info("RegisterAgent response: (%d, %s, %s, %s, %s, %s)" %
                      (message.agentID, message.token, message.publicKey,
                       message.privateKey, message.cipheredPublicKey,
                       message.aggregatorPublicKey))
        theApp.peer_info.ID = message.agentID
        theApp.peer_info.AuthToken = message.token
        theApp.peer_info.PublicKey = message.publicKey
        theApp.peer_info.PrivateKey = message.privateKey
        theApp.peer_info.CipheredPublicKey = message.cipheredPublicKey
        theApp.peer_info.AggregatorPublicKey = message.aggregatorPublicKey
        theApp.peer_info.registered = True

    def login(self):
        g_logger.info("Sending Login message to aggregator")
        request_msg = Login()
        self._make_request_header(request_msg.header)
        if theApp.peer_info.props['internet_ip']:
            request_msg.ip = theApp.peer_info.props['internet_ip']
        defer_ = self._send_message(request_msg, True)
        defer_.addCallback(self._handle_login)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_login(self, message):
        g_logger.info("Received LoginResponse from aggregator.")
        theApp.peer_info.login = True

    def logout(self):
        g_logger.info("Sending Logout message to aggregator")
        request_msg = Logout()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg, True)
        defer_.addCallback(self._handle_check_availability)
        defer_.addErrback(self._handle_error)
        return defer_

    #def report_peer_info(self):
        #g_logger.info("Sending ReportPeerInfo message to aggregator")
        #url = self.base_url + "/reportpeerinfo/"
        #result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        g_logger.info("Sending GetSuperPeerList message to aggregator")
        url = self.base_url + "/getsuperpeerlist/"
        request_msg = GetSuperPeerList()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_get_super_peer_list)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_get_super_peer_list(self, message):
        for speer in message.knownSuperPeers:
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
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_get_peer_list)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_get_peer_list(self, message):
        for peer in message.knownPeers:
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
        request_msg = GetEvents()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_get_events)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_get_events(self, message):
        print(message)
        for event in message.events:
            theApp.event_manager.add_event(event)

    """ Report """
    #----------------------------------------------------------------------
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.pending_report_ids.append(report.header.reportID)
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.pending_report_ids.append(report.header.reportID)
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        g_logger.debug("Sending WebsiteReport to aggregator")
        url = self.base_url + "/sendwebsitereport/"
        request_msg = SendWebsiteReport()
        self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_send_website_report)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_website_report(self, message):
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.pending_report_ids.pop(0) # assume FIFO
        g_logger.info("WebsiteReport '%s' has been sent to aggregator" % \
                      report_id)
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_AGGREGATOR)

    def send_service_report(self, report):
        g_logger.debug("Sending ServiceReport to aggregator")
        url = self.base_url + "/sendservicereport/"
        request_msg = SendServiceReport()
        self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_send_service_report)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_service_report(self, message):
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.pending_report_ids.pop(0) # assume FIFO
        g_logger.info("ServiceReport '%s' has been sent to aggregator" % \
                      report_id)
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_AGGREGATOR)

    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        g_logger.info("Sending WebsiteSuggestion message to aggregator")
        url = self.base_url + "/websitesuggestion/"
        request_msg = WebsiteSuggestion()
        self._make_request_header(request_msg.header)
        request_msg.websiteURL = website_url
        request_msg.emailAddress = theApp.peer_info.Email
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_send_website_suggestion)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_website_suggestion(self, message):
        g_logger.info("WebsiteSuggestion has been sent to aggregator")

    def send_service_suggestion(self, service_name, host_name, ip):
        g_logger.info("Sending ServiceSuggestion message to aggregator")
        url = self.base_url + "/servicesuggestion/"
        request_msg = ServiceSuggestion()
        self._make_request_header(request_msg.header)
        request_msg.serviceName = service_name
        request_msg.emailAddress = theApp.peer_info.Email
        request_msg.hostName = host_name
        request_msg.ip = ip
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_send_service_suggestion)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_service_suggestion(self, message):
        g_logger.info("ServiceSuggestion has been sent to aggregator")

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        g_logger.info("Sending NewVersion message to aggregator")
        request_msg = NewVersion()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_check_version)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_version(self, message):
        print(message)

    def check_tests(self):
        g_logger.info("Sending NewTests message to aggregator")
        request_msg = NewTests()
        self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_check_tests)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_tests(self, message):
        print(message)

    #----------------------------------------------------------------------
    def _decode_message(self, data, msg_type):
        message = message_creator[msg_type]()
        message.ParseFromString(base64.b64decode(data))
        return message

    def _send_message(self, message, safeSend=False):
        if safeSend and not self.available:
            speer_id = theApp.peer_manager.get_random_speer_connected()
            if speer_id is not None:
                return theApp.peer_manager.sessions[speer_id].\
                       forward_message(0, message)
        data = base64.b64encode(message.SerializeToString())
        url = self.base_url + aggregator_api_url[message.DESCRIPTOR.name]
        defer_ = self._send_request('POST', url, data)
        response_msg_type = message_id_to_type.get(\
            message_type_to_id[message.DESCRIPTOR.name] + 1)
        if response_msg_type:
            defer_.addCallback(self._decode_message, response_msg_type)
        return defer_

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
        #d.addErrback(self._handle_error)
        return d

    def _handle_error(self, failure):
        from twisted.internet import error
        failure.trap(error.ConnectError)
        g_logger.error("Connecting to the aggregator failed.")
        self.available = False
        theApp.statistics.aggregator_fail_num = \
              theApp.statistics.aggregator_fail_num + 1

def out(data):
    print(data)

if __name__ == "__main__":
    import time
    api = AggregatorAPI()
    #api = AggregatorAPI('http://www.baidu.com')
    d = api.get_events()
    d.addCallback(out)
    report = WebsiteReport()
    report.header.reportID = 'xw384kkre'
    report.header.agentID = 10000
    report.header.testID = 1
    report.header.timeZone = 8
    report.header.timeUTC = int(time.time())
    report.report.websiteURL = 'http://www.baidu.com'
    report.report.statusCode = 200

    #api.send_report(report)

    #api.register("test1", "test", "test@hotmail.com")

    from twisted.internet import reactor
    reactor.callLater(10, reactor.stop)
    reactor.run()
