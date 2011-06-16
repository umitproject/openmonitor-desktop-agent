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

from umit.icm.agent.Global import *
from umit.icm.agent.utils.DBHelper import DBHelper

########################################################################
class DBKVPHelper(DBHelper):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, table_name, db_file_name=None):
        """Constructor"""
        if db_file_name is not None:            
            self.db_helper = DBHelper('sqlite')
            self.db_helper.connect(db_file_name)
            
        self.table_name = table_name            
        self.sql_select = "select * from " + table_name + " where key=?"
        self.sql_update = "update " + table_name + " set value=? where key=?"
        self.sql_insert = "insert into " + table_name + " values(?, ?)"
        self.sql_delete = "delete from " + table_name + " where key=?"
        
    def attach(self, db_helper):
        self.db_helper = db_helper        
        
    def read(self, key, default=None):
        if self.db_helper is None:
            raise Exception('db_helper is None.')
        result = self.db_helper.select(self.sql_select, (key,))        
        try:
            return self.unpack(result[0][1])
        except:
            g_logger.warning("No value found for key '%s' in db config." % key)            
            return default
        
    def write(self, key, value):
        if self.db_helper is None:
            raise Exception('db_helper is None.')
        self.db_helper.execute(self.sql_delete, (key,))
        self.db_helper.execute(self.sql_insert, (key, self.pack(value)))
        self.commit()
        
    def delete(self, key):
        if self.db_helper is None:
            raise Exception('db_helper is None.')
        self.db_helper.execute(self.sql_delete, (key,))
        self.commit()
    
    