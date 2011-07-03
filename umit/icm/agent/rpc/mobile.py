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

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
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
            data = MessageFactory.encode(response_msg)
            self._transport.write(data)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            for agent_data in message.peers:
                if self.remote_id != agent_data.id:
                    entry = { 'id': agent_data.id,
                              'ip': agent_data.agentIP,
                              'port': agent_data.agentPort,
                              'token': agent_data.token,
                              'public_key': agent_data.publicKey,
                              'status': 'Connected' }
                    theApp.peer_manager.add_super_peer(entry)
        elif isinstance(message, P2PGetPeerList):
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
            data = MessageFactory.encode(response_msg)
            self._transport.write(data)
        elif isinstance(message, P2PGetPeerListResponse):
            for agent_data in message.peers:
                if self.remote_id != agent_data.id:
                    entry = { 'id': agent_data.id,
                              'ip': agent_data.agentIP,
                              'port': agent_data.agentPort,
                              'token': agent_data.token,
                              'public_key': agent_data.publicKey,
                              'status': 'Connected' }
                    theApp.peer_manager.add_normal_peer(entry)
        elif isinstance(message, WebsiteReport):
            theApp.report_manager.add_report(message)
        elif isinstance(message, ServiceReport):
            theApp.report_manager.add_report(message)
        elif isinstance(message, AgentUpdateResponse):
            g_logger.info("Peer %s update agent to version %s: %S" %
                          (self.remote_id, message.version, message.result))
        elif isinstance(message, TestModuleUpdateResponse):
            g_logger.info("Peer %s update test mod to version %s: %S" %
                          (self.remote_id, message.version, message.result))


    def close(self):
        if self.ID in theApp.peer_manager.mobile_peers:
            theApp.peer_manager.mobile_peers[self.ID].Status = 'Disconnected'

