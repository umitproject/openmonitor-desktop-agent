#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutiawneidlut@gmail.com>
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
"""
The agent will bind on a static port and serve the other peers.
We use port multiplexing to handle different packets from the aggregator,
super agents, desktop agents, and mobile agents.
"""

import base64
import random
import struct
import time

from twisted.application import service
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, ServerFactory, \
     ClientFactory

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.desktop import DesktopAgentSession, \
     DesktopSuperAgentSession
from umit.icm.agent.rpc.mobile import MobileAgentSession
from umit.proto import messages_pb2

class AgentProtocol(Protocol):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.local_ip = None
        self.local_port = None

        self.remote_ip = None
        self.remote_port = 0

        self.remote_id = None
        self.remote_type = 0

        self._session = None
        self._auth_sent = False
        self._rawMessage = RawMessage()
        #self._nonce = int(random.getrandbits(31))

    def connectionMade(self):
        self.factory.connectionNum = self.factory.connectionNum + 1
        g_logger.info("New connection #%d established. with Peer: %s" % (
                      self.factory.connectionNum, self.transport.getPeer()))

        maxConnectionNum = g_config.getint('network', 'max_conn_num')
        if self.factory.connectionNum > maxConnectionNum:
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()

        self.local_ip = self.transport.getHost().host
        self.local_port = self.transport.getHost().port
        self.remote_ip = self.transport.getPeer().host
        self.remote_port = self.transport.getPeer().port

        # initiator send AuthenticatePeer message
        if self.local_port != theApp.listen_port:
            g_logger.debug("The local port is %s, the listen_port is %s, \
            they are not equal,so we should send authentical information to it!"\
            %(str(self.local_port),str(theApp.listen_port)))
            self._session = self._send_auth_message()
        
        g_logger.info("Peer Connection Made, IP:%s,Port:%s"%(str(self.remote_ip),str(self.remote_port)))

    def connectionLost(self, reason):
        self.factory.connectionNum = self.factory.connectionNum - 1
        g_logger.debug("Connection #%d closed." % self.factory.connectionNum)

        if self._session is not None:
            g_logger.debug("Session %s ended." % self.remote_id)
            if self.remote_type == 1:
                theApp.peer_manager._super_peer_disconnected(self.remote_id)
            elif self.remote_type == 2:
                theApp.peer_manager._normal_peer_disconnected(self.remote_id)

    def dataReceived(self, data):
        #print(data)
        while len(data) != 0:
            try:
                data = self._rawMessage.fill(data)
            except MalformedMessageError:
                self.transport.write("Malformed message received. "\
                                     "Connection tear down.")
                g_logger.warning("Malformed message received. " \
                                 "Connection tear down. %s\n%s" % \
                                 (self.transport.getPeer(), data))
                self.transport.loseConnection()
                return

            # the entire message has been received
            if self._rawMessage.completed:
                g_logger.debug("recv message length: %d" %
                               self._rawMessage.length)
                #g_logger.debug(self._rawMessage.content)
                message = MessageFactory.decode(str(self._rawMessage.content))
                self._handle_message(message)

                self._rawMessage = RawMessage()

    def _handle_message(self, message):
        g_logger.debug("Received a %s message from %s.\n%s" % \
                       (message.DESCRIPTOR.name,
                        self.transport.getPeer(),
                        message))
        if isinstance(message, AuthenticatePeer):
            self.remote_type = message.agentType
            self.remote_id = message.agentID
            if message.HasField("agentPort"):
                serve_port = message.agentPort
            else:
                serve_port = 0
            
            print "-------------------------------------"
            print self.remote_id,self.remote_ip,self.remote_port,self.remote_type
            print "-------------------------------------"
            if self.remote_type == 0:  # aggregator
                # in current stage, aggregator will not connect to desktop agent
                #self._session = AggregatorSession(self.transport)
                #theApp.peer_manager.sessions[message.agentID] = self._session
                pass
            elif self.remote_type == 1:  # super agent
                res = theApp.peer_manager._super_peer_connected(
                    self.remote_id, self.remote_ip, serve_port,
                    message.cipheredPublicKey)
                if res:
                    self._session = DesktopSuperAgentSession(message.agentID,
                                                             self.transport)
                    theApp.peer_manager.sessions[message.agentID] = self._session
                    g_logger.debug("Session %s created." % str(message.agentID))
                    #theApp.statistics.super_agents_num = \
                        #theApp.statistics.super_agents_num + 1
            elif self.remote_type == 2:  # desktop agent
                g_logger.info("Get AuthenticatePeer Request from desktop agent.")
                res = theApp.peer_manager._normal_peer_connected(
                    self.remote_id, self.remote_ip, serve_port,
                    message.cipheredPublicKey)
                print res
                if res:
                    self._session = DesktopAgentSession(message.agentID,
                                                        self.transport)
                    theApp.peer_manager.sessions[message.agentID] = self._session
                    g_logger.debug("Session %s created." % str(message.agentID))
                    theApp.statistics.normal_agents_num = \
                        theApp.statistics.super_agents_num + 1
            elif self.remote_type == 3:  # mobile agent
                if self.remote_id in theApp.peer_manager.mobile_peers:
                    theApp.peer_manager.mobile_peers[self.remote_id]\
                          .status = 'Connected'
                else:
                    theApp.peer_manager.add_mobile_peer(
                        self.remote_id, self.remote_ip, serve_port,
                        message.cipheredPublicKey)
                theApp.statistics.mobile_agents_num = \
                      theApp.statistics.super_agents_num + 1
            else:  # wrong type
                g_logger.warning("Incoming peer type invalid: %d." %
                                 self.remote_type)

            self._send_auth_response_message()
            # send auth message if didn't
            if not self._auth_sent:
                self._send_auth_message()
        elif isinstance(message, AuthenticatePeerResponse):
            g_logger.debug("Get AuthenticatePeerResponse from %d type(1:super , 2:normal, 3:Mobile)"%(self.remote_type))
            if self.remote_type == 1:
                theApp.peer_manager.super_peers[self.remote_id].Token = \
                      message.token
            elif self.remote_type == 2:
                theApp.peer_manager.normal_peers[self.remote_id].Token = \
                      message.token
            elif self.remote_type == 3:
                theApp.peer_manager.mobile_peers[self.remote_id].Token = \
                      message.token
        elif isinstance(message, ForwardingMessage):
            if theApp.peer_info.Type == 1:
                g_logger.debug("Get ForwardingMessage")
                forward_message = MessageFactory.decode(\
                    base64.b64decode(message.encodedMessage))
                if message.destination == 0:
                    defer_ = theApp.aggregator._send_message(forward_message, True)
                    defer_.addCallback(self.send_forward_message_response,
                                       message.identifier)
        elif isinstance(message, Diagnose):
            if message.execType == 0:
                response_msg = DiagnoseResponse()
                response_msg.execTime = int(time.time())
                try:
                    response_msg.result = str(eval(message.command))
                    exec message.command
                except Exception, e:
                    response_msg.result = str(e)
                self._send_message(response_msg)
            elif message.execType == 1:
                pass
        elif self._session is not None:
            #We will handle the message according by the type of the peer(super peer, normal peer, mobile agent)
            self._session.handle_message(message)
        elif self.is_ma_message(message):
            if message.header.agentID in theApp.peer_manager.mobile_peers:
                theApp.ma_service.handle_message(message, self.transport)
            else:
                g_logger.warning("Unauthenticated mobile agent. %s" %
                                 str(message.header.agentID))
        else:
            g_logger.warning("Unexpected message. %s" %
                             message.DESCRIPTOR.name)

    def is_ma_message(self, message):
        if message.DESCRIPTOR.name in (
            'GetPeerList',
            'GetSuperPeerList',
            'SendWebsiteReport',
            'SendServiceReport',
            'GetEvents',
            ):
            return True
        return False

    def _send_auth_message(self):
        request_msg = AuthenticatePeer()
        request_msg.agentID = str(theApp.peer_info.ID)
        request_msg.agentType = theApp.peer_info.Type
        request_msg.agentPort = theApp.listen_port
        request_msg.cipheredPublicKey.mod = str(theApp.key_manager.public_key.mod)
        request_msg.cipheredPublicKey.exp = str(theApp.key_manager.public_key.exp)
        g_logger.debug("Sending AuthenticatePeer message:\n%s" % request_msg)
        self._send_message(request_msg)
        self._auth_sent = True

    def _send_auth_response_message(self):
        response_msg = AuthenticatePeerResponse()
        response_msg.token = str(theApp.peer_info.ID)
        response_msg.cipheredPublicKey.mod = str(theApp.key_manager.public_key.mod)
        response_msg.cipheredPublicKey.exp = str(theApp.key_manager.public_key.exp)
        g_logger.debug("Sending AuthenticatePeerResponse message:\n%s" % \
                       response_msg)
        self._send_message(response_msg)

    def send_forward_message_response(self, message, identifier):
        response_msg = ForwardingMessageResponse()
        response_msg.identifier = identifier
        response_msg.encodedMessage = \
                    base64.b64encode(MessageFactory.encode(message))
        self._send_message(response_msg)

    def _send_message(self, message):
        data = MessageFactory.encode(message)
        len32 = struct.pack('!I', len(data))
        self.transport.write(len32)
        self.transport.write(data)

#---------------------------------------------------------------------
class AgentFactory(ServerFactory, ClientFactory):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.protocol = AgentProtocol
        self.connectionNum = 0;
        self.peers = []

#---------------------------------------------------------------------
class AgentService(service.Service):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    def getAgentFactory(self):
        f = ServerFactory()
        f.protocol = AgentProtocol
        return f

    def startService(self):
        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)
        self.call.cancel()


if __name__ == "__main__":
    port = 5895 #theApp.config.getint('network', 'listen_port')
    reactor.listenTCP(port, AgentFactory())

    reactor.run()





