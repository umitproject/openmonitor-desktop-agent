#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 US

import os
import socket
import struct
import sys
import time

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir))

sys.path.insert(0, ROOT_DIR)

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

address = raw_input("Input peer address(ip:port): ")
ip, port = address.split(':')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
s.connect((ip, int(port)))
newFlag = 'y'

while newFlag == 'y':
    print("---------Client Request Begin---------")
    request_msg = Diagnose()
    #exec_type = int(raw_input("Exec type: "))
    #request_msg.execType = exec_type
    #if exec_type == 1:
        #cron_time = raw_input("Cron time: ")
        #request_msg.cronTime = cron_time
    cmd = raw_input("Commnad: ")
    request_msg.execType = 0
    request_msg.command = cmd
    data = MessageFactory.encode(request_msg)
    length = struct.pack('!I', len(data))
    s.send(length)
    s.send(data)
    print("----------Client Request End----------")
    print("Diagnose message sent. Now waiting for result.")
    print("---------Server Response Begin---------")
    length = struct.unpack('!i', s.recv(4))[0]
    data = s.recv(length)
    response_msg = MessageFactory.decode(data)
    print("Exec time: %s" % time.ctime(response_msg.execTime))
    print("Result:\n%s" % response_msg.result)
    print("----------Server Response End----------")

print("bye!")