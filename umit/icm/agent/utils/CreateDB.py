#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
#           Adriano Marques <adriano@umitproject.org>
#           Tianwei liu <liutianweidlut@gmail.com>
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

mod = 93740173714873692520486809225128030132198461438147249362129501889664779512410440220785650833428588898698591424963196756217514115251721698086685512592960422731696162410024157767288910468830028582731342024445624992243984053669314926468760439060317134193339836267660799899385710848833751883032635625332235630111L
exp = 65537L

def pack(val):
    return sqlite3.Binary(cPickle.dumps(val, 2))


def create(conn_str):
    conn = sqlite3.connect(conn_str)
    c = conn.cursor()

    # Create the tables
    c.execute("CREATE TABLE config ("
              "key TEXT primary key not null, "
              "value BLOB not null"
              ")")

    c.execute("CREATE TABLE keys ("
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
              "public_key BLOB, "
              "token TEXT, "
              "geo TEXT, "
              "status TEXT,"
              "network_id INTEGER"
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
              "agent_id TEXT PRIMARY KEY NOT NULL, "
              "username TEXT NOT NULL, "
              "password TEXT NOT NULL, "
              "email TEXT, "
              "ciphered_public_key_hash BLOB NOT NULL, "
              "type INTEGER DEFAULT 2"
              ")")

    #c.execute("CREATE TABLE stats ("
              #"time INTEGER NOT NULL PRIMARY KEY, "
              # report stats
              #"reports_total INTEGER NOT NULL, "
              #"reports_in_queue INTEGER NOT NULL, "
              #"reports_generated INTEGER NOT NULL, "
              #"reports_sent INTEGER NOT NULL, "
              #"reports_sent_to_ag INTEGER NOT NULL, "
              #"reports_sent_to_sa INTEGER NOT NULL, "
              #"reports_sent_to_da INTEGER NOT NULL, "
              #"reports_sent_to_ma INTEGER NOT NULL, "
              #"reports_recved INTEGER NOT NULL, "
              #"reports_recved_from_sa INTEGER NOT NULL, "
              #"reports_recved_from_da INTEGER NOT NULL, "
              #"reports_recved_from_ma INTEGER NOT NULL, "
              # task stats
              #"running_task_num INTEGER NOT NULL, "
              #"task_done INTEGER NOT NULL, "
              #"task_failed INTEGER NOT NULL, "
              #"task_done_by_type BLOB NOT NULL, "
              #"task_failed_by_type BLOB NOT NULL, "
              # connection stats
              #"ag_status TEXT NOT NULL, "
              #"ag_failed_times INTEGER NOT NULL, "
              #"sa_num INTEGER NOT NULL, "
              #"sa_failed_times INTEGER NOT NULL, "
              #"da_num INTEGER NOT NULL, "
              #"da_failed_times INTEGER NOT NULL, "
              #"ma_num INTEGER NOT NULL, "
              #"ma_failed_times INTEGER NOT NULL "
              #")")
    
    c.execute("CREATE TABLE stats" 
              "( key TEXT NOT NULL primary key ,"
              " value TEXT NOT NULL )")
    
    c.execute("CREATE TABLE networks ("
              "id INTEGER NOT NULL PRIMARY KEY,"
              "start_number INTEGER NOT NULL,"
              "end_number INTEGER NOT NULL,"
              "nodes_count INTEGER NOT NULL,"
              "created_at INTEGER NOT NULL,"
              "updated_at INTEGER NOT NULL"
              ")")

    c.execute("CREATE TABLE banlist ("
              "agent_id INTEGER NOT NULL UNIQUE"
              ")")

    c.execute("CREATE TABLE bannets ("
              "id INTEGER NOT NULL PRIMARY KEY,"
              "start_number INTEGER NOT NULL,"
              "end_number INTEGER NOT NULL,"
              "nodes_count INTEGER NOT NULL,"
              "flags INTEGER NOT NULL,"
              "created_at INTEGER NOT NULL,"
              "updated_at INTEGER NOT NULL"
              ")")
    #db table for software update
    c.execute("CREATE TABLE updates ("
              "version TEXT NOT NULL PRIMARY KEY,"
              "news_date TEXT NOT NULL,"
              "software_name TEXT,"
              "description TEXT,"
              "download_url TEXT NOT NULL,"
              "is_update INTEGER NOT NULL,"
              "check_code TEXT"
               ")")
    
    #db for super peer by manual
    c.execute("CREATE TABLE super_peers_manual ("
              "ip TEXT NOT NULL,"
              "port INTEGER NOT NULL,"
              "description TEXT,"
              "constraint pk_super_peers_manual primary key (ip,port))")
    
    
    # Insert pre-defined values

    c.execute("INSERT INTO keys VALUES('aggregator_publickey', ?)",
              (pack((mod, exp)),))

    # Data for test
    c.execute("INSERT INTO peers VALUES(10004, 1, '202.206.64.11', 3128, '', '', "
              "'China', 'UNKNOWN', NULL)")



    conn.commit()
    c.close()
