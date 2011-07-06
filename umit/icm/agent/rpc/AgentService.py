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
"""
The agent will bind on a static port and serve the other peers.
We use port multiplexing to handle different packets from the aggregator,
super agents, desktop agents, and mobile agents.
"""

try:
    execfile('E:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

import random
import struct
import time

from twisted.application import service
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, ServerFactory, \
     ClientFactory

from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.aggregator import AggregagorSession
from umit.icm.agent.rpc.desktop import DesktopAgentSession, \
     DesktopSuperAgentSession
from umit.icm.agent.rpc.mobile import MobileAgentSession

########################################################################
class AgentProtocol(Protocol):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.local_ip = None
        self.local_port = None

        self.remote_ip = None
        self.remote_port = 0

        self.remote_id = 0
        self.remote_type = 0

        self._session = None
        self._auth_sent = False
        self._rawMessage = RawMessage()
        #self._nonce = int(random.getrandbits(31))

    def connectionMade(self):
        self.factory.connectionNum = self.factory.connectionNum + 1
        g_logger.info("New connection established. with Peer: %s" %
                      self.transport.getPeer())
        g_logger.info("Connection num: %d" % self.factory.connectionNum)

        maxConnectionNum = g_config.getint('network', 'max_connections_num')
        if self.factory.connectionNum > maxConnectionNum:
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()

        self.local_ip = self.transport.getHost().host
        self.local_port = self.transport.getHost().port
        self.remote_ip = self.transport.getPeer().host
        self.remote_port = self.transport.getPeer().port

        # initiator send AuthenticatePeer message
        if self.local_port != theApp.listen_port:
            self._session = self._send_auth_message()

    def connectionLost(self, reason):
        self.factory.connectionNum = self.factory.connectionNum - 1
        g_logger.info("Connection closed.")
        g_logger.info("Current connection num: %d" % self.factory.connectionNum)

        if self._session is not None:
            self._session.close()
            del theApp.peer_manager.sessions[self.remote_id]

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

            if self._rawMessage.completed:
                g_logger.debug("recv message length: %d" % self._rawMessage.length)
                #g_logger.debug(self._rawMessage.content)
                message = MessageFactory.decode(str(self._rawMessage.content))
                g_logger.debug("Received a %s message from %s.\n%s" % \
                               (message.DESCRIPTOR.name,
                                self.transport.getPeer(),
                                message))
                if isinstance(message, AuthenticatePeer):
                    self.remote_id = message.peerID
                    self.remote_type = message.peerType
                    if message.peerType == 0:  # aggregator
                        self._session = AggregatorSession(message.peerID,
                                                          self.transport)
                    elif message.peerType == 1:  # super agent
                        theApp.peer_manager.add_super_peer(self.remote_id,
                                                           self.remote_ip,
                                                           message.servePort,
                                                           'Connected')
                        self._session = DesktopSuperAgentSession(message.peerID,
                                                                 self.transport)
                    elif message.peerType == 2:  # desktop agent
                        theApp.peer_manager.add_normal_peer(self.remote_id,
                                                            self.remote_ip,
                                                            message.servePort,
                                                            'Connected')
                        self._session = DesktopAgentSession(message.peerID,
                                                            self.transport)
                    elif message.peerType == 3:  # mobile agent
                        theApp.peer_manager.add_mobile_peer(self.remote_id,
                                                            self.remote_ip,
                                                            message.servePort,
                                                            'Connected')
                        self._session = MobileAgentSession(message.peerID,
                                                           self.transport)
                    else:  # wrong type
                        pass
                    theApp.peer_manager.\
                          sessions[message.peerID] = self._session
                    g_logger.info("Session %d created." % message.peerID)
                    # send auth message if didn't
                    if not self._auth_sent:
                        self._send_auth_message()
                elif isinstance(message, Diagnose):
                    self._handle_diagnose(message)
                elif self._session is not None:
                    self._session.handle_message(message)
                else:
                    g_logger.warning("Unexpected message. %s" %
                                     message.DESCRIPTOR.name)
                self._rawMessage = RawMessage()

    def _send_auth_message(self):
        request_msg = AuthenticatePeer()
        request_msg.peerID = theApp.peer_info.ID
        request_msg.peerType = theApp.peer_info.Type
        request_msg.servePort = theApp.listen_port
        #request_msg.cipheredKey = theApp.peer_info.cipheredKey
        g_logger.debug("Sending AuthenticatePeer message:\n%s" % request_msg)
        data = MessageFactory.encode(request_msg)
        self.transport.write(data)
        self._auth_sent = True

    def _handle_diagnose(self, message):
        if message.execType == 0:
            response_msg = DiagnoseResponse()
            response_msg.execTime = int(time.time())
            try:
                response_msg.result = str(eval(message.command))
            except Exception, e:
                response_msg.result = str(e)
            data = MessageFactory.encode(response_msg)
            self.transport.write(data)
        elif message.execType == 1:
            pass

########################################################################
class AgentFactory(ServerFactory, ClientFactory):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.protocol = AgentProtocol
        self.connectionNum = 0;
        self.peers = []

########################################################################
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





