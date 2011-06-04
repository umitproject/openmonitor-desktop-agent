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

import os
import sqlite3

from umit.icm.agent.Logging import log

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
            log.error("Cannot find database at '%s'." % db_path)
            return        
        self.conn = sqlite3.connect(db_path, timeout)
        log.debug("Attached to database '%s'." % db_path)
        self.cur = self.conn.cursor()
    
    def use(self, db_name):
        """Do nothing""" 
    
    def select(self, statement):
        """Select statement execution, return a result set"""
        if self.conn is None:
            log.error("There's no connection to database.")
            return        
        self.cur.execute(statement)
        result = self.cur.fetchall()
        log.debug("%d rows selected." % len(result))
        return result
    
    def execute(self):
        """Non-select statement execution"""
        if self.conn is None:
            log.error("There's no connection to database.")
            return   
        self.cur.execute(statement) 
    
    