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

########################################################################
class AggregatorProxy(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, url):
        """Constructor"""
        self.base_url = url
        self.available = False
        self.report_id_list = []

    def _make_request_header(self, header):
        header.token = theApp.peer_info.AuthToken
        header.agentID = theApp.peer_info.ID

    def check_availability(self):
        g_logger.info("Sending CheckAggregator message to aggregator")
        url = self.base_url + '/checkaggregator/' # temporarily hardcoded
        request_msg = CheckAggregator()
        self._make_request_header(request_msg.header)
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_check_availability)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_availability(self, data):
        response_msg = CheckAggregatorResponse()
        response_msg.ParseFromString(base64.b64decode(data))
        if response_msg.status == "ON":
            self.available = True
        else:
            self.available = False
        g_logger.info("Aggregator status: %s" % response_msg.status)

    """ Peer """
    #----------------------------------------------------------------------
    def register(self, ip=None):
        g_logger.info("Sending RegisterAgent message to aggregator")
        url = self.base_url + "/registeragent/"
        request_msg = RegisterAgent()
        from umit.icm.agent.Version import VERSION_INT
        request_msg.versionNo = VERSION_INT
        request_msg.agentType = 'DESKTOP'
        if ip:
            request_msg.ip = ip
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_register)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_register(self, data):
        response_msg = RegisterAgentResponse()
        response_msg.ParseFromString(base64.b64decode(data))
        reg_data = [response_msg.agentID, response_msg.token,
                    response_msg.publicKey, response_msg.privateKey,
                    response_msg.cipheredPublicKey,
                    response_msg.aggregatorPublicKey]
        return reg_data

    #def report_peer_info(self):
        #g_logger.info("Sending ReportPeerInfo message to aggregator")
        #url = self.base_url + "/reportpeerinfo/"
        #result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        g_logger.info("Sending GetSuperPeerList message to aggregator")
        url = self.base_url + "/getsuperpeerlist/"
        request_msg = GetSuperPeerList()
        self._make_request_header(request_msg.header)
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_get_super_peer_list)
        return defer_

    def _handle_get_super_peer_list(self, data):
        response_msg = GetSuperPeerListResponse()
        response_msg.ParseFromString(base64.b64decode(data))
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
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_get_peer_list)
        return defer_

    def _handle_get_peer_list(self, data):
        response_msg = GetPeerListResponse()
        response_msg.ParseFromString(base64.b64decode(data))
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
        request_msg = GetEvents()
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_get_events)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_get_events(self, data):
        print(data)

    """ Report """
    #----------------------------------------------------------------------
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.report_id_list.append(report.header.reportID)
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.report_id_list.append(report.header.reportID)
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        g_logger.debug("Sending WebsiteReport to aggregator")
        url = self.base_url + "/sendwebsitereport/"
        request_msg = SendWebsiteReport()
        self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_send_website_report)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_website_report(self, data):
        response_msg = SendReportResponse()
        response_msg.ParseFromString(base64.b64decode(data))
        g_logger.info("WebsiteReport has been sent to aggregator")
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.report_id_list.pop(0) # assume FIFO
        return report_id, ReportStatus.SENT_TO_AGGREGATOR

    def send_service_report(self, report):
        g_logger.debug("Sending ServiceReport to aggregator")
        url = self.base_url + "/sendservicereport/"
        request_msg = SendServiceReport()
        self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_send_service_report)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_service_report(self, data):
        response_msg = SendReportResponse()
        response_msg.ParseFromString(base64.b64decode(data))
        g_logger.info("ServiceReport has been sent to aggregator")
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.report_id_list.pop(0) # assume FIFO
        return report_id, ReportStatus.SENT_TO_AGGREGATOR

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
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_send_website_suggestion)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_website_suggestion(self, data):
        response_msg = TestSuggestionResponse()
        response_msg.ParseFromString(base64.b64decode(data))
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
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_send_service_suggestion)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_send_service_suggestion(self, data):
        response_msg = TestSuggestionResponse()
        response_msg.ParseFromString(base64.b64decode(data))
        g_logger.info("ServiceSuggestion has been sent to aggregator")

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        g_logger.info("Sending NewVersion message to aggregator")
        url = self.base_url + "/checkversion/"
        request_msg = NewVersion()
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_check_version)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_version(self, data):
        print(data)

    def check_tests(self):
        g_logger.info("Sending NewTests message to aggregator")
        url = self.base_url + "/checktests/"
        request_msg = NewTests()
        data = base64.b64encode(request_msg.SerializeToString())
        defer_ = self._send_request('POST', url, data)
        defer_.addCallback(self._handle_check_tests)
        defer_.addErrback(self._handle_error)
        return defer_

    def _handle_check_tests(self, data):
        print(data)

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
        #d.addErrback(self._handle_error)
        return d

    def _handle_error(self, failure):
        from twisted.internet import error
        failure.trap(error.ConnectError)
        g_logger.error("Connecting to the aggregator failed.")
        self.available = False
        theApp.statistics.aggregator_fail_num = \
              theApp.statistics.aggregator_fail_num + 1



