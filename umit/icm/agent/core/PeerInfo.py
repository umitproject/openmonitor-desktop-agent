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

import cPickle

from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.utils.Network import get_local_ip, get_internet_ip

########################################################################
class PeerInfo(object):
    """"""
    ID = 0
    Type = 2  # normal peer by default
    AuthToken = ''
    Email = ''
    PublicKey = ''
    PrivateKey = ''
    CipheredPublicKey = ''
    AggregatorPublicKey = ''
    props = {}

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.props['local_ip'] = get_local_ip()
        self.props['internet_ip'] = get_internet_ip()
        self.registered = False
        self.login = False

    def _handle_register_response(self, data):
        if data is not None:
            self.ID = data[0]
            self.AuthToken = data[1]
            self.PublicKey = data[2]
            self.PrivateKey = data[3]
            self.CipheredPublicKey = data[4]
            self.AggregatorPublicKey = data[5]
            self.save_to_db()

    def load_from_db(self):
        rs = g_db_helper.select('select * from user_info')
        if not rs:
            g_logger.info("No peer info in db.")
        else:
            if len(rs) > 1:
                g_logger.warning("More than one record in user_info. " \
                                 "Use the first one.")
            g_logger.debug(rs[0])
            self.ID = rs[0][0]
            self.Email = rs[0][1]
            self.AuthToken = rs[0][2]
            self.PublicKey = rs[0][3]
            self.PrivateKey = rs[0][4]
            self.CipheredPublicKey = rs[0][5]
            self.AggregatorPublicKey = rs[0][6]
            self.Type = rs[0][7]
            self.registered = True
        # load properties
        rs = g_db_helper.select('select * from peer_info')
        for entry in rs:
            self.props[entry[0]] = g_db_helper.unpack(entry[1])

    def save_to_db(self):
        if self.registered:
            g_db_helper.execute("insert or replace into user_info values " \
                            "(%d, '%s', '%s', '%s', '%s', '%s', '%s', %d)" % \
                            (self.ID, self.Email, self.AuthToken,
                             self.PublicKey, self.PrivateKey,
                             self.CipheredPublicKey, self.AggregatorPublicKey,
                             self.Type))
        for key in self.props:
            g_db_helper.execute(
                "insert or replace into peer_info values (?, ?)",
                (key, g_db_helper.pack(self.props[key])))
        g_db_helper.commit()


if __name__ == "__main__":
    pi = PeerInfo()
    pi.load()