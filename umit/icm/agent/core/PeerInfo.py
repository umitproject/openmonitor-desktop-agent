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

from umit.icm.agent.Global import g_logger, g_db_helper
from umit.icm.agent.utils.Network import get_local_ip, get_public_ip

########################################################################
class PeerInfo(object):
    """"""
    ID = 10000
    Username = ''
    AuthToken = ''
    Email = ''
    PublicKey = ''
    PrivateKey = ''
    
    props = {}    

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.load()
        self.props['ip'] = get_local_ip()
        self.props['public_ip'] = get_public_ip()
        
    def load(self):
        rs = g_db_helper.select('select * from user_info')
        if len(rs) > 0:
            if len(rs) > 1:            
                g_logger.warning("There're more than one record in user_info. "
                                 "We use the first one.")
            
            g_logger.debug(rs[0])
            self.ID = rs[0][0]
            self.Username = rs[0][1]
            self.AuthToken = rs[0][2]
            self.Email = rs[0][3]
            self.PublicKey = rs[0][4]
            self.PrivateKey = rs[0][5]
        rs = g_db_helper.select('select * from kvp')
        for entry in rs:
            self.props[entry[0]] = g_db_helper.unpack(entry[1])
            
    def save(self):
        g_db_helper.execute("delete from user_info")
        g_db_helper.execute("insert into user_info values (" + str(self.ID) + 
                            ",'" + self.Username + "','" + self.AuthToken + 
                            "','" + self.Email + "','" + self.PublicKey + 
                            "','" + self.PrivateKey + "')")
        g_db_helper.execute("delete from kvp")
        sql = "insert into kvp values (?, ?)"
        for key in self.props:
            g_db_helper.execute(sql, (key, g_db_helper.pack(self.props[key])))
        g_db_helper.commit()

    def getPublicKey(self):
        return self._public_key
    
    def getPrivateKey(self):
        return self._private_key
    
    def getLocalIP(self):
        return self._ip
    
    def getPublicIP(self):
        return self._pub_ip
    
if __name__ == "__main__":
    pi = PeerInfo()
    pi.load()