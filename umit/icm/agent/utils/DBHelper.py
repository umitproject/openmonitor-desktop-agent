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
execfile('F:\\workspace\\PyWork\\icm-agent\\umit\\icm\\agent\\UmitImporter.py')

import os

from umit.icm.agent.Basic import DB_DIR
from umit.icm.agent.Logging import log
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
            log.error("'%s' is not a valid db type." % db_type)
        
    def connect(self, conn_str):
        """Connect to the database"""
        self.db_helper.connect(conn_str)
    
    def use(self, db_name):
        """Set a database into use"""
        self.db_helper.use(db_name)
    
    def select(self, statement):
        """Select statement execution, return a result set"""
        return self.db_helper.select(statement)
    
    def insert(self):
        self.db_helper.insert()
        pass
    
    def update(self):
        self.db_helper.insert()
        pass
    
    def delete(self):
        self.db_helper.delete()
        pass

    def execute(self, statement):
        """Non-select statement execution"""
        self.db_helper.execute(statement)
    
if __name__ == "__main__":
    helper = DBHelper('sqlite')
    helper.connect(os.path.join(DB_DIR, 'World.db3'))
    helper.use('main')
    print(helper.select('select * from City'))
    