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
import random
import time

from twisted.internet import defer

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.Version import *
from umit.icm.agent.test import TEST_PACKAGE_VERSION
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.utils.FileDownloader import FileDownloader
from umit.icm.agent.Upgrade import *
from umit.icm.agent.core.ReportManager import ReportStatus


class DesktopAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)
        self.pending_report_ids = []  # must be a FIFO queue

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        self._send_message(request_msg)

    def _handle_get_super_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_super_peers(message.count)
        response_msg = P2PGetSuperPeerListResponse()
        for speer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.agentID = speer.ID
            agent_data.agentIP = speer.IP
            agent_data.agentPort = speer.Port
            agent_data.token = speer.Token
            agent_data.publicKey = speer.PublicKey
            agent_data.peerStatus = speer.Status
        self._send_message(response_msg)

    def _handle_get_super_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_super_peer(agent_data.agentID,
                                                   agent_data.agentIP,
                                                   agent_data.agentPort,
                                                   agent_data.token,
                                                   agent_data.publicKey)

    def get_peer_list(self, count):
        g_logger.info("Send P2PGetPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetPeerList()
        request_msg.count = count
        self._send_message(request_msg)

    def _handle_get_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_normal_peers(message.count)
        response_msg = P2PGetPeerListResponse()
        for peer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.agentID = peer.ID
            agent_data.agentIP = peer.IP
            agent_data.agentPort = peer.Port
            agent_data.token = peer.Token
            agent_data.publicKey = peer.PublicKey
            agent_data.peerStatus = peer.Status
        self._send_message(response_msg)

    def _handle_get_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_normal_peer(agent_data.agentID,
                                                    agent_data.agentIP,
                                                    agent_data.agentPort,
                                                    agent_data.token,
                                                    agent_data.publicKey)
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        request_msg = SendWebsiteReport()
        request_msg.header.token = theApp.peer_info.AuthToken
        request_msg.header.agentID = theApp.peer_info.ID
        request_msg.report.CopyFrom(report)
        self._send_message(request_msg)
        self.pending_report_ids.append(report.header.reportID)

    def _handle_send_website_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(str(message.header.agentID))
        theApp.report_manager.add_report(message.report)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.currentVersionNo = VERSION_NUM
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM
        self._send_message(response_msg)

    def send_service_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        request_msg = SendServiceReport()
        request_msg.header.token = theApp.peer_info.AuthToken
        request_msg.header.agentID = theApp.peer_info.ID
        request_msg.report.CopyFrom(report)
        self._send_message(request_msg)
        self.pending_report_ids.append(report.header.reportID)

    def _handle_send_service_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(str(message.header.agentID))
        theApp.report_manager.add_report(message.report)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.currentVersionNo = VERSION_NUM
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM
        self._send_message(response_msg)

    def _handle_send_report_response(self, data):
        report_id = self.pending_report_ids.pop(0)
        theApp.statistics.reports_sent_to_normal_agent = \
              theApp.statistics.reports_sent_to_normal_agent + 1
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_AGENT)

    def require_agent_update(self, version, download_url, check_code=0):
        g_logger.info("Send AgentUpdate message to %s" % self.remote_ip)
        request_msg = AgentUpdate()
        request_msg.version = version
        request_msg.downloadURL = download_url
        if check_code != 0:
            request_msg.checkCode = check_code
        self._send_message(request_msg)

    def require_test_mod_update(self, version, download_url, check_code=0):
        g_logger.info("Send TestModuleUpdate message to %s" % self.remote_ip)
        request_msg = TestModuleUpdate()
        request_msg.version = version
        request_msg.downloadURL = download_url
        if check_code != 0:
            request_msg.checkCode = check_code
        self._send_message(request_msg)

    def _send_message(self, message):
        data = MessageFactory.encode(message)
        length = struct.pack('!I', len(data))
        self._transport.write(length)
        self._transport.write(data)

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
            self._handle_get_super_peer_list(message)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            self._handle_get_super_peer_list_response(message)
        elif isinstance(message, P2PGetPeerList):
            self._handle_get_peer_list(message)
        elif isinstance(message, P2PGetPeerListResponse):
            self._handle_get_peer_list_response(message)
        elif isinstance(message, SendWebsiteReport):
            self._handle_send_website_report(message)
        elif isinstance(message, SendServiceReport):
            self._handle_send_service_report(message)
        elif isinstance(message, SendReportResponse):
            self._handle_send_report_response(message)
        elif isinstance(message, AgentUpdateResponse):
            g_logger.info("Peer %s update agent to version %s: %S" %
                          (self.remote_id, message.version, message.result))
        elif isinstance(message, TestModuleUpdateResponse):
            g_logger.info("Peer %s update test mod to version %s: %S" %
                          (self.remote_id, message.version, message.result))

    def close(self):
        if self.remote_id in theApp.peer_manager.normal_peers:
            theApp.peer_manager.normal_peers[self.remote_id].Status = \
                  'Disconnected'

#---------------------------------------------------------------------
class DesktopSuperAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)
        self.pending_report_ids = []  # must be a FIFO queue
        self.forwarding_defers = {}

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        self._send_message(request_msg)

    def _handle_get_super_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_super_peers(message.count)
        response_msg = P2PGetSuperPeerListResponse()
        for speer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.agentID = speer.ID
            agent_data.agentIP = speer.IP
            agent_data.agentPort = speer.Port
            agent_data.token = speer.Token
            agent_data.publicKey = speer.PublicKey
            agent_data.peerStatus = speer.Status
        self._send_message(response_msg)

    def _handle_get_super_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_super_peer(agent_data.agentID,
                                                   agent_data.agentIP,
                                                   agent_data.agentPort,
                                                   agent_data.token,
                                                   agent_data.publicKey)

    def get_peer_list(self, count):
        g_logger.info("Send P2PGetPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetPeerList()
        request_msg.count = count
        self._send_message(request_msg)

    def _handle_get_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_normal_peers(message.count)
        response_msg = P2PGetPeerListResponse()
        for peer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.agentID = peer.ID
            agent_data.agentIP = peer.IP
            agent_data.agentPort = peer.Port
            agent_data.token = peer.Token
            agent_data.publicKey = peer.PublicKey
            agent_data.peerStatus = peer.Status
        self._send_message(response_msg)

    def _handle_get_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_normal_peer(agent_data.agentID,
                                                    agent_data.agentIP,
                                                    agent_data.agentPort,
                                                    agent_data.token,
                                                    agent_data.publicKey)

    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        request_msg = SendWebsiteReport()
        request_msg.header.token = theApp.peer_info.AuthToken
        request_msg.header.agentID = theApp.peer_info.ID
        request_msg.report.CopyFrom(report)
        self._send_message(request_msg)
        self.pending_report_ids.append(report.header.reportID)

    def _handle_send_website_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(str(message.header.agentID))
        theApp.report_manager.add_report(message.report)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.currentVersionNo = VERSION_NUM
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM
        self._send_message(response_msg)

    def send_service_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        request_msg = SendServiceReport()
        request_msg.header.token = theApp.peer_info.AuthToken
        request_msg.header.agentID = theApp.peer_info.ID
        request_msg.report.CopyFrom(report)
        self._send_message(request_msg)
        self.pending_report_ids.append(report.header.reportID)

    def _handle_send_service_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(str(message.header.agentID))
        theApp.report_manager.add_report(message.report)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.currentVersionNo = VERSION_NUM
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM
        self._send_message(response_msg)

    def _handle_send_report_response(self, data):
        report_id = self.pending_report_ids.pop(0)
        theApp.statistics.reports_sent_to_super_agent = \
              theApp.statistics.reports_sent_to_super_agent + 1
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_SUPER_AGENT)

    def _handle_agent_update(self, message):
        if compare_version(message.version, VERSION) > 0:
            if not os.path.exists(TMP_DIR):
                os.mkdir(TMP_DIR)
            downloader = FileDownloader(
                message.downloadURL,
                os.path.join(TMP_DIR,
                             'icm-agent_' + message.version + '.tar.gz')
                )
            if message.HasField('checkCode'):
                check_code = message.checkCode
            else:
                check_code = 0
            downloader.addCallback(update_agent, message.version,
                                   message.checkCode)
            downloader.start()

    def _handle_test_mod_update(self, message):
        if compare_version(message.version, TEST_PACKAGE_VERSION) > 0:
            if not os.path.exists(TMP_DIR):
                os.mkdir(TMP_DIR)
            downloader = FileDownloader(
                message.downloadURL,
                os.path.join(TMP_DIR, 'test_' + message.version + '.py')
                )
            if message.HasField('checkCode'):
                downloader.addCallback(update_test_mod, message.version,
                                       message.checkCode)
            else:
                downloader.addCallback(update_test_mod, message.version)
            downloader.start()

    def forward_message(self, target, message):
        request_msg = ForwardingMessage()
        request_msg.destination = target
        request_msg.identifier = "%s_%d" % \
                   (theApp.peer_info.ID, int(time.time() * 1000))
        request_msg.encodedMessage = \
                   base64.b64encode(MessageFactory.encode(message))
        defer_ = defer.Deferred()
        self.forwarding_defers[request_msg.identifier] = defer_
        self._send_message(request_msg)
        return defer_

    def _handle_forward_message_response(self, message):
        if message.identifier not in self.forwarding_defers:
            g_logger.error("message id '%s' not in the forwarding list" % \
                           message.identifier)
        defer_ = self.forwarding_defers[message.identifier]
        response_msg = MessageFactory.decode(\
            base64.b64decode(message.encodedMessage))
        defer_.callback(response_msg)

    def _send_message(self, message):
        data = MessageFactory.encode(message)
        length = struct.pack('!I', len(data))
        self._transport.write(length)
        self._transport.write(data)

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
            self._handle_get_super_peer_list(message)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            self._handle_get_super_peer_list_response(message)
        elif isinstance(message, P2PGetPeerList):
            self._handle_get_peer_list(message)
        elif isinstance(message, P2PGetPeerListResponse):
            self._handle_get_peer_list_response(message)
        elif isinstance(message, SendWebsiteReport):
            self._handle_send_website_report(message)
        elif isinstance(message, SendServiceReport):
            self._handle_send_service_report(message)
        elif isinstance(message, SendReportResponse):
            self._handle_send_report_response(message)
        elif isinstance(message, AgentUpdate):
            self._handle_agent_update(message)
        elif isinstance(message, TestModuleUpdate):
            self._handle_test_mod_update(message)
        elif isinstance(message, ForwardingMessageResponse):
            self._handle_forward_message_response(message)

    def close(self):
        if self.remote_id in theApp.peer_manager.super_peers:
            theApp.peer_manager.super_peers[self.remote_id].Status = \
                  'Disconnected'