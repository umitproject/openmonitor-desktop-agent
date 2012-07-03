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

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp


class PeerInfo(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = 0
        self.Type = 2  # normal peer by default
        self.Username = ''
        self.Password = ''
        self.Email = ''
        self.CipheredPublicKeyHash = None

        self.local_ip = ''
        self.internet_ip = ''


        self.is_registered = False
        self.is_logged_in = False

        self.get_local_ip()
        self.get_internet_ip()


        self.country_code = '' 
        

    def load_from_db(self):
        rs = g_db_helper.select('select * from peer_info')
        if not rs:
            g_logger.info("No peer info in db.")
        else:
            if len(rs) > 1:
                g_logger.warning("More than one record in user_info. " \
                                 "Use the last one.")
            g_logger.debug(rs[-1])
            self.ID = rs[-1][0]
            self.Username = rs[-1][1]
            self.Password = rs[-1][2]
            self.Email = rs[-1][3]
            self.CipheredPublicKeyHash = rs[-1][4]
            self.Type = rs[-1][5]
            self.is_registered = True

    def save_to_db(self):
        if self.is_registered:
            sql_str = "insert or replace into peer_info values " \
                            "(%d, '%s', '%s', '%s', '%s', %d, '%s')" % \
                            (self.ID, self.Username, self.Password, self.Email,
                             self.CipheredPublicKeyHash, self.Type, self.country_code)
            g_logger.info("[save_to_db]:save %s into DB"%sql_str)            
            g_db_helper.execute(sql_str)
            g_db_helper.commit()

    def clear_db(self):
        g_db_helper.execute("delete from peer_info")
        g_db_helper.commit()
        
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
    pi.load_from_db()