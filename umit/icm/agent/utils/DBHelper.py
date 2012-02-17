#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
#           Adriano Marques <adriano@umitproject.org>
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
"""
DBHelper is a class used to store/retrieve data from a relational SQL database
for the agent.
"""

import os
import time

from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import g_logger
from umit.icm.agent.utils.SQLiteHelper import SQLiteHelper

########################################################################
class DBHelper(object):
    """"""
    db_types = { 'sqlite': SQLiteHelper }
    db_helper = None

    #----------------------------------------------------------------------
    def __init__(self, db_type):
        """Constructor"""
        try:
            self.db_helper = self.db_types[db_type]()
        except KeyError:
            g_logger.error("'%s' is not a valid db type." % db_type)
        
        self.db_type = db_type

    def connect(self, conn_str):
        """Connect to the database"""
        if self.db_type == "sqlite":
            if not os.path.exists(conn_str):
                from umit.icm.agent.utils import CreateDB
                CreateDB.create(conn_str)
            self.db_helper.connect(conn_str)

    def use(self, db_name):
        """Set a database into use"""
        self.db_helper.use(db_name)

    def select(self, statement, parameters=None):
        """Select statement execution, return a result set"""
        return self.db_helper.select(statement, parameters)

    def execute(self, statement, parameters=None):
        """Non-select statement execution"""
        self.db_helper.execute(statement, parameters)

    def commit(self):
        self.db_helper.commit()

    def close(self):
        self.db_helper.close()

    def pack(self, val):
        return self.db_helper.pack(val)

    def unpack(self, data):
        return self.db_helper.unpack(data)

    def get_value(self, key, default=None):
        result = self.db_helper.select(
            "select * from kvp where key=?", (key,))
        try:
            return self.unpack(result[0][1])
        except:
            g_logger.warning("No value found for key '%s' in db kvp." % key)
            return default

    def set_value(self, key, value):
        self.db_helper.execute(
            "insert or replace into kvp values(?, ?)",
            (key, self.pack(value)))
        self.commit()

    def del_value(self, key):
        self.db_helper.execute(
            "delete from kvp where key=?", (key,))
        self.commit()
    
    def insert_network(self, start_number, end_number, nodes_count):
        network = self.get_network(start_number, end_number)
        if network:
            g_logger.critical("Exists! Returning %s" % network)
            return network[0][0]
        
        self.execute("INSERT INTO networks ("
                     "start_number, end_number, "
                     "nodes_count, created_at, updated_at) "
                     "values (%d, %d, %d, %d, %d)" % (start_number,
                                                      end_number,
                                                      nodes_count,
                                                      int(time.time()),
                                                      int(time.time())))
        self.commit()
        
        network = self.get_network(start_number, end_number)
        return network[0][0]
    
    def get_network(self, start_number, end_number):
        return self.select("SELECT * FROM networks WHERE "
                           "start_number <= %d AND end_number >= %d" % \
                              (start_number, end_number))
        
    def insert_banned_agent(self, agent_id):
        agent = self.get_peer(agent_id)
        if agent:
            self.remove_peer(agent_id)
        
        agent = self.get_banned_agent(agent_id)
        if agent:
            return agent
        
        insert = self.execute("INSERT INTO banlist VALUES (%d)" % agent_id)
        self.commit()
        
        return insert
    
    def get_peer(self, agent_id):
        return self.select("SELECT * FROM peers WHERE id = %d" % agent_id)
    
    def remove_peer(self, agent_id):
        return self.execute("DELETE FROM peers WHERE id = %d" % agent_id)
    
    def insert_banned_network(self, start_ip, end_ip, nodes_count, flag):
        bannet = self.get_banned_network(start_ip, end_ip)
        if bannet:
            # Update node count and flags
            self.execute("UPDATE bannets SET start_number=%d, "
                         "end_number=%d, nodes_count=%d, "
                         "flags=%d, updated_at=%d WHERE " 
                         "id=%d" % (start_ip, end_ip, nodes_count,
                                    flag, int(time.time()), bannet[0][0]))
        else:
            # Insert into db
            self.execute("INSERT INTO bannets (start_number, end_number, "
                         "nodes_count, flags, created_at, updated_at) VALUES "
                         "(%s, %s, %s, %d, %d, %d)" % \
                            (start_ip, end_ip, nodes_count, flag,
                             int(time.time()), int(time.time())))
            
        self.commit()
    
    def get_banned_network(self, start_ip, end_ip):
        return self.select("SELECT * FROM bannets WHERE "
                           "start_number <= %s AND end_number >= %s" % \
                           (start_ip, end_ip))
    
    def get_banned_agent(self, agent_id):
        return self.select("SELECT * FROM banlist WHERE "
                           "agent_id = %d" % agent_id)

    def agent_is_banned(self, agent_id):
        agent = self.get_banned_agent(agent_id)
        if agent:
            return True
        return False
    
    def network_is_banned(self, ip):
        network = self.get_banned_network(ip, ip)
        if network:
            return True
        return False

if __name__ == "__main__":
    helper = DBHelper('sqlite')
    helper.connect(os.path.join(DB_DIR, 'storage.db3'))
    helper.set_value('aggregator_url', 'http://alpha.openmonitor.org/api')
    print(helper.get_value('aggregator_url'))
