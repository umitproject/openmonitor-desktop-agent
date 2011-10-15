#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
##
## Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import os
import base64


DEFAULT_BLOCK_SIZE = 32
DEFAULT_PADDING = '{'
RANDOM_PARAM = 32
CHALLENGE_SIZE = 10
RSA_KEY_SIZE = 1024

class CryptoLib:

    def __init__(self, blockSize=DEFAULT_BLOCK_SIZE, padding=DEFAULT_PADDING):
        self.blockSize = blockSize
        self.padding = padding

    def generateRSAKey(self, size=RSA_KEY_SIZE):
        # generate new RSA key
        keyPair = RSA.generate(size, os.urandom)
        # export keys
        key = {}
        key['public'] = RSAKey(keyPair.n, keyPair.e)
        key['private'] = RSAKey(keyPair.n, keyPair.e, keyPair.d, keyPair.p, keyPair.q, keyPair.u)
        return key

    def pad(self, data):
        paddedData = data + (self.blockSize - len(data) % self.blockSize) * self.padding
        return paddedData

    def generateAESKey(self):
        secret = os.urandom(self.blockSize)
        return base64.b64encode(secret)

    def encodeRSAPrivateKey(self, data, key):
        # get RSA private key
        privateKey = key.getPrivateKey()
        # encode data
        return self.__encodeRSA(data, privateKey)

    def encodeRSAPublicKey(self, data, key):
        # get RSA public key
        publicKey = key.getPublicKey()
        # encode data
        return self.__encodeRSA(data, publicKey)

    def __encodeRSA(self, data, key):
        # encode data
        encodedData = key.encrypt(data, 32)
        return base64.b64encode(encodedData[0])
        #return encodedData

    def decodeRSAPrivateKey(self, encodedData, key):
        # get RSA private key
        privateKey = key.getPrivateKey()
        # decode data
        return self.__decodeRSA(encodedData, privateKey)

    def decodeRSAPublicKey(self, encodedData, key):
        # get RSA public key
        publicKey = key.getPublicKey()
        # encode data
        return self.__decodeRSA(encodedData, publicKey)

    def __decodeRSA(self, encodedData, key):
        # decode data
        data = key.decrypt(base64.b64decode(encodedData))
        #data = key.decrypt(encodedData)
        return data

    def encodeAES(self, data, secret):
        # base64 decode secret
        secret = base64.b64decode(secret)
        # generate cipher from secret
        cipher = AES.new(secret)
        # encode data
        encodedData = base64.b64encode(cipher.encrypt(self.pad(data)))
        return encodedData

    def decodeAES(self, encodedData, secret):
        # base64 decode secret
        secret = base64.b64decode(secret)
        # generate cipher from secret
        cipher = AES.new(secret)
        # decode data
        data = cipher.decrypt(base64.b64decode(encodedData)).rstrip(self.padding)
        return data

    def signRSA(self, data, key):
        privateKey = key.getPrivateKey()
        signed = privateKey.sign(str(data), '')
        return base64.b64encode(str(signed[0]))

    def verifySignatureRSA(self, challenge, signedChallenge, key):
        publicKey = key.getPublicKey()
        return publicKey.verify(str(challenge), (long(base64.b64decode(signedChallenge)),))

    def generateChallenge(self):
        return base64.b64encode(os.urandom(CHALLENGE_SIZE))


class RSAKey:

    def __init__(self, mod, exp, d=None, p=None, q=None, u=None):
        self.mod = mod
        self.exp = exp
        self.d = d
        self.p = p
        self.q = q
        self.u = u

    def getPublicKey(self):
        rsaKey = RSA.construct((long(self.mod), long(self.exp)))
        return rsaKey.publickey()

    def getPrivateKey(self):
        rsaKey = RSA.construct((long(self.mod), long(self.exp), long(self.d), long(self.p), long(self.q), long(self.u)))
        return rsaKey