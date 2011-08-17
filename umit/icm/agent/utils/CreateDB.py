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

import cPickle
import sqlite3


def pack(val):
    return sqlite3.Binary(cPickle.dumps(val, 2))


def create(conn_str):
    conn = sqlite3.connect(conn_str)
    c = conn.cursor()
    
    # Create the tables
    c.execute("CREATE TABLE kvp ("
              "key TEXT primary key not null, "
              "value BLOB not null"
              ")")
    
    c.execute("CREATE TABLE events ("
              "id INTEGER NOT NULL PRIMARY KEY, "
              "test_type TEXT NOT NULL, "
              "event_type TEXT NOT NULL, "
              "time INTEGER NOT NULL, "
              "since_time INTEGER NOT NULL, "
              "locations TEXT NOT NULL, "
              "website_report TEXT, "
              "service_report TEXT"
              ")")
    
    c.execute("CREATE TABLE peers ("
              "id INTEGER NOT NULL PRIMARY KEY, "
              "type INTEGER NOT NULL, "
              "ip TEXT NOT NULL, "
              "port INTEGER NOT NULL, "
              "token TEXT, "
              "public_key BLOB, "
              "geo TEXT"
              ")")
    
    c.execute("CREATE TABLE reports ("
              "report_id TEXT NOT NULL PRIMARY KEY, "
              "test_id INTEGER NOT NULL, "
              "time_gen INTEGER NOT NULL, "
              "content BLOB NOT NULL, "
              "source_id INTEGER NOT NULL, "
              "source_ip TEXT DEFAULT (''), "
              "status TEXT DEFAULT ('')"
              ")")
    
    c.execute("CREATE TABLE unsent_reports ("
              "report_id TEXT NOT NULL, "
              "test_id INTEGER NOT NULL, "
              "time_gen INTEGER NOT NULL, "
              "content BLOB NOT NULL, "
              "source_id INTEGER NOT NULL, "
              "source_ip TEXT DEFAULT (''), "
              "status TEXT DEFAULT ('')"
              ")")
    
    c.execute("CREATE TABLE peer_info ("
              "agent_id INTEGER PRIMARY KEY NOT NULL, "
              "email TEXT, "
              "token TEXT, "
              "public_key BLOB NOT NULL, "
              "private_key BLOB NOT NULL, "
              "ciphered_public_key BLOB NOT NULL, "
              "type INTEGER DEFAULT 2"
              ")")
    
    c.execute("CREATE TABLE stats ("
              "time INTEGER NOT NULL PRIMARY KEY, "
              "super_agent_num INTEGER NOT NULL, "
              "normal_agent_num INTEGER NOT NULL, "
              "mobile_agent_num INTEGER NOT NULL, "
              "reports_sent_to_aggregator INTEGER NOT NULL, "
              "reports_sent_to_super_agent INTEGER NOT NULL, "
              "reports_sent_to_normal_agent INTEGER NOT NULL, "
              "reports_sent_to_mobile_agent INTEGER NOT NULL, "
              "reports_received INTEGER NOT NULL, "
              "tests_done INTEGER NOT NULL"
              ")")
    
    # Insert pre-defined values
    c.execute("INSERT INTO kvp VALUES('aggregator_url', ?)",
              (pack('http://icm-dev.appspot.com/api'),))
    c.execute("INSERT INTO kvp VALUES('selected_tests', ?)",
              (pack(''),))
    
    # Data for test
    c.execute("INSERT INTO peers VALUES(10004, 1, '202.206.64.11', 3128, '', '', "
              "'China')")
    
    
    conn.commit()
    c.close()
