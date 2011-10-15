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

import base64

from Crypto.Cipher import AES

DEFAULT_BLOCK_SIZE = 32
DEFAULT_PADDING = '{'

########################################################################
class AESKey(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, block_size=DEFAULT_BLOCK_SIZE):
        """Constructor"""
        self.obj = None
        self.block_size = block_size

    def generate(self):
        # generate a key with alpha, num and +,/,=
        self.key = base64.b64encode(
            Random.get_random_bytes(self.block_size))[:self.block_size]
        self.obj = AES.new(self.key)

    def set_key(self, key):
        if len(key) > self.block_size:
            key = key[:self.block_size]
        elif len(key) < self.block_size:
            key += DEFAULT_PADDING * (self.block_size - len(key))
        self.key = key
        self.obj = AES.new(key)

    def get_key(self):
        return self.key

    def encrypt(self, plaintext):
        if len(plaintext) % self.block_size != 0:
            plaintext += DEFAULT_PADDING * \
                (self.block_size - len(plaintext) % self.block_size)
        return self.obj.encrypt(plaintext)

    def decrypt(self, ciphertext):
        return self.obj.decrypt(ciphertext).rstrip(DEFAULT_PADDING)


from Crypto.PublicKey import RSA
from Crypto import Random

RSA_KEY_SIZE = 1024

########################################################################
class RSAKey(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.obj = None
        self.mod = 0
        self.exp = 0
        self.random = Random.new().read

    def construct(self, mod, exp):
        self.obj = RSA.construct((mod, exp))
        self.mod = self.obj.n
        self.exp = self.obj.e

    def generate(self, bits=RSA_KEY_SIZE):
        self.obj = RSA.generate(bits)
        self.mod = self.obj.n
        self.exp = self.obj.e

    def encrypt(self, plaintext):
        return self.obj.encrypt(plaintext, self.random)[0]

    def decrypt(self, ciphertext):
        return self.obj.decrypt(ciphertext)

if __name__ == "__main__":
    aes_key = AESKey()
    aes_key.generate()
    ct = aes_key.encrypt("Hello World!")
    print(ct)
    pt = aes_key.decrypt(ct)
    print(pt)

    rsa_key = RSAKey()
    rsa_key.generate()
    ct = rsa_key.encrypt('Hello World!')
    print(ct)
    pt = rsa_key.decrypt(ct)
    print('a')
    print(pt)



