#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
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


def create_file_conf(conf_path):
    # create config file
    fp = open(conf_path, 'w')

    from ConfigParser import ConfigParser
    config = ConfigParser()

    config.add_section('application')
    config.set('application', 'auto_login_swittch', False)
    config.set('application', 'auto_update', True)
    config.set('application', 'startup_on_boot', True)
    config.set('application', 'auto_update',True)
    config.set('application', 'auto_update_test_mod', True)

    config.add_section('logging')
    config.set('logging', 'log_level', 'INFO')

    config.add_section('network')
    config.set('network', 'max_speer_num', 10)
    config.set('network', 'max_peer_num', 15)
    config.set('network', 'max_conn_num', 100)
    config.set('network', 'listen_port', 5895)

    config.add_section('web')
    config.set('web', 'listen_port', 8080)

    config.set('network', 'aggregator_url', 'http://alpha.openmonitor.org')
    config.set('application', 'selected_tests', '')

    config.write(fp)
    fp.close()


def create_db_conf(db_path):
    # create configuration in db
    if not os.path.exists(db_path):
        # create the db first
        from umit.icm.agent.utils import CreateDB
        CreateDB.create(db_path)

    from umit.icm.agent.db import DBKVPHelper
    db_kvp_helper = DBKVPHelper('sqlite')
    db_kvp_helper.connect(db_path)

    db_kvp_helper.write('application|auto_login_swittch', False)
    db_kvp_helper.write('application|auto_update', True)
    db_kvp_helper.write('application|startup_on_boot', True)
    db_kvp_helper.write('application|auto_update_test_mod', True)
    db_kvp_helper.write('application|auto_update', False)
    
    db_kvp_helper.write('logging|log_level', 'INFO')

    db_kvp_helper.write('network|max_speer_num', 10)
    db_kvp_helper.write('network|max_peer_num', 15)
    db_kvp_helper.write('network|max_conn_num', 100)
    db_kvp_helper.write('network|listen_port', 5895)

    db_kvp_helper.write('web|listen_port', 8080)

    db_kvp_helper.write('network|aggregator_url',
                        'http://alpha.openmonitor.org')
    db_kvp_helper.write('application|selected_tests', '')

    db_kvp_helper.close()

