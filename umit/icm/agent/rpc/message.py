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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import struct

from umit.proto.messages_pb2 import *
from umit.icm.agent.rpc.messages_ext_pb2 import *
from umit.icm.agent.rpc.MessageID import *

MAX_MESSAGE_LENGTH = 1024 * 1024   # max message length is 1M


class MalformedMessageError(Exception):
    """ Received a malformed message """

class RawMessage(object):
    """"""

    def __init__(self):
        """Constructor"""
        self.length = 0
        self.lengthBuffer = ''
        self.offset = 0
        self.remaining = 0
        self.completed = False
        self.content = None

    def fill(self, data):
        if self.completed:
            return data

        offset = 0
        if self.length == 0:
            # fill the length field first
            if len(data) >= 4-len(self.lengthBuffer):
                offset += 4-len(self.lengthBuffer)
                self.lengthBuffer += data[:offset]
                self.length = struct.unpack('!I', self.lengthBuffer)[0]
                if self.length > MAX_MESSAGE_LENGTH:
                    raise MalformedMessageError
                self.content = bytearray(self.length)
                self.remaining = self.length
            else:
                self.lengthBuffer += data
                return ''

        dataLen = len(data)-offset
        if dataLen >= self.remaining:
            self.content[self.offset:self.length] = data[offset:offset+self.remaining]
            data = data[self.remaining+offset:]
            self.remaining = 0
            self.completed = True
        else:
            self.content[self.offset:self.offset+dataLen] = data[offset:]
            self.offset += dataLen
            self.remaining -= dataLen
            return ''

        return data


if __name__ == "__main__":
    msg_send = WebsiteReport()
    msg_send.agentType = 2
    msg_send.agentID = '11111'
    msg_send.agentPort = 8000
    print(msg_send)
    str_ = msg_send.SerializeToString()
    print(str_)
    msg_recv = AuthenticatePeer()
    msg_recv.ParseFromString(str_)
    print(msg_recv)
    if msg_recv.HasField("checkCode"):
        print("Has check code")
    else:
        print("Doesn't have check code")

    #data = '\x03\x00\x00\x00'
    #msg = RawMessage()
    #data = msg.fill('\x05\x00')
    #data = msg.fill('\x00\x00A')
    #data = msg.fill('B')
    #data = msg.fill('CDEFG')
    #print(msg.content)
    #print(data)
