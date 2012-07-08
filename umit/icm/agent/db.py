#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
#           Tianwei Liu <liutianweidlut@gmail.com>
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
Database module
"""

import os
import time

from types import StringTypes

from umit.icm.agent.logger import g_logger
from umit.icm.agent.utils.Network import convert_ip

#---------------------------------------------------------------------
class DBConnection(object):
    """
    DBConnection class provides operations against SQL-like relational
    databases.
    """

    def __init__(self, conn_str):
        """Do nothing"""
        self.conn_str = conn_str
        self.is_open = False

    def open(self):
        """Open a connection to the databse"""
        raise NotImplementedError("This method is currently not supported.")

    def use(self, db_name):
        """Use a databse"""
        raise NotImplementedError("This method is currently not supported.")

    def select(self, sql_str):
        """Execute a select statement and return the result set"""
        raise NotImplementedError("This method is currently not supported.")

    def execute(self, sql_str):
        """Execute a non-select stmt and return the num of lines affected"""
        raise NotImplementedError("This method is currently not supported.")

    def commit(self):
        """Commit the changes to database"""
        raise NotImplementedError("This method is currently not supported.")

    def close(self):
        """Close the connection"""
        raise NotImplementedError("This method is currently not supported.")


#---------------------------------------------------------------------
import base64
import cPickle
import sqlite3

class SQLiteConnection(DBConnection):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, db_path):
        """Constructor"""
        self.db_path = db_path
        self.conn = None
        self.cur = None

    def open(self, timeout=3000):
        """Connect to the database"""
        if not os.path.exists(self.db_path):
            raise IOError("Cannot find database at '%s'." % self.db_path)
        self.conn = sqlite3.connect(self.db_path, timeout)
        if not self.conn:
            raise IOError("Unable to open database '%s'." % self.db_path)
        g_logger.debug("Database connected '%s'." % self.db_path)
        self.is_open = True
        self.cur = self.conn.cursor()

    def use(self, db_name):
        """Do nothing"""

    def select(self, statement, parameters=None):
        """Select statement execution, return a result set"""
        if self.conn is None:
            raise Exception("There's no connection to database.")
        if parameters is None:
            self.cur.execute(statement)
        else:
            self.cur.execute(statement, parameters)
        result = self.cur.fetchall()

        # if only one column is selected, need to remove the empty elements
        # in the second place
        if result and len(result[0]) == 1:
            result = [ row[0] for row in result ]

        #g_logger.debug("%d rows selected." % len(result))
        return result

    def execute(self, statement, parameters=None):
        """Non-select statement execution"""
        if self.conn is None:
            raise Exception("There's no connection to database.")
        if parameters is None:
            self.cur.execute(statement)
        else:
            self.cur.execute(statement, parameters)
        #g_logger.debug("%d rows affected." % self.cur.rowcount)
        return self.cur.rowcount

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
        self.is_open = False

    def pack(self, val):
        return sqlite3.Binary(cPickle.dumps(val, 2))

    def unpack(self, data):
        return cPickle.loads(str(data))

    def list_tables(self):
        return self.select("select name from sqlite_master where type='table' "
                           "order by name;")

#---------------------------------------------------------------------
class DBHelper(object):
    """
    A class with many useful methods for accessing DB
    """
    connection_classes = { 'sqlite': SQLiteConnection }

    #----------------------------------------------------------------------
    def __init__(self, db_type):
        """Constructor"""
        if db_type not in self.connection_classes:
            raise Exception("'%s' is not a valid db type." % db_type)
        self.db_type = db_type

    def connect(self, *args, **kwargs):
        """Connect to the database"""
        conn_str = args[0]
        self.db_conn = self.connection_classes[self.db_type](conn_str)
        self.db_conn.open(*args[1:], **kwargs)

    def attach(self, db_conn):
        """Attach to a existing database connection"""
        if not isinstance(db_conn, DBConnection):
            raise TypeError("%s is not a valid connection instance." % db_conn)
        if not db_conn.is_open:
            db_conn.open()
        self.db_conn = db_conn

    def close(self):
        """Cloes the connection"""
        if self.db_conn.is_open:
            self.db_conn.close()

    def pack(self, val):
        return self.db_conn.pack(val)

    def unpack(self, data):
        return self.db_conn.unpack(data)

    def get_value(self, table_name, key, default=None):
        result = self.db_conn.select(
            "select * from " + table_name + " where key=?", (key, ))
        try:
            return self.unpack(result[0][1])
        except:
            g_logger.warning("No value found for key '%s' in db kvp." % key)
            return default

    def set_value(self, table_name, key, value):
        self.db_conn.execute(
            "insert or replace into " + table_name + " values(?, ?)",
            (key, self.pack(value)))
        self.db_conn.commit()

    def del_value(self, table_name, key):
        self.db_conn.execute(
            "delete from " + table_name + " where key=?", (key, ))
        self.db_conn.commit()

    def select(self, statement, parameters=None):
        return self.db_conn.select(statement, parameters)

    def execute(self, statement, parameters=None):
        return self.db_conn.execute(statement, parameters)

    def commit(self):
        self.db_conn.commit()

    def insert_network(self, start_number, end_number, nodes_count):
        network = self.get_network(start_number, end_number)
        if network:
            g_logger.critical("Exists! Returning %s" % network)
            return network[0][0]

        self.db_conn.execute("INSERT INTO networks ("
                             "start_number, end_number, "
                             "nodes_count, created_at, updated_at) "
                             "values (%d, %d, %d, %d, %d)" % (start_number,
                                                              end_number,
                                                              nodes_count,
                                                              int(time.time()),
                                                              int(time.time())))
        self.db_conn.commit()

        network = self.get_network(start_number, end_number)
        return network[0][0]

    def get_network(self, start_number, end_number):
        return self.db_conn.select("SELECT * FROM networks WHERE "
                                   "start_number <= %d AND end_number >= %d" % \
                                   (start_number, end_number))

    def insert_banned_agent(self, agent_id):
        agent = self.get_peer(agent_id)
        if agent:
            self.remove_peer(agent_id)

        agent = self.get_banned_agent(agent_id)
        if agent:
            return agent

        insert = self.db_conn.execute("INSERT INTO banlist VALUES ('%s')" % \
                                      agent_id)
        self.db_conn.commit()

        return insert

    def get_peer(self, agent_id):
        return self.select("SELECT * FROM peers WHERE id = '%s'" % agent_id)

    def remove_peer(self, agent_id):
        return self.execute("DELETE FROM peers WHERE id = '%s'" % agent_id)

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
                         "('%s', '%s', '%s', %d, %d, %d)" % \
                            (start_ip, end_ip, nodes_count, flag,
                             int(time.time()), int(time.time())))

        self.db_conn.commit()

    def get_banned_network(self, start_ip, end_ip):
        if type(start_ip) in StringTypes:
            start_ip = convert_ip(start_ip)

        if type(end_ip) in StringTypes:
            end_ip = convert_ip(end_ip)

        return self.db_conn.select("SELECT * FROM bannets WHERE "
                                   "start_number <= %d AND end_number >= %d" % \
                                   (start_ip, end_ip))

    def get_banned_agent(self, agent_id):
        return self.db_conn.select("SELECT * FROM banlist WHERE "
                                   "agent_id = '%s'" % agent_id)

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

    def get_aggregator_publickey(self):
        return self.get_value('keys', 'aggregator_publickey')

    def get_self_publickey(self):
        return self.get_value('keys', 'self_publickey')

    def get_self_privatekey(self):
        return self.get_value('keys', 'self_privatekey')

    def set_self_publickey(self, publickey):
        self.set_value('keys', 'self_publickey', publickey)

    def set_self_privatekey(self, privatekey):
        self.set_value('keys', 'self_privatekey', privatekey)

    def get_aggregator_aes_key(self):
        return self.get_value('keys', 'aggregator_aes_key')

    #####################################################
    #Methods for Dashboard Window(Timeline or QueryFrame)
    def get_task_sets(self,task_type = None):
        """
        Tasks (All, done, wait)for Dashboard Window
        """
        from umit.icm.agent.gui.dashboard.DashboardListBase import TASK_ALL,TASK_SUCCESSED,TASK_FAILED
        from umit.icm.agent.test import TASK_STATUS_DONE,TASK_STATUS_FAILED
        if task_type == TASK_ALL:
            return self.db_conn.select("SELECT * from tasks")
        elif task_type == TASK_SUCCESSED:
            return self.db_conn.select("SELECT * from tasks where done_status = '%s' "%(TASK_STATUS_DONE))
        elif task_type == TASK_FAILED:
            return self.db_conn.select("SELECT * from tasks where done_status = '%s' "%(TASK_STATUS_FAILED))
        else:
            g_logger.error("Didn't input any legal task type for query :%s"%(task_type))
            return None
    
    def get_report_sets(self,report_type = None):
        """
        Reports for Dashboar Window (sent, unsent, maybe received)
        """
        from umit.icm.agent.gui.dashboard.DashboardListBase import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED
        if report_type == REPORT:
            return None
        elif report_type == REPORT_SENT:
            return self.db_conn.select("SELECT * from reports")
        elif report_type == REPORT_UNSENT:
            return self.db_conn.select("SELECT * from unsent_reports")
        elif report_type == REPORT_RECEIVED:
            return self.db_conn.select("SELECT * from received_reports")
        else:
            g_logger.error("Didn't input any legal report type for query :%s"%(report_type))
            return None
        
    def get_test_sets(self,test_type = None):
        """
        Test sets for Dashboard Window(successful or failed)
        """
        from umit.icm.agent.gui.dashboard.DashboardListBase import CAPA_THROTTLED,CAPACITY,CAPA_SERVICE
        from umit.icm.agent.test import TASK_STATUS_DONE,TASK_STATUS_FAILED
        if test_type == CAPA_THROTTLED:
            return self.db_conn.select("SELECT \
                                    sequence,test_id,website_url,test_type,done_status,done_result,execute_time \
                                      from tasks where test_type = 'WEB' ")
        elif test_type == CAPACITY:
            return None
        elif test_type == CAPA_SERVICE:
            return self.db_conn.select("SELECT \
                                    sequence,test_id,service_name,service_port,service_ip,test_type,done_status,done_result,execute_time \
                                      from tasks where test_type = 'Service' ")
        else:
            g_logger.error("Didn't input any legal test sets type for query :%s"%(test_type))
            return None   
          
    def timerange_changes_count_generic(self,start,end,choice_tab):
        """
        This method helps datagrab get the basic data from database 
        """   
        from umit.icm.agent.gui.dashboard.DashboardListBase import CAPA_THROTTLED,CAPACITY,CAPA_SERVICE
        from umit.icm.agent.gui.dashboard.DashboardListBase import REPORT,REPORT_SENT,REPORT_UNSENT,REPORT_RECEIVED
        
        g_logger.debug("Timeline Query:start:%s, end:%s, tab:%s"%(start,end,choice_tab))
        
        if  choice_tab ==  REPORT_SENT:
            return len(self.db_conn.select("SELECT * from reports "
                            "WHERE time_gen >= ? AND time_gen < ? "
                            "ORDER BY time_gen DESC", (start,end)))
        elif choice_tab ==  REPORT_UNSENT:
            return len(self.db_conn.select("SELECT * from unsent_reports "
                            "WHERE time_gen >= ? AND time_gen < ? "
                            "ORDER BY time_gen DESC", (start,end)))
        elif choice_tab ==  REPORT_RECEIVED:
            return 0
        elif choice_tab ==  CAPA_THROTTLED:
            return len(self.db_conn.select("SELECT * from tasks WHERE execute_time >= ? AND execute_time < ? AND test_type = 'WEB' ",(start,end)))
        elif choice_tab ==  CAPA_SERVICE:
            return len(self.db_conn.select("SELECT * from tasks WHERE execute_time >= ? AND execute_time < ? AND test_type = 'Service' ",(start,end)))
        else:
            return 0       

#---------------------------------------------------------------------
class DBKVPHelper(object):
    """
    DBKVPHelper is used to implement KVP operations in a database.
    """
    connection_classes = { 'sqlite': SQLiteConnection }

    #----------------------------------------------------------------------
    def __init__(self, db_type):
        """Constructor"""
        if db_type not in self.connection_classes:
            raise Exception("'%s' is not a valid db type." % db_type)
        self.db_type = db_type
        # set the table to be used, default is 'config'
        self.use_table('config')

    def connect(self, *args, **kwargs):
        """Connect to the database"""
        conn_str = args[0]
        self.db_conn = self.connection_classes[self.db_type](conn_str)
        self.db_conn.open(*args[1:], **kwargs)

    def attach(self, db_conn):
        """Attach to a existing database connection"""
        if not isinstance(db_conn, DBConnection):
            raise TypeError("%s is not a valid connection instance." % db_conn)
        if not db_conn.is_open:
            db_conn.open()
        self.db_conn = db_conn

    def close(self):
        """Cloes the connection"""
        if self.db_conn.is_open:
            self.db_conn.close()

    def use_table(self, table_name):
        self.table_name = table_name
        self.sql_select = "select * from " + table_name + " where key=?"
        self.sql_update = "update " + table_name + " set value=? where key=?"
        self.sql_insert = "insert into " + table_name + " values(?, ?)"
        self.sql_delete = "delete from " + table_name + " where key=?"

    def read(self, key, default=None):
        if not self.db_conn:
            raise Exception('No connection to database.')
        result = self.db_conn.select(self.sql_select, (key,))
        try:
            return self.unpack(result[0][1])
        except:
            g_logger.warning("No value found for key '%s' in db config." % key)
            return default

    def write(self, key, value):
        if not self.db_conn:
            raise Exception('No connection to database.')
        self.db_conn.execute(self.sql_delete, (key,))
        self.db_conn.execute(self.sql_insert, (key, self.pack(value)))
        self.db_conn.commit()

    def delete(self, key):
        if not self.db_conn:
            raise Exception('No connection to database.')
        self.db_conn.execute(self.sql_delete, (key,))
        self.db_conn.commit()

    def pack(self, val):
        return self.db_conn.pack(val)

    def unpack(self, data):
        return self.db_conn.unpack(data)


if __name__ == "__main__":
    from umit.icm.agent.BasePaths import *
    #conn = SQLiteConnection(os.path.join(DB_DIR, 'storage.db3'))
    #conn.open()
    #print(conn.list_tables())
    #print(conn.select("select key,value from kvp"))
    #print(conn.execute("insert into kvp values('aaa', 'bbb')"))
    #print(conn.select("select key,value from kvp"))
    #print(conn.execute("delete from kvp where key='aaa' and value='bbb'"))
    #print(conn.select("select key,value from kvp"))
    #conn.close()
    #helper = DBHelper('sqlite')
    #helper.connect(os.path.join(DB_DIR, 'storage.db3'))
    #print(helper.get_banned_network(0, 100))

    kvp_helper = DBKVPHelper('sqlite')
    kvp_helper.use_table('kvp')
    kvp_helper.connect(os.path.join(DB_DIR, 'storage.db3'))
    print(kvp_helper.read('aggregator_url'))

