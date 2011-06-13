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

########################################################################
class PeerEntry:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
    ID = 0
    IP = None
    Geo = None

########################################################################
class PeerManager:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.super_peers = {}
        self.normal_peers = {}
        self.mobile_peers = {}
        
    def add_super_peer(self, id, transport):
        peer_entry = PeerEntry()
        peer_entry.ID = id
        peer_entry.IP = transport.GetPeer()
        # check if exists
        if id not in self.super_peers:
            self.super_peers[id] = peer_entry
        
    def add_normal_peer(self, id, transport):
        peer_entry = PeerEntry()
        peer_entry.ID = id
        peer_entry.IP = transport.GetPeer()
        # check if exists
        if id not in self.normal_peers:
            self.normal_peers[id] = peer_entry
            
    def add_mobile_peer(self, id, transport):
        peer_entry = PeerEntry()
        peer_entry.ID = id
        peer_entry.IP = transport.GetPeer()
        # check if exists
        if id not in self.mobile_peers:
            self.mobile_peers[id] = peer_entry
    
    