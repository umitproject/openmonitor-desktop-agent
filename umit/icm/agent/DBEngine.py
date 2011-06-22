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

try:
    execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')
except:
    pass

from collections import deque
import os
import random
import threading
import time

from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *
from umit.icm.agent.utils.DBHelper import DBHelper
from umit.icm.agent.utils.DBKVPHelper import DBKVPHelper

########################################################################
class DBError(Exception):
    "A error occurs during DB operation."

########################################################################
class DBEngine(threading.Thread):
    """"""

    class Query(object):
        ID = 0
        Type = 0
        SQL = None

    class QueryStatus:
        SUCCEEDED = 'QueryStatus.Succeeded'
        FAILED = 'QueryStatus.Failed'

    #----------------------------------------------------------------------
    def __init__(self, name='DBEngineThread'):
        """Constructor"""
        threading.Thread.__init__(self, name=name)
        self._stop_flag = False
        self.random = random
        self.max_queue_size = 1000
        self.query_queue = deque()
        self.waiting_pool = {}

    def run(self):
        self.db_helper = DBHelper('sqlite')
        self.db_helper.connect(os.path.join(DB_DIR, 'storage.db3'))
        self.db_config = DBKVPHelper('config')
        self.db_config.attach(self.db_helper)
        while True:
            try:
                query = self.query_queue.popleft()
                if query.Type == 'SELECT':
                    result = self.db_helper.select(query.SQL)
                    self.waiting_pool[query.ID] = result
                elif query.Type == 'NONSELECT':
                    self.db_helper.execute(query.SQL)
                    self.waiting_pool[query.ID] = self.QueryStatus.SUCCEEDED
                elif query.Type == 'COMMIT':
                    self.db_helper.commit()
                elif query.Type == 'GET_CONFIG':
                    result = self.db_config.read(query.Key, query.Default)
                    self.waiting_pool[query.ID] = result
                elif query.Type == 'SET_CONFIG':
                    self.db_config.write(query.Key, query.Value)
                    self.waiting_pool[query.ID] = self.QueryStatus.SUCCEEDED
                elif query.Type == 'DEL_CONFIG':
                    self.db_config.delete(query.Key)
                    self.waiting_pool[query.ID] = self.QueryStatus.SUCCEEDED
                else:
                    raise TypeError("Unknown Type '%s'", query.Type)
            except IndexError:
                if self._stop_flag:
                    break
                time.sleep(0.01)
            except Exception, e:
                g_logger.error("%s: %s" % (type(e), e))
                self.waiting_pool[query.ID] = self.QueryStatus.FAILED

    def insert_query(self, sql, type_):
        if len(self.query_queue) >= self.max_queue_size:
            g_logger.warning("DBEngine - Query queue exceeds max length.")
            return
        query = self.Query()
        query.ID = str(int(time.time())) + str(random.randint(0, 100))
        query.Type = type_
        query.SQL = sql
        self.query_queue.append(query)
        return query.ID

    def get_result(self, query_id):
        if query_id in self.waiting_pool:
            result = self.waiting_pool[query_id]
            del self.waiting_pool[query_id]
            if result == self.QueryStatus.FAILED:
                raise DBError()
            return result
        return None

    def exec_select(self, sql_select):
        query_id = self.insert_query(sql_select, 'SELECT')
        while query_id not in self.waiting_pool:
            time.sleep(0.01)
        return self.get_result(query_id)

    """ Need commit after exec_nonselect """
    def exec_nonselect(self, sql_nonselect):
        query_id = self.insert_query(sql_nonselect, 'NONSELECT')
        while query_id not in self.waiting_pool:
            time.sleep(0.01)
        self.get_result(query_id)

    def get_config(self, key, default=None):
        if len(self.query_queue) >= self.max_queue_size:
            g_logger.warning("DBEngine - Query queue exceeds max length.")
            return
        query = self.Query()
        query.ID = str(int(time.time())) + str(random.randint(0, 100))
        query.Type = 'GET_CONFIG'
        query.Key = key
        query.Default = default
        self.query_queue.append(query)

        while query.ID not in self.waiting_pool:
            time.sleep(0.01)

        result = self.waiting_pool[query.ID]
        del self.waiting_pool[query.ID]
        if result == self.QueryStatus.FAILED:
            raise DBError()
        return result

    def set_config(self, key, value):
        if len(self.query_queue) >= self.max_queue_size:
            g_logger.warning("DBEngine - Query queue exceeds max length.")
            return
        query = self.Query()
        query.ID = str(int(time.time())) + str(random.randint(0, 100))
        query.Type = 'SET_CONFIG'
        query.Key = key
        query.Value = value
        self.query_queue.append(query)

        while query.ID not in self.waiting_pool:
            time.sleep(0.01)

        result = self.waiting_pool[query.ID]
        del self.waiting_pool[query.ID]
        if result == self.QueryStatus.FAILED:
            raise DBError()

    def del_config(self, key):
        if len(self.query_queue) >= self.max_queue_size:
            g_logger.warning("DBEngine - Query queue exceeds max length.")
            return
        query = self.Query()
        query.ID = str(int(time.time())) + str(random.randint(0, 100))
        query.Type = 'DEL_CONFIG'
        query.Key = key
        self.query_queue.append(query)

        while query.ID not in self.waiting_pool:
            time.sleep(0.01)

        result = self.waiting_pool[query.ID]
        del self.waiting_pool[query.ID]
        if result == self.QueryStatus.FAILED:
            raise DBError()

    def commit(self):
        self.insert_query('', 'COMMIT')

    def stop(self):
        self._stop_flag = True


if __name__ == "__main__":
    db = DBEngine()
    db.start()
    db.exec_nonselect("insert into peers values(10004, 1, '157.222.40.58', "\
                      "19234, 'null', 'abcdef', 'China', 'OK')")
    db.commit()
    #db.set_config('login_saved', True)
    #print(db.get_config('aggregator_url'))
    db.stop()