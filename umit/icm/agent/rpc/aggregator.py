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

import base64
import os
import sys
import urllib

from twisted.web import client
from twisted.web.error import Error
from twisted.internet import error

from google.protobuf.text_format import MessageToString

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.core.ReportManager import ReportStatus
from umit.icm.agent.Errors import AggergatorError
from umit.icm.agent.secure.Key import AESKey

aggregator_api_url = {
    'CheckAggregator': '/checkaggregator/',
    'RegisterAgent': '/registeragent/',
    'Login': '/loginagent/',
    'LoginStep2': '/loginagent2/',
    'Logout': '/logoutagent/',
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
    def __init__(self, aggregator=None):
        """Constructor"""
        self.base_url = g_db_helper.get_value('aggregator_url') if aggregator is None else aggregator
        self.available = True
        self.pending_report_ids = []

    def check_aggregator(self):
        g_logger.info("Sending CheckAggregator message to aggregator")
        request_msg = CheckAggregator()
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, CheckAggregatorResponse)
        defer_.addCallback(self._handle_check_aggregator_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_check_aggregator_response(self, message):
        if message is None:
            return
        
        if message.status == "ON":
            self.available = True
        else:
            self.available = False
        g_logger.info("Aggregator status: %s" % message.status)
        g_logger.debug("Aggregator version: %s" % message.header.currentVersionNo)
        g_logger.debug("Aggregator test version: %s" % message.header.currentTestVersionNo)
        
        return message

    """ Peer """
    #----------------------------------------------------------------------

    def register(self, username, password):
        g_logger.info("Sending RegisterAgent message to aggregator")
        request_msg = RegisterAgent()
        from umit.icm.agent.Version import VERSION_NUM
        request_msg.versionNo = VERSION_NUM
        request_msg.agentType = 'DESKTOP'
        request_msg.credentials.username = username
        request_msg.credentials.password = password
        request_msg.agentPublicKey.mod = str(theApp.key_manager.public_key.mod)
        request_msg.agentPublicKey.exp = str(theApp.key_manager.public_key.exp)
        if theApp.peer_info.internet_ip:
            request_msg.ip = theApp.peer_info.internet_ip

        # send message
        defer_ = self._send_message(request_msg, RegisterAgentResponse)
        defer_.addCallback(self._handle_register_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_register_response(self, message):
        if message is None:
            return
        
        g_logger.info("RegisterAgent response: (%d, %s)" %
                      (message.agentID, message.publicKeyHash))
        
        return {'id': message.agentID, 'hash': message.publicKeyHash}

    def login(self, username, password):
        g_logger.info("Sending Login message to aggregator")
        request_msg = Login()
        request_msg.agentID = theApp.peer_info.ID
        import random
        self.challenge = str(random.random())
        request_msg.challenge = self.challenge
        request_msg.port = theApp.listen_port
        if theApp.peer_info.internet_ip:
            request_msg.ip = theApp.peer_info.internet_ip

        defer_ = self._send_message(request_msg, LoginStep1)
        defer_.addCallback(self._handle_login_step1)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_login_step1(self, message):
        if message is None:
            return
        g_logger.info("Received LoginStep1 from aggregator.")
        if not theApp.key_manager.aggregator_public_key.verify(
            self.challenge, message.cipheredChallenge):
            g_logger.warning("Challenge doesn't match. Maybe something wrong "
                             "with aggregator public key or the current "
                             "aggregator is fake.")
            return
        g_logger.info("Sending LoginStep2 message to aggregator")
        request_msg = LoginStep2()
        request_msg.processID = message.processID
        request_msg.cipheredChallenge = theApp.key_manager.private_key.sign(message.challenge)

        defer_ = self._send_message(request_msg, LoginResponse)
        defer_.addCallback(self._handle_login_response)
        defer_.addErrback(self._handle_errback)
        
        return defer_

    def _handle_login_response(self, message):
        if message is None:
            return
        g_logger.info("Received LoginResponse from aggregator.")
        g_logger.info("Login successfully.")
        
        return True

    def logout(self):
        g_logger.info("Sending Logout message to aggregator")
        request_msg = Logout()
        request_msg.agentID = theApp.peer_info.ID
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_logout)
        
        return defer_

    def _handle_logout(self, message):
        g_logger.info("Received LogoutResponse from aggregator.")
        g_logger.debug("Logout message: %s" % message)
        
        theApp.peer_info.login = False
        
        return message

    #def report_peer_info(self):
        #g_logger.info("Sending ReportPeerInfo message to aggregator")
        #url = self.base_url + "/reportpeerinfo/"
        #result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        g_logger.info("Sending GetSuperPeerList message to aggregator")
        request_msg = GetSuperPeerList()
        request_msg.count = count

        defer_ = self._send_message(request_msg, GetSuperPeerListResponse)
        defer_.addCallback(self._handle_get_super_peer_list_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_super_peer_list_response(self, message):
        if message is None:
            return
        for speer in message.knownSuperPeers:
            theApp.peer_manager.add_super_peer(speer.agentID,
                                               speer.agentIP,
                                               speer.agentPort,
                                               speer.token,
                                               speer.publicKey)
            theApp.peer_manager.connect_to_peer(speer.agentID)
        
        return message

    def get_peer_list(self, count):
        g_logger.info("Sending GetPeerList message to aggregator")
        url = self.base_url + "/getpeerlist/"
        request_msg = GetPeerList()
        request_msg.count = count

        defer_ = self._send_message(request_msg, GetPeerListResponse)
        defer_.addCallback(self._handle_get_peer_list_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_peer_list_response(self, message):
        if message is None:
            return
        for peer in message.knownPeers:
            theApp.peer_manager.add_normal_peer(peer.agentID,
                                                peer.agentIP,
                                                peer.agentPort,
                                                peer.token,
                                                peer.publicKey)
            theApp.peer_manager.connect_to_peer(peer.agentID)
        
        return message

    """ Event """
    #----------------------------------------------------------------------
    def get_events(self):
        g_logger.info("Sending GetEvents message to aggregator")
        url = self.base_url + "/getevents/"
        request_msg = GetEvents()
        #self._make_request_header(request_msg.header)

        defer_ = self._send_message(request_msg, GetEventsResponse)
        defer_.addCallback(self._handle_get_events_response)
        defer_.addErrback(self._handle_errback)
        
        return defer_

    def _handle_get_events_response(self, message):
        if message is None:
            return
        for event in message.events:
            theApp.event_manager.add_event(event)
        
        return message

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
        #self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_website_report_response)
        defer_.addErrback(self._handle_errback)
        
        return defer_

    def _handle_send_website_report_response(self, message):
        if message is None:
            return
        
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        
        if len(self.pending_report_ids):
            report_id = self.pending_report_ids.pop(0) # assume FIFO
            g_logger.info("WebsiteReport '%s' has been sent to aggregator" % \
                          report_id)
            theApp.report_manager.remove_report(report_id,
                                                ReportStatus.SENT_TO_AGGREGATOR)
        else:
            g_logger.info("WebsiteReport has been sent to aggregator")
        
        return message

    def send_service_report(self, report):
        g_logger.debug("Sending ServiceReport to aggregator")
        url = self.base_url + "/sendservicereport/"
        request_msg = SendServiceReport()
        #self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_service_report_response)
        defer_.addErrback(self._handle_errback)
        
        return defer_

    def _handle_send_service_report_response(self, message):
        g_logger.debug("Handle Send Service Report: %s" % message)
        if message is None:
            return
        
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        
        if len(self.pending_report_ids):
            report_id = self.pending_report_ids.pop(0) # assume FIFO
            g_logger.info("ServiceReport '%s' has been sent to aggregator" % \
                          report_id)
            theApp.report_manager.remove_report(report_id,
                                                ReportStatus.SENT_TO_AGGREGATOR)
        else:
            g_logger.info("ServiceReport has been sent to aggregator")
        
        return message

    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        g_logger.info("Sending WebsiteSuggestion message to aggregator")
        url = self.base_url + "/websitesuggestion/"
        request_msg = WebsiteSuggestion()
        #self._make_request_header(request_msg.header)
        request_msg.websiteURL = website_url
        request_msg.emailAddress = theApp.peer_info.Email

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_website_suggestion_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_website_suggestion_response(self, message):
        if message is None:
            return
        g_logger.info("WebsiteSuggestion has been sent to aggregator")
        return True

    def send_service_suggestion(self, service_name, host_name, ip):
        g_logger.info("Sending ServiceSuggestion message to aggregator")
        url = self.base_url + "/servicesuggestion/"
        request_msg = ServiceSuggestion()
        #self._make_request_header(request_msg.header)
        request_msg.serviceName = service_name
        request_msg.emailAddress = theApp.peer_info.Email
        request_msg.hostName = host_name
        request_msg.ip = ip

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_service_suggestion_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_service_suggestion_response(self, message):
        if message is None:
            return
        g_logger.info("ServiceSuggestion has been sent to aggregator")
        return True

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        g_logger.info("Sending NewVersion message to aggregator")
        request_msg = NewVersion()
        #self._make_request_header(request_msg.header)
        from umit.icm.agent.Version import VERSION_NUM
        request_msg.agentVersionNo = VERSION_NUM
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, NewVersionResponse)
        defer_.addCallback(self._handle_check_version_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_check_version_response(self, message):
        if message is None:
            return
        
        return message

    def check_tests(self):
        g_logger.info("Sending NewTests message to aggregator")
        request_msg = NewTests()
        #self._make_request_header(request_msg.header)
        from umit.icm.agent.test import TEST_PACKAGE_VERSION_NUM
        request_msg.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM

        defer_ = self._send_message(request_msg, NewTestsResponse)
        defer_.addCallback(self._handle_check_tests_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_check_tests_response(self, message):
        if message is None:
            return
        
        return message

    """ Private """
    #----------------------------------------------------------------------
    def _rsa_encrypt(self, message):
        return base64.b64encode(
            theApp.key_manager.aggregator_public_key.encrypt(
                message.SerializeToString()))

    def _rsa_decrypt(self, text, msg_type):
        if text is None:
            return
        message = msg_type()
        message.ParseFromString(
            theApp.key_manager.private_key.decrypt(
                base64.b64decode(text)))
        return message

    def _aes_encrypt(self, message):
        assert theApp.key_manager.aggregator_aes_key
        return base64.b64encode(
            theApp.key_manager.aggregator_aes_key.encrypt(
                message.SerializeToString()))

    def _aes_decrypt(self, text, msg_type):
        if text is None:
            return
        
        assert theApp.key_manager.aggregator_aes_key
        
        message = msg_type()
        message.ParseFromString(
            theApp.key_manager.aggregator_aes_key.decrypt(
                base64.b64decode(text)))
        
        return message

    def _encode(self, message):
        return base64.b64encode(message.SerializeToString())

    def _decode(self, text, msg_type):
        if text is None:
            return
        
        message = msg_type()
        message.ParseFromString(base64.b64decode(text))
        
        return message

    def _send_message(self, message, response_msg_type=None):
        postdata = {}

        # encode message
        if isinstance(message, CheckAggregator):
            postdata['msg'] = self._encode(message)
        elif isinstance(message, Login) or isinstance(message, LoginStep2):
            postdata['msg'] = self._encode(message)
        elif isinstance(message, RegisterAgent):
            # generate AES key
            theApp.key_manager.aggregator_aes_key = AESKey()
            theApp.key_manager.aggregator_aes_key.generate()
            g_db_helper.set_value('aggregator_aes_key',
                                  theApp.key_manager.aggregator_aes_key.get_key())

            postdata['key'] = base64.b64encode(
                theApp.key_manager.aggregator_public_key.encrypt(
                    base64.b64encode(
                        theApp.key_manager.aggregator_aes_key.get_key())))
            postdata['msg'] = self._aes_encrypt(message)
        else:
            postdata['agentID'] = theApp.peer_info.ID
            postdata['msg'] = self._aes_encrypt(message)
        
        # send message
        url = self.base_url + aggregator_api_url[message.DESCRIPTOR.name]
        data = urllib.urlencode(postdata)
        defer_ = self._send_request('POST', url, data)

        # decode message
        if response_msg_type is not None:
            if isinstance(message, CheckAggregator):
                defer_.addCallback(self._decode, response_msg_type)
            elif isinstance(message, Login) or isinstance(message, LoginStep2):
                defer_.addCallback(self._decode, response_msg_type)
            else:
                defer_.addCallback(self._aes_decrypt, response_msg_type)
        
        defer_.addErrback(self._decode_errback)
        
        return defer_

    def _send_request(self, method, uri, data="", mimeType=None):
        g_logger.info("Sending message to aggregator at %s" % uri)
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data:
            headers['Content-Length'] = str(len(data))
        d = client.getPage(uri, method=method, postdata=data,
                           headers=headers)
        d.addErrback(self._connection_errback)
        return d

    def _connection_errback(self, failure):
        g_logger.error("[AggregatorAPI] - %s" % failure)
        
        if isinstance(failure, error.ConnectError) or \
           isinstance(failure, error.DNSLookupError):
            g_logger.error("Connecting to the aggregator failed.")
            self.available = False
            theApp.statistics.aggregator_fail_num = \
                  theApp.statistics.aggregator_fail_num + 1

        try:
            failure.raiseException()
        except Exception, err:
            if isinstance(err, Error):
                g_logger.error(">>> The Aggregator had an Internal Error:")
                g_logger.error(err.response)


    def _decode_errback(self, failure):
        g_logger.error("[AggregatorAPI] - Failed to decode. %s" % failure)

    def _handle_errback(self, failure):
        g_logger.error("Aggregator failure: %s" % str(failure))


if __name__ == "__main__":
    import time
    api = AggregatorAPI()
    #api = AggregatorAPI('http://www.baidu.com')
    d = api.check_version()

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
