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

from umit.icm.agent.rpc.message import message_creator, message_type_to_id, \
     message_id_to_type
from umit.icm.agent.utils.StringBinaryHelper import BinaryReader, BinaryWriter

class MessageFactory(object):
    """"""
    _reader = BinaryReader()
    _writer = BinaryWriter()

    #----------------------------------------------------------------------
    #def __init__(self):
        #"""Constructor"""

    @classmethod
    def create(cls, msg_type):
        return message_creator[msg_type]()

    @classmethod
    def encode(cls, message):
        cls._writer.reset()
        msg_type = message.DESCRIPTOR.name
        msg_type_id = message_type_to_id[msg_type]
        msg_str = message.SerializeToString()
        total_length = 4 + len(msg_str)
        cls._writer.writeInt32(total_length)
        cls._writer.writeInt32(msg_type_id)
        cls._writer.writeFixedLengthString(msg_str, len(msg_str))
        return cls._writer.getString()

    @classmethod
    def decode(cls, str_):
        cls._reader.setString(str_)
        msg_type_id = cls._reader.readInt32()
        msg_type = message_id_to_type[msg_type_id]
        message = cls.create(msg_type)
        msg_str = cls._reader.readFixedLengthString(len(str_)-4)
        message.ParseFromString(msg_str)
        return message

    @classmethod
    def encrypt(cls, str_):
        pass

    @classmethod
    def decrypt(cls, str_):
        pass
