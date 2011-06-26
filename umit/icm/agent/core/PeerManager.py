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

import random

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from twisted.internet import reactor

########################################################################
class PeerEntry:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.transport = None

    ID = None
    Type = None
    IP = None
    Port = None
    Token = None
    PublicKey = None
    Status = None
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
        self.super_peer_num = 0
        self.normal_peer_num = 0
        self.mobile_peer_num = 0
        self.sessions = {}
        self.load_from_db()

    def save_to_db(self):
        for peer_entry in self.super_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "(%d, %d, '%s', %d, '%s', '%s', '%s', '%s')" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.Token, peer_entry.PublicKey,
                 peer_entry.Geo, peer_entry.Status))
        for peer_entry in self.normal_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "(%d, %d, '%s', %d, '%s', '%s', '%s', '%s')" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.Token, peer_entry.PublicKey,
                 peer_entry.Geo, peer_entry.Status))
        for peer_entry in self.mobile_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "(%d, %d, '%s', %d, '%s', '%s', '%s', '%s')" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.Token, peer_entry.PublicKey,
                 peer_entry.Geo, peer_entry.Status))
        g_db_helper.commit()

    def load_from_db(self):
        result = g_db_helper.select("select * from peers")
        for row in result:
            peer_entry = PeerEntry()
            peer_entry.ID = row[0]
            peer_entry.Type = row[1]
            peer_entry.IP = row[2]
            peer_entry.Port = row[3]
            peer_entry.Token = row[4]
            peer_entry.PublicKey = row[5]
            peer_entry.Geo = row[6]
            peer_entry.Status = row[7]
            if peer_entry.Type == 1:
                self.super_peers[peer_entry.ID] = peer_entry
            elif peer_entry.Type == 2:
                self.normal_peers[peer_entry.ID] = peer_entry
            elif peer_entry.Type == 3:
                self.mobile_peers[peer_entry.ID] = peer_entry

    def connect_all(self):
        for peer_entry in self.super_peers.values():
            if peer_entry.ID not in self.sessions:
                reactor.connectTCP(peer_entry.IP, peer_entry.Port,
                                   theApp.factory)
                g_logger.debug("Connecting to %s:%d..." %
                               (peer_entry.IP, peer_entry.Port))

        for peer_entry in self.normal_peers.values():
            if peer_entry.ID not in self.sessions:
                reactor.connectTCP(peer_entry.IP, peer_entry.Port,
                                   theApp.factory)
                g_logger.debug("Connecting to %s:%d..." %
                               (peer_entry.IP, peer_entry.Port))

        for peer_entry in self.mobile_peers.values():
            if peer_entry.ID not in self.sessions:
                reactor.connectTCP(peer_entry.IP, peer_entry.Port,
                                   theApp.factory)
                g_logger.debug("Connecting to %s:%d..." %
                               (peer_entry.IP, peer_entry.Port))

    def add_super_peer(self, param):
        peer_entry = PeerEntry()
        peer_entry.Type = 1
        peer_entry.ID = param['id']
        peer_entry.IP = param['ip']
        peer_entry.Port = param['port']
        if 'token' in param:
            peer_entry.Token = param['token']
        if 'public_key' in param:
            peer_entry.PublicKey = param['public_key']
        if 'status' in param:
            peer_entry.Status = param['status']
        if peer_entry.ID not in self.super_peers:
            self.super_peers[peer_entry.ID] = peer_entry
            self.super_peer_num = self.super_peer_num + 1

    def add_normal_peer(self, param):
        peer_entry = PeerEntry()
        peer_entry.Type = 2
        peer_entry.ID = param['id']
        peer_entry.IP = param['ip']
        peer_entry.Port = param['port']
        if 'token' in param:
            peer_entry.Token = param['token']
        if 'public_key' in param:
            peer_entry.PublicKey = param['public_key']
        if 'status' in param:
            peer_entry.Status = param['status']
        if peer_entry.ID not in self.normal_peers:
            self.normal_peers[peer_entry.ID] = peer_entry
            self.super_peer_num = self.normal_peer_num + 1

    def add_mobile_peer(self, param):
        peer_entry = PeerEntry()
        peer_entry.Type = 3
        peer_entry.ID = param['id']
        peer_entry.IP = param['ip']
        peer_entry.Port = param['port']
        if 'token' in param:
            peer_entry.Token = param['token']
        if 'public_key' in param:
            peer_entry.PublicKey = param['public_key']
        if 'status' in param:
            peer_entry.Status = param['status']
        if peer_entry.ID not in self.mobile_peers:
            self.mobile_peers[peer_entry.ID] = peer_entry
            self.super_peer_num = self.mobile_peer_num + 1

    def remove_super_peer(self, peer_id):
        if peer_id in self.super_peers:
            if self.super_peers[peer_id].transport:
                print(self.super_peers[peer_id].transport)
            del self.super_peers[peer_id]
            self.super_peer_num = self.super_peer_num - 1

    def remove_normal_peer(self, id):
        if peer_id in self.normal_peers:
            if self.normal_peers[peer_id].transport:
                print(self.normal_peers[peer_id].transport)
            del self.normal_peers[peer_id]
            self.normal_peer_num = self.normal_peer_num - 1

    def remove_mobile_peer(self, id):
        if peer_id in self.mobile_peers:
            if self.mobile_peers[peer_id].transport:
                print(self.mobile_peers[peer_id].transport)
            del self.mobile_peers[peer_id]
            self.mobile_peer_num = self.mobile_peer_num - 1

    def select_super_peers(self, count):
        all_peers = self.super_peers.values()
        if len(all_peers) <= count:
            chosen_peers = all_peers
            return chosen_peers
        else:
            chosen_peers = []
            while len(chosen_peers) < count:
                peer = all_peers[random.randint(0, count)]
                if peer not in chosen_peers:
                    chosen_peers.append(peer)

    def select_normal_peers(self, count):
        all_peers = self.normal_peers.values()
        if len(all_peers) <= count:
            chosen_peers = all_peers
            return chosen_peers
        else:
            chosen_peers = []
            while len(chosen_peers) < count:
                peer = all_peers[random.randint(0, count)]
                if peer not in chosen_peers:
                    chosen_peers.append(peer)

    def select_mobile_peers(self, count):
        all_peers = self.mobile_peers.values()
        if len(all_peers) <= count:
            chosen_peers = all_peers
            return chosen_peers
        else:
            chosen_peers = []
            while len(chosen_peers) < count:
                peer = all_peers[random.randint(0, count)]
                if peer not in chosen_peers:
                    chosen_peers.append(peer)
