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

from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.Errors import *
from umit.icm.agent.secure.Key import *

########################################################################
class KeyManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # Load Aggregator Public Key
        ag_pubkey = g_db_helper.get_value('aggregator_public_key', None)
        if not ag_pubkey:
            raise InitializationError("Missing aggregator public key.")
        self.aggregator_public_key = RSAPublicKey()
        self.aggregator_public_key.construct(*ag_pubkey)

        public_key = g_db_helper.get_value('public_key')
        private_key = g_db_helper.get_value('private_key')
        if not public_key or not private_key:
            # Generate RSA key
            g_logger.info("Generate RSA key for first time running.")
            self.private_key = RSAPrivateKey()
            self.private_key.generate()
            self.public_key = RSAPublicKey()
            self.public_key.construct(self.private_key.mod, self.private_key.exp)

            # write into db
            g_db_helper.set_value('public_key', (self.public_key.mod,
                                                 self.public_key.exp))
            g_db_helper.set_value('private_key', (self.private_key.obj.n,
                                                  self.private_key.obj.e,
                                                  self.private_key.obj.d,
                                                  self.private_key.obj.p,
                                                  self.private_key.obj.q,
                                                  self.private_key.obj.u))
        else:
            self.public_key = RSAPublicKey()
            self.public_key.construct(*public_key)
            self.private_key = RSAPrivateKey()
            self.private_key.construct(*private_key)

        ag_aeskey = g_db_helper.get_value('aggregator_aes_key')
        self.aggregator_aes_key = None
        if ag_aeskey:
            self.aggregator_aes_key = AESKey()
            self.aggregator_aes_key.set_key(ag_aeskey)

        self.public_keys = {}
        self.symmetric_keys = {}

    def set_public_key(self, name, public_key):
        self.public_keys[name] = public_key

    def get_public_key(self, name):
        if name in self.public_keys:
            return self.public_keys[name]
        else:
            g_logger.warn("Public key for '%s' not found." % name)
            return None
