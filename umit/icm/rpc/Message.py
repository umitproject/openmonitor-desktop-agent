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

import umit.icm.rpc.messages_pb2
from umit.icm.utils.BinaryHelper import BinaryReader

MAX_MESSAGE_LENGTH = 1024 * 1024   # max message length is 1M

class MalformedMessageError(Exception):
    """ Received a malformed message """

class Message(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.length = 0
        self.lengthBuffer = ''
        self.offset = 0
        self.remaining = 0
        self.completed = False
        self.content = None
        self.reader = None
        self.type_ = None
        self.encrypted = False
        
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
            self.reader = BinaryReader(self.content)
        else:
            self.content[self.offset:self.offset+dataLen] = data[offset:]
            self.offset += dataLen
            self.remaining -= dataLen
            return ''
        
        return data
    
    def decode(self):
        if not self.completed: 
            return
                
        self.type_ = self.reader.readSzString()
        pass
    
    def decrypt(self):
        if not self.completed: 
            return
        pass
        
        
if __name__ == "__main__":
    data = '\x03\x00\x00\x00'
    msg = Message()
    data = msg.fill('\x05\x00')
    data = msg.fill('\x00\x00A')
    data = msg.fill('B')
    data = msg.fill('CDEFG')
    print(msg.content)
    print(data)
