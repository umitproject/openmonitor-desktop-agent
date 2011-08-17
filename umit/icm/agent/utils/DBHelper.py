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
"""
DBHelper is a class used to store/retrieve data from a relational SQL database
for the agent.
"""

try:
    execfile("F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py")
except:
    pass

import os

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


if __name__ == "__main__":
    helper = DBHelper('sqlite')
    helper.connect(os.path.join(DB_DIR, 'storage.db3'))
    helper.set_value('aggregator_url', 'http://icm-dev.appspot.com/api')
    print(helper.get_value('aggregator_url'))
