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

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, ServerFactory

import sys
import UmitImporter
from umit.icm.Config import config
from umit.icm.Logging import log
from umit.icm.rpc.aggregator import *
from umit.icm.rpc.Message import Message, MalformedMessageError
from umit.icm.rpc.MessageType import *

########################################################################
class AgentProtocol(Protocol):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.message = Message()
        
    def connectionMade(self):
        self.factory.connectionNum = self.factory.connectionNum + 1
        log.info("New connection established.")
        log.info(self.factory.connectionNum)
        maxConnectionNum = config.getint('network', 'max_connections_num')
        if self.factory.connectionNum > maxConnectionNum:
            self.transport.write("Too many connections, try later") 
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.connectionNum = self.factory.connectionNum - 1
        log.info("Connection closed.")
        log.info(self.factory.connectionNum)

    def dataReceived(self, data):
        print(data)        
        while len(data) != 0:
            try:
                data = self.message.fill(data)
            except MalformedMessageError:
                self.transport.write("Malformed message received. Connection tear down.") 
                log.warning("Malformed message received. Connection tear down. %s\n%s" % (self.transport.getHost(), data))
                self.transport.loseConnection()
                return
                
            if self.message.completed:
                self.handleMessage(self.message)
                self.message = Message()
        
    def handleMessage(self, message):
        message.decode()
        if message.type_ == "handshake":
            # handshake
            pass
        else:
            # rpc call
            if message.encrypted:
                message.decrypt()
            
            if message.type_ == ASSIGN_TASK:
                at = AssignTaskResponser(message)
                at.execute()
            else:
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
    
    
        
if __name__ == "__main__":
    port = config.getint('network', 'listen_port')
    reactor.listenTCP(port, AgentFactory())
    
    reactor.run()
        
    
        
        
    
    