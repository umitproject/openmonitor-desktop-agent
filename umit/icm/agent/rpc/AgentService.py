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
    execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

from twisted.application import service
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, ServerFactory

import sys
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.rpc.aggregator import *
from umit.icm.agent.rpc.message import RawMessage, MalformedMessageError
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.icm.agent.rpc.MessageType import *

########################################################################
class AgentProtocol(Protocol):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.remote_ip = None
        self._rawMessage = RawMessage()
        self._handler = CommonHandler()
        
    def connectionMade(self):
        self.factory.connectionNum = self.factory.connectionNum + 1
        g_logger.info("New connection established. From %s" % 
                      self.transport.getPeer())
        g_logger.info(self.factory.connectionNum)
        maxConnectionNum = g_config.getint('network', 'max_connections_num')
        if self.factory.connectionNum > maxConnectionNum:
            self.transport.write("Too many connections, try later") 
            self.transport.loseConnection()
        self.remote_ip = self.transport.getPeer().host        

    def connectionLost(self, reason):
        self.factory.connectionNum = self.factory.connectionNum - 1
        g_logger.info("Connection closed.")
        g_logger.info(self.factory.connectionNum)

    def dataReceived(self, data):
        print(data)
        while len(data) != 0:
            try:
                data = self.rawMessage.fill(data)
            except MalformedMessageError:
                self.transport.write("Malformed message received. "\
                                     "Connection tear down.") 
                theApp.log.warning("Malformed message received. "\
                                   "Connection tear down. %s\n%s" % \
                                   (self.transport.getPeer(), data))
                self.transport.loseConnection()
                return
                
            if self.rawMessage.completed:
                self._handler.process(self.rawMessage)
                self.rawMessage = RawMessage()
                
########################################################################
class CommonHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    def process(self, raw_message):
        message = MessageFactory.decode(raw_message)
        if message.type_ == "handshake":
            # handshake
            pass
        else:
            # rpc call
            if type(message) == AssignTask:                
                g_test_manager.add_test()
            else:
                pass

########################################################################
class AggregatorHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    def process(self, raw_message):
        pass
    
########################################################################
class SuperAgentHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    def process(self, raw_message):
        pass
    
########################################################################
class DesktopAgentHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    def process(self, raw_message):
        pass
    
########################################################################
class MobileAgentHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    def process(self, raw_message):
        pass
        
########################################################################
class AgentFactory(ServerFactory):
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
    port = theApp.config.getint('network', 'listen_port')
    reactor.listenTCP(port, AgentFactory())
    
    reactor.run()
        
    
        
        
    
    