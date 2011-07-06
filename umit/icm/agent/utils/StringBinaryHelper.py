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
    def __init__(self, str_=''):
        self.str_ = str_
        self.length = len(str_)
        self.offset = 0
        self.remaining = self.length

    def reset(self):
        self.offset = 0
        self.remaining = self.length

    def setString(self, str_):
        self.str_ = str_
        self.length = len(str_)
        self.offset = 0
        self.remaining = self.length

    def readByte(self):
        if self.remaining == 0:
            raise ExceedLengthError
        else:
            byte = self.str_[offset]
            self.offset = self.offset + 1
            self.remaining = self.remaining - 1
            return byte

    def readBytes(self, length):
        if self.remaining < length:
            raise ExceedLengthError
        else:
            bytes = self.str_[self.offset:self.offset+length]
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
        length = self.readUInt32()
        return self.unpack(str(length) + 's', length)

    def readSzString(self):
        endPos = self.str_.find('\x00', self.offset)
        if endPos == -1:
            raise ExceedLengthError
        else:
            szStr = self.str_[self.offset:endPos]
            self.offset = endPos + 1
            self.remaining = self.length - self.offset
            return szStr

    def readFixedLengthString(self, length):
        return self.unpack(str(length) + 's', length)

    def unpack(self, fmt, length = 1):
        return unpack(fmt, self.readBytes(length))[0]

class BinaryWriter(object):
    def __init__(self, str_=''):
        self.str_ = str_

    def reset(self):
        self.str_ = ''

    def getString(self):
        return self.str_

    def writeByte(self, byte):
        self.str_ = self.str_ + byte

    def writeBytes(self, bytes_):
        self.str_ = self.str_ + bytes_

    def writeChar(self, c):
        self.pack('b', c)

    def writeUChar(self, uc):
        self.pack('B', uc)

    def writeBool(self, b):
        self.pack('?', b)

    def writeInt16(self, s):
        self.pack('h', s)

    def writeUInt16(self, us):
        self.pack('H', us)

    def writeInt32(self, i):
        self.pack('i', i)

    def writeUInt32(self, ui):
        self.pack('I', ui)

    def writeInt64(self, l):
        self.pack('q', l)

    def writeUInt64(self, ul):
        self.pack('Q', ul)

    def writeFloat(self, f):
        self.pack('f', f)

    def writeDouble(self, d):
        self.pack('d', d)

    def writeString(self, str_):
        self.writeUInt32(len(str_))
        self.pack(str(len(str_)) + 's', str_)

    def writeSzString(self, str_):
        self.pack(str(len(str_)) + 's', str_)
        self.writeChar(0)

    def writeFixedLengthString(self, str_, length):
        self.pack(str(length) + 's', str_)

    def pack(self, fmt, param):
        self.writeBytes(pack(fmt, param))


if __name__ == "__main__":
    br = BinaryReader("\x01\x00\x00\x00\x03\x00ABCDEF\x00GHI\x00")
    print(br.readUInt16())
    print(br.readString())
    print(br.readSzString())
    print(br.readSzString())
    bw = BinaryWriter()
    bw.writeBool(False)
    bw.writeString('h')
    bw.writeSzString('good')
    bw.writeInt32(65)
    print(bw.getString())




