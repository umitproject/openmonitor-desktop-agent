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

from umit.icm.agent.rpc.messages_pb2 import *
from umit.icm.agent.utils.StringBinaryHelper import BinaryReader, BinaryWriter

class MessageFactory(object):
    """"""
    _reader = BinaryReader()
    _writer = BinaryWriter()
    _creator = {'AssignTask': AssignTask}

    #----------------------------------------------------------------------
    #def __init__(self):
        #"""Constructor"""
        
    @classmethod
    def create(cls, msg_type):        
        return cls.creator[msg_type]()
    
    @classmethod
    def encode(cls, message):
        cls.writer.reset()
        cls.writer.writeString(message.DESCRIPTOR.name)
        cls.writer.writeString(message.SerializeToString())        
        return cls.writer.getString()
    
    @classmethod
    def decode(cls, str_):
        cls.reader.setString(str_)
        msg_type = cls.reader.readString()
        message = cls.create(msg_type)
        msg_str = cls.reader.readString()
        message.ParseFromString(msg_str)
        return message
    
    @classmethod
    def encrypt(cls, str_):
        pass
    
    @classmethod
    def decrypt(cls, str_):
        pass
    
if __name__ == "__main__":
    MessageFactory.create('AssignTask')
    MessageFactory.encode()
    
    pass