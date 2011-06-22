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
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.Session import Session

########################################################################
class DesktopAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s", self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._send_request(protocol.transport, data)

    def get_peer_list(self, count):
        g_logger.info("Send P2PGetPeerList message to %s", self.remote_ip)
        request_msg = P2PGetPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._send_request(protocol.transport, data)

    def _send_request(self, data=""):
        self.transport.write(data)

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
            count = message.getSuperPeerListRequest.count
            chosen_peers = theApp.peer_manager.super_peers[0:count]
            response_msg = P2PGetSuperPeerListResponse()
            for speer in chosen_peers:
                agent_data = AgentData()
                agent_data.id = speer.ID
                agent_data.token = speer.Token
                agent_data.publicKey = speer.PublicKey
                agent_data.peerStatus = speer.Status
                agent_data.agentIP = speer.IP
                agent_data.agentPort = speer.Port
                response_msg.peers.append(agent_data)
            data = MessageFactory.encode(response_msg)
            self.transport.write(data)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            for agent_data in message.peers:
                peer_entry = PeerEntry()
                peer_entry.Type = 0
                peer_entry.ID = agent_data.id
                peer_entry.IP = agent_data.agentIP
                peer_entry.Port = agent_data.agentPort
                peer_entry.Token = agent_data.token
                peer_entry.PublicKey = agent_data.publicKey
                peer_entry.Status = agent_data.peerStatus
                theApp.peer_manager.add_super_peer(peer_entry)
        elif isinstance(message, P2PGetPeerList):
            count = message.getPeerListRequest.count
            chosen_peers = theApp.peer_manager.normal_peers[0:count]
            response_msg = P2PGetPeerListResponse()
            for peer in chosen_peers:
                agent_data = AgentData()
                agent_data.id = peer.ID
                agent_data.token = peer.Token
                agent_data.publicKey = peer.PublicKey
                agent_data.peerStatus = peer.Status
                agent_data.agentIP = peer.IP
                agent_data.agentPort = peer.Port
                response_msg.peers.append(agent_data)
            data = MessageFactory.encode(response_msg)
            self.transport.write(data)
        elif isinstance(message, P2PGetPeerListResponse):
            for agent_data in message.peers:
                peer_entry = PeerEntry()
                peer_entry.Type = 1
                peer_entry.ID = agent_data.id
                peer_entry.IP = agent_data.agentIP
                peer_entry.Port = agent_data.agentPort
                peer_entry.Token = agent_data.token
                peer_entry.PublicKey = agent_data.publicKey
                peer_entry.Status = agent_data.peerStatus
                theApp.peer_manager.add_normal_peer(peer_entry)

    def close(self):
        if self.ID in theApp.peer_manager.normal_peers:
            theApp.peer_manager.normal_peers[self.ID].Status = 'Disconnected'

########################################################################
class DesktopSuperAgentSession(Session):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, id_, transport):
        """Constructor"""
        Session.__init__(self, id_, transport)

    def get_super_peer_list(self, count):
        g_logger.info("Send P2PGetSuperPeerList message to %s", self.remote_ip)
        request_msg = P2PGetSuperPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._send_request(protocol.transport, data)

    def get_peer_list(self, count):
        g_logger.info("Send P2PGetPeerList message to %s", self.remote_ip)
        request_msg = P2PGetPeerList()
        request_msg.count = count
        data = MessageFactory.encode(request_msg)
        self._send_request(protocol.transport, data)

    def _send_request(self, data=""):
        self.transport.write(data)

    def handle_message(self, message):
        if isinstance(message, P2PGetSuperPeerList):
            count = message.getSuperPeerListRequest.count
            chosen_peers = theApp.peer_manager.super_peers[0:count]
            response_msg = P2PGetSuperPeerListResponse()
            for speer in chosen_peers:
                agent_data = AgentData()
                agent_data.id = speer.ID
                agent_data.token = speer.Token
                agent_data.publicKey = speer.PublicKey
                agent_data.peerStatus = speer.Status
                agent_data.agentIP = speer.IP
                agent_data.agentPort = speer.Port
                response_msg.peers.append(agent_data)
            data = MessageFactory.encode(response_msg)
            self.transport.write(data)
        elif isinstance(message, P2PGetSuperPeerListResponse):
            for agent_data in message.peers:
                peer_entry = PeerEntry()
                peer_entry.Type = 0
                peer_entry.ID = agent_data.id
                peer_entry.IP = agent_data.agentIP
                peer_entry.Port = agent_data.agentPort
                peer_entry.Token = agent_data.token
                peer_entry.PublicKey = agent_data.publicKey
                peer_entry.Status = agent_data.peerStatus
                theApp.peer_manager.add_super_peer(peer_entry)
        elif isinstance(message, P2PGetPeerList):
            count = message.getPeerListRequest.count
            chosen_peers = theApp.peer_manager.normal_peers[0:count]
            response_msg = P2PGetPeerListResponse()
            for peer in chosen_peers:
                agent_data = AgentData()
                agent_data.id = peer.ID
                agent_data.token = peer.Token
                agent_data.publicKey = peer.PublicKey
                agent_data.peerStatus = peer.Status
                agent_data.agentIP = peer.IP
                agent_data.agentPort = peer.Port
                response_msg.peers.append(agent_data)
            data = MessageFactory.encode(response_msg)
            self.transport.write(data)
        elif isinstance(message, P2PGetPeerListResponse):
            for agent_data in message.peers:
                peer_entry = PeerEntry()
                peer_entry.Type = 1
                peer_entry.ID = agent_data.id
                peer_entry.IP = agent_data.agentIP
                peer_entry.Port = agent_data.agentPort
                peer_entry.Token = agent_data.token
                peer_entry.PublicKey = agent_data.publicKey
                peer_entry.Status = agent_data.peerStatus
                theApp.peer_manager.add_normal_peer(peer_entry)

    def close(self):
        if self.ID in theApp.peer_manager.super_peers:
            theApp.peer_manager.super_peers[self.ID].Status = 'Disconnected'