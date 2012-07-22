#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
#           Adriano Marques <adriano@umitproject.org>
#           Tianwei Liu <liutiawneidlut@gmail.com>
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

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from twisted.internet import reactor
import umit.icm.agent.libcagepeers

FAILURE_INCREASE_COUNT = 2
SUCCESS_REDUCE_COUNT = 1


class PeerEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ID = ''          # string
        self.Type = 0        # integer
        self.IP = ''         # string
        self.Port = 0        # integer
        self.Token = ''      # string
        self.CipheredPublicKey = ''  # bytes
        self.Geo = ''        # string
        self.Status = ''
        self.network_id = 0

        self.transport = None
        self.status = 'Disconnected'

    def __unicode__(self):
        return u"Peer Entry %d (%s - %d) %s:%s - Net ID %s" % \
                        (self.ID,
                         {1:"super peer", 2:"desktop", 3:"mobile"}[self.Type],
                         self.Type, self.IP, self.Port, self.network_id)


#---------------------------------------------------------------------
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
        self.max_speer_num = g_config.getint('network', 'max_speer_num')
        self.max_peer_num = g_config.getint('network', 'max_peer_num')

        self.connected_peer_num = 0
        self.connected_speer_num = 0

    def save_to_db(self):
        g_logger.info("List of super peers is : %s" % self.super_peers.values())
        for peer_entry in self.super_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "('%s', %d, '%s', %d, '%s', '%s', '%s', '%s', %d)" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.CipheredPublicKey,
                 peer_entry.Token, peer_entry.Geo, peer_entry.Status,
                 peer_entry.network_id))
        for peer_entry in self.normal_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "('%s', %d, '%s', %d, '%s', '%s', '%s', '%s', %d)" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.CipheredPublicKey,
                 peer_entry.Token, peer_entry.Geo, peer_entry.Status,
                 peer_entry.network_id))
        for peer_entry in self.mobile_peers.values():
            g_db_helper.execute(
                "insert or replace into peers values" \
                "('%s', %d, '%s', %d, '%s', '%s', '%s', '%s', %d)" % \
                (peer_entry.ID, peer_entry.Type, peer_entry.IP,
                 peer_entry.Port, peer_entry.CipheredPublicKey,
                 peer_entry.Token, peer_entry.Geo, peer_entry.Status,
                 peer_entry.network_id))
        g_db_helper.commit()

    def load_from_db(self):
        # Must change it to a LoopingCall so that the table is constantly updated with peers and superpeers from the aggregator
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
            if peer_entry.Type == 1:
                self.super_peers[peer_entry.ID] = peer_entry
            elif peer_entry.Type == 2:
                self.normal_peers[peer_entry.ID] = peer_entry
            elif peer_entry.Type == 3:
                self.mobile_peers[peer_entry.ID] = peer_entry

    last_gotten = 0
    last_connected = 0

    def scan(self):
        """The scanning procedure works as follows:
        Scanning Peer A, sends check_alive packets in preferred networks in
        specific port ranges with its own info (ID, ip, port, pb key).

        The receiving peer, would receive this packet and check against the
        aggregator or another super peer if that is a tagged agent. If negative,
        the agent can respond with its own details and proceed with connection.
        If positive, which means the agent was tagged for abuse or misconduct
        in the past, it will ignore the request as if it never received it.

        ---

        The preferred networks are defined as follows:
        - A compilation you can get from the Aggregator or another super peer
        - The networks with higher concentration of nodes
        - Your local network
        - The networks within your region
        - The networks in regions nearby
        - The rest of the internet

        API: get_netlist
        Message: GetNetlist
        Response: GetNetlistResponse

        ---

        The logic on refusing to answer scan probes:
        - Match ip against a compilation you can get from the Aggregator or
          another super peer
        - Refuse to connect from networks with higher concentration of tagged
          nodes.

        API: get_banlist (for the compilation)
        Message: GetBanlist
        Response: GetBanlistResponse

        API: get_bannets (for the tagged networks)
        Message: GetBannets
        Response: GetBannetsResponse

        """
        # get the numbers of super peers and normal peers should be connected
        speer_num = 0
        peer_num = 0

        if self.connected_speer_num < self.max_speer_num:
            speer_num = self.max_speer_num - self.connected_speer_num

        if self.connected_peer_num < self.max_peer_num:
            peer_num = self.max_peer_num - self.connected_peer_num

        # get the peer list from aggregator if available
        # Also the peers gotten from aggregator last time could be connected
        if theApp.aggregator.available and \
           (self.last_gotten > 0 and self.last_connected > 0):
            theApp.aggregator.get_super_peer_list(speer_num)
            theApp.aggregator.get_peer_list(peer_num)
            # check alive after peer list gotten
            return

        # get the peer list from super agents
        # pick one super agent
        speer = self.get_random_speer_connected()
        speer.get_super_peer_list(speer_num)
        speer.get_peer_list(peer_num)
        #return

        # get the peer list from other agents (gossip)
        # pick some agents
        peer = self.get_random_peer_connected()
        peer.get_super_peer_list(speer_num)
        peer.get_peer_list(peer_num)
        #return

        # scan local network

        # scan local region

        # scan nearby regions

        # other ways

        #
        #
        #

    def add_peer(self):
        # delegate to aggregator
        g_logger.info("CALLING GET LOCATION")
        theApp.aggregator.getlocation()
        theApp.aggregator.add_peer()
        g_logger.info("END OF ADD PEER")


    def agent_is_banned(self, agent_id):
        return g_db_helper.agent_is_banned(agent_id)

    def network_is_banned(self, ip):
        return g_db_helper.network_is_banned(ip)

    def _super_peer_connected(self, peer_id, ip, port, ciphered_public_key=None,
                             network_id=0):
        if self.agent_is_banned(peer_id) or self.network_is_banned(ip):
            g_logger.info("Super agent %s is banned or is running from "
                          "a banned network %s" % (peer_id, ip))
            if peer_id in self.super_peers:
                self.remove_super_peer(peer_id)
            return False

        if peer_id in self.super_peers and \
           self.super_peers[peer_id].status == 'Connected':
            g_logger.warning("Peer %s already connected." % peer_id)
            return False

        if peer_id in self.super_peers:
            g_logger.debug("Peer id %s already exists in super peer list." %
                           peer_id)
            self.super_peers[peer_id].status = 'Connected'
        else:
            peer_entry = PeerEntry()
            peer_entry.Type = 1
            peer_entry.ID = peer_id
            peer_entry.IP = ip
            peer_entry.Port = port
            peer_entry.CipheredPublicKey = ciphered_public_key
            peer_entry.status = 'Connected'
            peer_entry.network_id = network_id
            self.super_peers[peer_entry.ID] = peer_entry

        self.connected_speer_num = self.connected_speer_num + 1
        return True

    def _super_peer_disconnected(self, peer_id):
        if peer_id not in self.super_peers:
            g_logger.warning("Peer id %s is not in super peer list." % \
                             (peer_id, ip))
            return False
        # will not remove the peer entry from the list
        self.super_peers[peer_id].status = 'Disconnected'
        self.connected_speer_num = self.connected_speer_num - 1
        return True

    def _normal_peer_connected(self, peer_id, ip, port, ciphered_public_key=None,
                              network_id=0):
        if self.agent_is_banned(peer_id) or self.network_is_banned(ip):
            g_logger.info("Desktop agent %s is banned or is running from "
                          "a banned network %s" % (peer_id, ip))
            if peer_id in self.normal_peers:
                self.remove_normal_peer(peer_id)
            return False

        if peer_id in self.normal_peers and \
           self.normal_peers[peer_id].status == 'Connected':
            g_logger.warning("Peer %s already connected." % peer_id)
            return False

        if peer_id in self.normal_peers:
            g_logger.debug("Peer id %s already exists in normal peer list." %
                           peer_id)
            self.normal_peers[peer_id].status = 'Connected'
        else:
            peer_entry = PeerEntry()
            peer_entry.Type = 2
            peer_entry.ID = peer_id
            peer_entry.IP = ip
            peer_entry.Port = port
            peer_entry.CipheredPublicKey = ciphered_public_key
            peer_entry.status = 'Connected'
            peer_entry.network_id = network_id
            self.normal_peers[peer_entry.ID] = peer_entry

        self.connected_peer_num = self.connected_peer_num + 1

    def _normal_peer_disconnected(self, peer_id):
        if peer_id not in self.normal_peers:
            g_logger.warning("Peer id %s is not in normal peer list." % \
                             (peer_id, ip))
            return False
        # will not remove the peer entry from the list
        self.normal_peers[peer_id].status = 'Disconnected'
        self.connected_peer_num = self.connected_peer_num - 1
        return True

    def add_super_peer(self, peer_id, ip, port, token =None ,ciphered_public_key=None,status='Disconnected', network_id=0):
        if self.agent_is_banned(peer_id) or self.network_is_banned(ip):
            g_logger.info("Super Peer agent %s is banned or is running from a banned "
                          "network %s" % (peer_id, ip))
            '''
            if peer_id in self.super_peers:
                self.remove_mobile_peer(peer_id)

            return 
            '''

        if peer_id in self.super_peers:
            g_logger.info("Peer id %s already exists in Super peer list." %
                          peer_id)
        else:
            peer_entry = PeerEntry()
            peer_entry.Type = 1
            peer_entry.ID = peer_id
            peer_entry.IP = ip
            peer_entry.Port = port
            peer_entry.CipheredPublicKey = ciphered_public_key
            peer_entry.status = status
            peer_entry.network_id = network_id
            self.super_peers[peer_entry.ID] = peer_entry
            self.super_peer_num = self.super_peer_num + 1

        self.save_to_db()


    def add_normal_peer(self, peer_id, ip, port, token =None ,ciphered_public_key=None,
                        status='Disconnected', network_id=0):

#        if self.agent_is_banned(peer_id) or self.network_is_banned(ip):
#            g_logger.info("Desktop agent %s is banned or is running from a banned "
#                          "network %s" % (peer_id, ip))
            
#        if peer_id in self.normal_peers:
#            self.remove_normal_peer(peer_id)
#
#        return

        if peer_id in self.normal_peers:
            g_logger.info("Peer id %s already exists in normal peer list." %
                          peer_id)
        else:
            peer_entry = PeerEntry()
            peer_entry.Type = 2
            peer_entry.ID = peer_id
            peer_entry.IP = ip
            peer_entry.Port = port
            peer_entry.Token = token
            peer_entry.CipheredPublicKey = ciphered_public_key
            peer_entry.status = status
            peer_entry.network_id = network_id
            self.normal_peers[peer_entry.ID] = peer_entry
            self.normal_peer_num = self.normal_peer_num + 1


    def add_mobile_peer(self, peer_id, ip, port, ciphered_public_key=None,
                        status='Disconnected', network_id=0):
        if self.agent_is_banned(peer_id) or self.network_is_banned(ip):
            g_logger.info("Mobile agent %s is banned or is running from a banned "
                          "network %s" % (peer_id, ip))

            if peer_id in self.mobile_peers:
                self.remove_mobile_peer(peer_id)

            return

        if peer_id in self.mobile_peers:
            g_logger.info("Peer id %s already exists in mobile peer list." %
                          peer_id)
        else:
            peer_entry = PeerEntry()
            peer_entry.Type = 3
            peer_entry.ID = peer_id
            peer_entry.IP = ip
            peer_entry.Port = port
            peer_entry.CipheredPublicKey = ciphered_public_key
            peer_entry.status = status
            peer_entry.network_id = network_id
            self.mobile_peers[peer_entry.ID] = peer_entry
            self.mobile_peer_num = self.mobile_peer_num + 1

    def remove_super_peer(self, peer_id):
        if peer_id in self.super_peers:
            if peer_id in self.sessions:
                self.sessions[peer_id].transport.loseConnection()
            del self.super_peers[peer_id]
            self.super_peer_num = self.super_peer_num - 1

    def remove_normal_peer(self, peer_id):
        if peer_id in self.normal_peers:
            if peer_id in self.sessions:
                self.sessions[peer_id].transport.loseConnection()
            del self.normal_peers[peer_id]
            self.normal_peer_num = self.normal_peer_num - 1

    def remove_mobile_peer(self, peer_id):
        if peer_id in self.mobile_peers:
            if peer_id in self.sessions:
                self.sessions[peer_id].transport.loseConnection()
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

    def get_random_speer_connected(self):
        id_list = []
        for peer_entry in self.super_peers.values():
            if peer_entry.status == 'Connected' and \
               peer_entry.ID in self.sessions:
                id_list.append(peer_entry.ID)

        if len(id_list) == 0:
            g_logger.warning("No available speer.")
            return None
        else:
            idx = random.randint(0, len(id_list)-1)
            return id_list[idx]

    def get_random_peer_connected(self):
        id_list = []
        for peer_entry in self.normal_peers.values():
            if peer_entry.status == 'Connected' and \
               peer_entry.ID in self.sessions:
                id_list.append(peer_entry.ID)

        if len(id_list) == 0:
            g_logger.warning("No available peer.")
            return None
        else:
            idx = random.randint(0, len(id_list)-1)
            return id_list[idx]

    def connect_all_super_peers(self):
        for peer_id in self.super_peers:
            self.connect_to_peer(peer_id)

    def connect_to_peer(self, peer_id):
        if self.agent_is_banned(peer_id):
            g_logger.info("Agent %s is banned." % peer_id)

        if peer_id == theApp.peer_info.ID:
            g_logger.error("Can't connect to self.")
        if peer_id not in self.sessions:
            peer_entry = None
            if peer_id in self.super_peers:
                peer_entry = self.super_peers[peer_id]
            elif peer_id in self.normal_peers:
                peer_entry = self.normal_peers[peer_id]
            elif peer_id in self.mobile_peers:
                peer_entry = self.mobile_peers[peer_id]
            else:
                g_logger.error("Peer id '%s' doesn't exist in all peer lists." %
                               peer_id)
                return

            if self.network_is_banned(peer_entry.IP):
                g_logger.info("Agent %s is banned in network grounds (%s)." % \
                                 (peer_id, peer_entry.IP))
                return

            reactor.connectTCP(peer_entry.IP, peer_entry.Port,
                               theApp.factory)
            g_logger.debug("Connecting to %s:%d..." %
                           (peer_entry.IP, peer_entry.Port))

    def sync_banlist(self, message):
        for agent_id in message.agent_ids:
            ban = g_db_helper.insert_banned_agent(agent_id)
            g_logger.info("Banned %s: %s" % (agent_id, str(ban)))

    def sync_bannets(self, message):
        for network in message.networks:
            ban = g_db_helper.insert_banned_network(network.start_ip,
                                                    network.end_ip,
                                                    network.nodes_count,
                                                    network.flags)
            g_logger.info("Banned %s: %s" % (network, str(ban)))


    def _connected_to_aggregator(self, data):
        if theApp.aggregator.available:
            if not theApp.peer_info.registered:
                d = theApp.aggregator.register()
                d.addCallback(self._after_registration)

            #elif not theApp.peer_info.login:
            #    #d = theApp.aggregator.login()
            #    #d.addCallback(self._after_login)
            #    theApp.peer_info.login = Truchecke
            #    self._after_login(None)

    def _after_registration(self, data):
        theApp.aggregator.login()

        theApp.task_manager.add_test(1, '*/2 * * * *', {'url':'http://www.baidu.com'}, 3)
        #theApp.task_manager.add_test(2, '*/3 * * * *', {'service':'ftp'})
        #theApp.task_manager.add_test(1, '*/5 * * * *', {'url':'http://www.sina.com'}, 2)

    def _after_login(self, data):
        if theApp.peer_info.login and theApp.use_gui:
            theApp.gtk_main.set_login_status(True)
        #else:
            #theApp.gtk_main.set_login_status(False)

    def _check_aggregator_errback(self, messgae):
        g_logger.critical("Failed to check aggregator: %s" % message)

    """
    Make the desktop agent connect to a certain number of super peers and \
    normal peers, also check the availability of the aggregator
    """

    '''
    Narendran - Each peer will have to maintain a constantly updated list of super peers. Choose the first from it and bootstrap.
    '''
    def maintain(self):
        # check the availability of the aggregator
        if not theApp.aggregator.available:
            d = theApp.aggregator.check_aggregator()
            d.addCallback(self._connected_to_aggregator)
            d.addErrback(self._check_aggregator_errback)

        for peer in self.super_peers.values():
            if peer.status == 'Disconnected':
                self.connect_to_peer(peer.ID)

        '''
        for peer in self.normal_peers.values():
            if peer.status == 'Disconnected':
                self.connect_to_peer(peer.ID)
        '''

        # examine the number of connected super peers
        if self.super_peer_num < self.max_speer_num:
            required_num = self.max_speer_num - self.super_peer_num
            if theApp.aggregator.available:
                g_logger.debug("Requiring %d super peers from the aggregator",
                               required_num)

                '''
                Once the geolocation service is up, pass the country code and  get the super peers belonging to that country alone instead of count
                '''
                #theApp.aggregator.get_super_peer_list(theApp.aggregator.getlocation())
            else:
                for peer in self.super_peers.values():
                    if peer.status == 'Connected' and peer.ID in self.sessions:
                        g_logger.debug("Requiring super peers from "
                                       "super peer %d belonging to %s" % (peer.ID, theApp.peer_info.country_code))
                        self.sessions[peer.ID].get_super_peer_list(theApp.peer_info.country_code)

        g_logger.info("-----------------PEER SYNCUP----------------")
        # Sync peers from libcage with peers table.
        if(theApp.peer_added):
            self.peers = []
            self.peers = theApp.cage_instance.getPeers()
            if(len(self.peers)==0):
                g_logger.info("There are no peers in the cage instance. Wait for few seconds")
            else:
                g_logger.info("Syncing up the peer list with the peers table")
                for i in range(len(self.peers)):
                    g_logger.info("Peer from cage instance is %s" % str(self.peers[i]))
                    peer_arr = self.peers[i].rsplit(",")
                    theApp.peer_manager.add_normal_peer(peer_arr[0],peer_arr[1],int(peer_arr[2]),None,None,"Connected",0);
                    theApp.peer_manager.save_to_db()


        


        '''
        if self.normal_peer_num < self.max_peer_num:
            required_num = self.max_peer_num - self.normal_peer_num
            if theApp.aggregator.available:
                g_logger.debug("Requiring %d peers from the aggregator",
                               required_num)
                theApp.aggregator.get_peer_list(required_num)
            else:
                for peer in self.super_peers.values():
                    if peer.status == 'Connected' and peer.ID in self.sessions:
                        g_logger.debug("Requiring %d peers from "
                                       "super peer %d" % (required_num, peer.ID))
                        self.sessions[peer.ID].get_peer_list(required_num)
        '''


