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

import struct

from umit.icm.agent.rpc.messages_pb2 import *
from umit.icm.agent.utils.StringBinaryHelper import BinaryReader, BinaryWriter

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
                self.length = struct.unpack('I', self.lengthBuffer)[0]
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

class MessageFactory(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.reader = BinaryReader()
        self.writer = BinaryWriter()
        self.creator = {'AssignTask': AssignTask}
        
    def create(self, msg_type):
        return self.creator[msg_type]()
            
    def encode(self, message):
        self.writer.reset()
        self.writer.writeSzString(message.DESCRIPTOR.name)
        self.writer.writeString(message.SerializeToString())
        return self.writer.getString()
    
    def decode(self, str_):
        self.reader.setString(str_)
        msg_type = self.reader.readSzString()
        message = self.create(msg_type)
        msg_str = self.reader.readString()
        message.ParseFromString(msg_str)
        return message
    
    def encrypt(self):
        pass
    
    def decrypt(self):
        pass
        
        
if __name__ == "__main__":
    s = AssignTask()
    #s.header = RequestHeader()
    s.header.token = "xxx"
    s.header.agentID = 123123
    print(s.SerializeToString())
    f = MessageFactory()
    str_ = f.encode(s)
    print(str_)
    msg = f.decode(str_)
    print(s.SerializeToString())
            
    #data = '\x03\x00\x00\x00'
    #msg = RawMessage()
    #data = msg.fill('\x05\x00')
    #data = msg.fill('\x00\x00A')
    #data = msg.fill('B')
    #data = msg.fill('CDEFG')
    #print(msg.content)
    #print(data)
