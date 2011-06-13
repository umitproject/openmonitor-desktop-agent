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

import base64
import cPickle
import os
import sqlite3

from umit.icm.agent.Global import g_logger

########################################################################
class SQLiteHelper(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.conn = None
        self.cur = None
        
    def connect(self, db_path, timeout=3000):
        """Connect to the database"""
        if not os.path.exists(db_path):
            g_logger.error("Cannot find database at '%s'." % db_path)
            return        
        self.conn = sqlite3.connect(db_path, timeout)
        g_logger.debug("Attached to database '%s'." % db_path)
        self.cur = self.conn.cursor()
    
    def use(self, db_name):
        """Do nothing""" 
    
    def select(self, statement, parameters=None):
        """Select statement execution, return a result set"""
        if self.conn is None:
            g_logger.error("There's no connection to database.")
            return
        if parameters is None:
            self.cur.execute(statement)
        else:
            self.cur.execute(statement, parameters)
        result = self.cur.fetchall()
        g_logger.debug("%d rows selected." % len(result))
        return result
    
    def execute(self, statement, parameters=None):
        """Non-select statement execution"""
        if self.conn is None:
            g_logger.error("There's no connection to database.")
            return
        if parameters is None:
            self.cur.execute(statement) 
        else:
            self.cur.execute(statement, parameters) 
        g_logger.debug("%d rows affected." % self.cur.rowcount)
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.cur.close()
        self.conn.close()
        
    def pack(self, val):
        return sqlite3.Binary(cPickle.dumps(val, 2))
    
    def unpack(self, data):
        return cPickle.loads(str(data))
    