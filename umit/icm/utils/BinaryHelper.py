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

from struct import *

class ExceedLengthError(Exception):
    "The reading operation exceeds the str length."
    
class BinaryReader(object):
    def __init__(self, bytes_):
        self.bytes_ = bytes_
        self.length = len(bytes_)
        self.offset = 0
        self.remaining = self.length
        
    def reset(self):
        self.offset = 0
        self.remaining = self.length

    def readByte(self):
        if self.remaining == 0:
            raise ExceedLengthError
        else:
            byte = self.bytes_[offset]
            self.offset = self.offset + 1
            self.remaining = self.remaining - 1
            return byte

    def readBytes(self, length):
        if self.remaining < length:
            raise ExceedLengthError
        else:
            bytes = self.bytes_[self.offset:self.offset+length]
            self.offset = self.offset + length 
            self.remaining = self.remaining - length
            return bytes

    def readChar(self):
        return self.unpack('b')

    def readUChar(self):
        return self.unpack('B')

    def readBool(self):
        return self.unpack('?')

    def readInt16(self):
        return self.unpack('h', 2)

    def readUInt16(self):
        return self.unpack('H', 2)

    def readInt32(self):
        return self.unpack('i', 4)

    def readUInt32(self):
        return self.unpack('I', 4)

    def readInt64(self):
        return self.unpack('q', 8)

    def readUInt64(self):
        return self.unpack('Q', 8)

    def readFloat(self):
        return self.unpack('f', 4)

    def readDouble(self):
        return self.unpack('d', 8)

    def readString(self):
        length = self.readUInt16()
        return self.unpack(str(length) + 's', length)
    
    def readSzString(self):        
        endPos = self.bytes_.find('\x00', self.offset)
        if endPos == -1:
            raise ExceedLengthError
        else:
            szStr = self.bytes_[self.offset:endPos]
            self.offset = endPos + 1
            self.remaining = self.length - self.offset
            return szStr

    def unpack(self, fmt, length = 1):
        return unpack(fmt, self.readBytes(length))[0]
    
if __name__ == "__main__":
    br = BinaryReader("\x01\x00\x00\x00\x03\x00ABCDEF\x00GHI\x00")
    print(br.readInt32())
    print(br.readString())
    print(br.readSzString())
    print(br.readSzString())
    
    
    