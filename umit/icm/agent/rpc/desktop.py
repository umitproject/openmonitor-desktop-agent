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

import random

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.Version import *
from umit.icm.agent.test import TEST_PACKAGE_VERSION
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.utils.FileDownloader import FileDownloader
from umit.icm.agent.Update import *

########################################################################
class DesktopAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(response_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(request_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(response_msg)
        self._transport.write(data)

    def _handle_get_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_normal_peer(agent_data.agentID,
                                                    agent_data.agentIP,
                                                    agent_data.agentPort,
                                                    agent_data.token,
                                                    agent_data.publicKey)

    def send_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        data = MessageFactory.encode(report)
        self._transport.write(data)

    def _handle_send_report_response(self, data):
        theApp.statistics.reports_sent_to_normal_agent = \
              theApp.statistics.reports_sent_to_normal_agent + 1

    def require_agent_update(self, version, download_url, check_code=0):
        g_logger.info("Send AgentUpdate message to %s" % self.remote_ip)
        request_msg = AgentUpdate()
        request_msg.version = version
        request_msg.downloadURL = download_url
        if check_code != 0:
            request_msg.checkCode = check_code
        data = MessageFactory.encode(request_msg)
        self._transport.write(data)

    def require_test_mod_update(self, version, download_url, check_code=0):
        g_logger.info("Send TestModuleUpdate message to %s" % self.remote_ip)
        request_msg = TestModuleUpdate()
        request_msg.version = version
        request_msg.downloadURL = download_url
        if check_code != 0:
            request_msg.checkCode = check_code
        data = MessageFactory.encode(request_msg)
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
        elif isinstance(message, WebsiteReport):
            theApp.statistics.reports_received = \
                  theApp.statistics.reports_received + 1
            theApp.report_manager.add_report(message)
        elif isinstance(message, ServiceReport):
            theApp.statistics.reports_received = \
                  theApp.statistics.reports_received + 1
            theApp.report_manager.add_report(message)
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

########################################################################
class DesktopSuperAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s" % self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(response_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(request_msg)
        self._transport.write(data)

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
        data = MessageFactory.encode(response_msg)
        self._transport.write(data)

    def _handle_get_peer_list_response(self, message):
        for agent_data in message.peers:
            if self.remote_id != agent_data.agentID:
                theApp.peer_manager.add_normal_peer(agent_data.agentID,
                                                    agent_data.agentIP,
                                                    agent_data.agentPort,
                                                    agent_data.token,
                                                    agent_data.publicKey)

    def send_report(self, report):
        g_logger.info("Send %s message to %s" % (report.DESCRIPTOR.name,
                                                 self.remote_ip))
        data = MessageFactory.encode(report)
        self._transport.write(data)

    def _handle_send_report_response(self, data):
        theApp.statistics.reports_sent_to_super_agent = \
              theApp.statistics.reports_sent_to_super_agent + 1

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

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
            self._handle_get_super_peer_list(message)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            self._handle_get_super_peer_list_response(message)
        elif isinstance(message, P2PGetPeerList):
            self._handle_get_peer_list(message)
        elif isinstance(message, P2PGetPeerListResponse):
            self._handle_get_peer_list_response(message)
        elif isinstance(message, WebsiteReport):
            theApp.statistics.reports_received = \
                  theApp.statistics.reports_received + 1
            theApp.report_manager.add_report(message)
        elif isinstance(message, ServiceReport):
            theApp.statistics.reports_received = \
                  theApp.statistics.reports_received + 1
            theApp.report_manager.add_report(message)
        elif isinstance(message, SendReportResponse):
            self._handle_send_report_response(message)
        elif isinstance(message, AgentUpdate):
            self._handle_agent_update(message)
        elif isinstance(message, TestModuleUpdate):
            self._handle_test_mod_update(message)

    def close(self):
        if self.remote_id in theApp.peer_manager.super_peers:
            theApp.peer_manager.super_peers[self.remote_id].Status = \
                  'Disconnected'