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

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.Version import *
from umit.icm.agent.test import TEST_PACKAGE_VERSION
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.Session import Session

########################################################################
class MobileAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)

    def _handle_get_super_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_super_peers(message.count)
        response_msg = P2PGetSuperPeerListResponse()
        for speer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.id = speer.ID
            agent_data.token = speer.Token
            agent_data.publicKey = speer.PublicKey
            agent_data.peerStatus = speer.Status
            agent_data.agentIP = speer.IP
            agent_data.agentPort = speer.Port
        self._send_message(response_msg)

    def _handle_get_super_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.id:
                entry = { 'id': agent_data.id,
                          'ip': agent_data.agentIP,
                          'port': agent_data.agentPort,
                          'token': agent_data.token,
                          'public_key': agent_data.publicKey,
                          'status': 'Connected' }
                theApp.peer_manager.add_super_peer(entry)

    def _handle_get_peer_list(self, message):
        chosen_peers = theApp.peer_manager.select_normal_peers(message.count)
        response_msg = P2PGetPeerListResponse()
        for peer in chosen_peers:
            agent_data = response_msg.peers.add()
            agent_data.id = peer.ID
            agent_data.token = peer.Token
            agent_data.publicKey = peer.PublicKey
            agent_data.peerStatus = peer.Status
            agent_data.agentIP = peer.IP
            agent_data.agentPort = peer.Port
        self._send_message(response_msg)

    def _handle_get_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.id:
                entry = { 'id': agent_data.id,
                          'ip': agent_data.agentIP,
                          'port': agent_data.agentPort,
                          'token': agent_data.token,
                          'public_key': agent_data.publicKey,
                          'status': 'Connected' }
                theApp.peer_manager.add_normal_peer(entry)

    def _handle_send_website_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(message.header.agentID)
        theApp.report_manager.add_report(message)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.token = theApp.peer_info.AuthToken
        response_msg.header.agentID = theApp.peer_info.ID
        self._send_message(response_msg)

    def _handle_send_service_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(message.header.agentID)
        theApp.report_manager.add_report(message)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.token = theApp.peer_info.AuthToken
        response_msg.header.agentID = theApp.peer_info.ID
        self._send_message(response_msg)

    def _handle_send_report_response(self, message):
        theApp.statistics.reports_sent_to_mobile_agent = \
              theApp.statistics.reports_sent_to_mobile_agent + 1

    def _handle_forward_message(self, message):
        if theApp.peer_info.Type != 1:
            return
        forward_message = MessageFactory.decode(\
            base64.b64decode(message.encodedMessage))
        if message.destination == 0:
            defer_ = theApp.aggregator.safe_send(forward_message)
            defer_.addCallback(self.send_forward_message_response,
                               message.identifier)
        else:
            pass

    def send_forward_message_response(self, message, identifier):
        response_msg = ForwardingMessageResponse()
        response_msg.identifier = identifier
        response_msg.encodedMessage = \
                    base64.b64encode(MessageFactory.encode(message))
        self._send_message(response_msg)

    def _send_message(self, message):
        data = MessageFactory.encode(request_msg)
        length = struct.pack('!I', len(data))
        self.transport.write(length)
        self.transport.write(data)

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
        elif isinstance(message, ForwardingMessage):
            self._handle_forward_message(message)

    def close(self):
        if self.remote_id in theApp.peer_manager.mobile_peers:
            theApp.peer_manager.mobile_peers[self.remote_id].Status = \
                  'Disconnected'

########################################################################
class MobileAgentService(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    def _handle_get_super_peer_list(self, message):
        agentID = message.header.agentID
        secretKey = theApp.peer_manager
        if message.HasField('count'):
            chosen_peers = theApp.peer_manager.select_super_peers(message.count)
        else:
            chosen_peers = theApp.peer_manager.super_peers
        response_msg = GetSuperPeerListResponse()
        response_msg.header.currentVersionNo = VERSION_INT
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION
        for speer in chosen_peers:
            agent_data = response_msg.knownSuperPeers.add()
            agent_data.id = speer.ID
            agent_data.token = speer.Token
            agent_data.publicKey = speer.PublicKey
            agent_data.peerStatus = speer.Status
            agent_data.agentIP = speer.IP
            agent_data.agentPort = speer.Port
        self._send_message(response_msg)

    def _handle_get_peer_list(self, message):
        agentID = message.header.agentID
        secretKey = theApp.peer_manager
        if message.HasField('count'):
            chosen_peers = theApp.peer_manager.select_normal_peers(message.count)
        else:
            chosen_peers = theApp.peer_manager.normal_peers
        response_msg = GetPeerListResponse()
        response_msg.header.currentVersionNo = VERSION_INT
        response_msg.header.currentTestVersionNo = TEST_PACKAGE_VERSION
        for peer in chosen_peers:
            agent_data = response_msg.knownPeers.add()
            agent_data.id = peer.ID
            agent_data.token = peer.Token
            agent_data.publicKey = peer.PublicKey
            agent_data.peerStatus = peer.Status
            agent_data.agentIP = peer.IP
            agent_data.agentPort = peer.Port
        self._send_message(response_msg)

    def _handle_send_website_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(message.header.agentID)
        theApp.report_manager.add_report(message)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.token = theApp.peer_info.AuthToken
        response_msg.header.agentID = theApp.peer_info.ID
        self._send_message(response_msg)

    def _handle_send_service_report(self, message):
        theApp.statistics.reports_received = \
              theApp.statistics.reports_received + 1
        message.report.header.passedNode.append(message.header.agentID)
        theApp.report_manager.add_report(message)
        # send response
        response_msg = SendReportResponse()
        response_msg.header.token = theApp.peer_info.AuthToken
        response_msg.header.agentID = theApp.peer_info.ID
        self._send_message(response_msg)

    def _handle_forward_message(self, message):
        if theApp.peer_info.Type != 1:
            return
        forward_message = MessageFactory.decode(\
            base64.b64decode(message.encodedMessage))
        if message.destination == 0:
            defer_ = theApp.aggregator.safe_send(forward_message)
            defer_.addCallback(self.send_forward_message_response,
                               message.identifier)
        else:
            pass

    def send_forward_message_response(self, message, identifier):
        response_msg = ForwardingMessageResponse()
        response_msg.identifier = identifier
        response_msg.encodedMessage = \
                    base64.b64encode(MessageFactory.encode(message))
        self._send_message(response_msg)

    def _send_message(self, message):
        data = MessageFactory.encode(request_msg)
        length = struct.pack('!I', len(data))
        self.transport.write(length)
        self.transport.write(data)

    def handle_message(self, message):
        if isinstance(message, GetSuperPeerList):
            self._handle_get_super_peer_list(message)
        elif isinstance(message, GetPeerList):
            self._handle_get_peer_list(message)
        elif isinstance(message, SendWebsiteReport):
            self._handle_send_website_report(message)
        elif isinstance(message, SendServiceReport):
            self._handle_send_service_report(message)
        elif isinstance(message, ForwardingMessage):
            self._handle_forward_message(message)
