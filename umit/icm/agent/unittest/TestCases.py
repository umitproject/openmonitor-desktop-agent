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

import os
import random
import socket
import unittest

# find ROOT dir
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir

execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))

from twisted.internet import reactor

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

class AgentServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.listen_port = 5895
        from umit.icm.agent.rpc.AgentService import AgentFactory
        reactor.listenTCP(self.listen_port, AgentFactory())
        #reactor.run()

    def tearDown(self):
        reactor.stop()

    def test_super_agent_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        s.connect(('127.0.0.1', self.listen_port))
        request_msg = AuthenticatePeer()
        request_msg.agentID = random.randint(10000, 99999)
        request_msg.agentType = 2
        request_msg.agentPort = random.randint(5900, 6000)
        request_msg.cipheredPublicKey = 'null'
        data = MessageFactory.encode(request_msg)
        s.send(data)
        length = struct.unpack('!i', s.recv(4))[0]
        data = s.recv(length)
        response_msg = MessageFactory.decode(data)
        s.close()

    def test_desktop_agent_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        s.connect(('127.0.0.1', self.listen_port))
        request_msg = AuthenticatePeer()
        request_msg.agentID = random.randint(10000, 99999)
        request_msg.agentType = 3
        request_msg.agentPort = random.randint(5900, 6000)
        request_msg.cipheredPublicKey = 'null'
        data = MessageFactory.encode(request_msg)
        s.send(data)
        length = struct.unpack('!i', s.recv(4))[0]
        data = s.recv(length)
        response_msg = MessageFactory.decode(data)
        s.close()

    def test_mobile_agent_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        s.connect(('127.0.0.1', self.listen_port))
        request_msg = AuthenticatePeer()
        request_msg.agentID = random.randint(10000, 99999)
        request_msg.agentType = 4
        request_msg.agentPort = random.randint(5900, 6000)
        request_msg.cipheredPublicKey = 'null'
        data = MessageFactory.encode(request_msg)
        s.send(data)
        length = struct.unpack('!i', s.recv(4))[0]
        data = s.recv(length)
        response_msg = MessageFactory.decode(data)
        s.close()

if __name__ == "__main__":
    msg = AgentUpdate()
    msg.version = "1.0"
    msg.downloadURL = "http://202.206.64.11/icm-agent.temp.tar.gz"
    msg.checkCode = 0
    data = MessageFactory.encode(msg)
    print(len(data))
    print(data)
