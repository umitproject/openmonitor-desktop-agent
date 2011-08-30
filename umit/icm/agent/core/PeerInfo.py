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

########################################################################
class PeerInfo(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = 0
        self.Type = 2  # normal peer by default
        self.AuthToken = ''
        self.Email = ''
        self.PublicKey = ''
        self.PrivateKey = ''
        self.CipheredPublicKey = ''
        self.AggregatorPublicKey = ''

        self.local_ip = ''
        self.internet_ip = ''

        self.registered = False
        self.login = False

        self.get_local_ip()
        self.get_internet_ip()

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
        rs = g_db_helper.select('select * from peer_info')
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
            self.Type = rs[0][6]
            self.registered = True

        self.local_ip = g_db_helper.get_value('local_ip', '')
        self.internet_ip = g_db_helper.get_value('internet_ip', '')

    def save_to_db(self):
        if self.registered:
            g_db_helper.execute("insert or replace into peer_info values " \
                            "(%d, '%s', '%s', '%s', '%s', '%s', %d)" % \
                            (self.ID, self.Email, self.AuthToken,
                             self.PublicKey, self.PrivateKey,
                             self.CipheredPublicKey, self.Type))
        g_db_helper.set_value('local_ip', self.local_ip)
        g_db_helper.set_value('internet_ip', self.internet_ip)

    def get_local_ip(self):
        from socket import socket, SOCK_DGRAM, AF_INET
        ip_urls = ["www.google.com", "www.baidu.com"]
        for each in ip_urls:
            try:
                s = socket(AF_INET, SOCK_DGRAM)
                s.settimeout(3)
                s.connect((each, 0))
                ip = s.getsockname()[0]
                self.local_ip = ip
                #print(each, ip)
                break
            except:
                pass

    def get_internet_ip(self):
        from twisted.web.client import getPage
        ip_urls = ["http://whereismyip.com/", "http://www.whereismyip.org/",
                   "http://myip.eu/"]
        for each in ip_urls:
            getPage(each).addCallback(self._handle_get_internet_ip)

    def _handle_get_internet_ip(self, data):
        import re
        ip = re.search('\d+\.\d+\.\d+\.\d+', data).group(0)
        #print(data, ip)
        self.internet_ip = ip


if __name__ == "__main__":
    pi = PeerInfo()
    pi.load()