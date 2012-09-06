#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Authors:  Tianwei Liu <liutianweidlut@gmail.com>
#           
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

import os
import sys
import time
import socket

from umit.icm.agent.logger import g_logger
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from twisted.internet import reactor


class SuperBehaviourByManual(object):
    """
    """
    def __init__(self,application):
        """
        """
        self.application = application
    
    def peer_communication(self):
        """
        """
        if self.check_peer_authentical() == True:
            g_logger.info("Now, the desktop agent will try to connect the super peer")
            
            ###############################################
            #here, we load the necessay information from db
            self.application.login_simulate()
            
            ###############################################
            #check if there are some super peers in peer db,
            #if some are loaded, we will skip this step
            if self.application.peer_manager.super_peers.values() != []:
                print self.application.peer_manager.super_peers.values()
                g_logger.info("Skip super peer add from superpeer by manual list")
                return
            
            super_peer_record = g_db_helper.get_super_peer_first()
            if super_peer_record != None:
                self.build_super_connection(str(super_peer_record[0]),int(super_peer_record[1]))
            else:
                g_logger.info("Sorry! Your super peer table cannot store any peers, you can add known peer and try again")
        else:
            g_logger.info("Sorry! The desktop agent cannot be authenticated by aggregator ago!")
            self.application.quit_window_in_wrong(primary_text = _("The desktop agent cannot be authenticated by aggregator ago"), \
                                      secondary_text = _("Please email to Open Monitor!"))            
 
    def build_super_connection(self,host=None,port=None):
        """
        this method will connect to host:port, to get necessary super peer information,
        and add them into peer list and super peer session.
        we will get peer_id, token, ciphered_public_key from super peer
        """
        if host == None or host == "" or port == None or port == "":
             g_logger.error("Wrong super peer conection information: host->%s, port->%d"%(host,port))
             return
        
        from umit.icm.agent.rpc.message import *
        from umit.icm.agent.rpc.MessageFactory import MessageFactory
        
        g_logger.error('Try to connect to super peer...., to get necessary information!!!')
        
        from umit.icm.agent.utils.CreateDB import mod,exp 
        try:
            s  = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            s.connect((host,port))
        except:
            g_logger.error('Cannot connect to the super peer, maybe it down!')
            return
        
        request_msg = AuthenticatePeer()
        request_msg.agentID = self.application.peer_info.ID
        request_msg.agentType = 2
        request_msg.agentPort = 5895
        request_msg.cipheredPublicKey.mod = str(mod)
        request_msg.cipheredPublicKey.exp = str(exp)
        data = MessageFactory.encode(request_msg)
        length = struct.pack('!I', len(data))
        s.send(length)
        s.send(data)
        length = struct.unpack('!i', s.recv(4))[0]
        data = s.recv(length)
        response_msg = MessageFactory.decode(data)
        
        g_logger.error('Get the super peer information (ip:%s,port:%s,agentID:%s)\
                        with build_super_connection process'%(host,port,response_msg.token))
        
        self.application.peer_manager.add_super_peer(peer_id=response_msg.token,ip=host,port=port)
            
        
    def check_peer_authentical(self):
        """
        Check the peer store the peer information in database
        """
        return g_db_helper.check_peer_info()     
