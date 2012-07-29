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

labels = ('', 'optional', 'required', 'repeated')
cpp_types = ('', 'int32', 'int64', 'uint32', 'uint64', 'double', 'float',
         'bool', 'enum', 'string', 'message')

while newFlag == 'y':
    print("---------Client Request Begin---------")
    msg_type = raw_input("Message type: ")
    request_msg = MessageFactory.create(msg_type)
    for field in request_msg.DESCRIPTOR.fields:
        value = raw_input("[%s] %s(%s): " % (labels[field.label], field.name,
                                             cpp_types[field.cpp_type]))
        if field.label == field.LABEL_REQUIRED:
            while value == '':
                print("Error! This field is required.")
                value = raw_input("[%s] %s(%s): " % (labels[field.label],
                                                    field.name,
                                                    cpp_types[field.cpp_type]))
        if field.cpp_type < 5:
            request_msg._fields[field] = int(value)
        elif field.cpp_type < 7:
            request_msg._fields[field] = float(value)
        elif field.cpp_type == 7:
            request_msg._fields[field] = bool(value)
        elif field.cpp_type == 8:
            request_msg._fields[field] = float(value)
        elif field.cpp_type == 9:
            request_msg._fields[field] = value
        else:
            pass
    data = MessageFactory.encode(request_msg)
    print(data)
    length = struct.pack('!I', len(data))
    s.send(length)
    s.send(data)
    print("----------Client Request End----------")
    print("Message has been sent. Now waiting for result.")
    print("---------Server Response Begin---------")
    length = struct.unpack('!i', s.recv(4))[0]
    data = s.recv(length)
    response_msg = MessageFactory.decode(data)
    print(response_msg)
    print("----------Server Response End----------")

print("bye!")