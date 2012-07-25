#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
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

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *

class Statistics(object):
    def __init__(self):
        self.reports_total = 0
        self.reports_in_queue = 0
        self.reports_generated = 0
        self.reports_sent = 0
        self.reports_sent_to_aggregator = 0
        self.reports_sent_to_super_agent = 0
        self.reports_sent_to_normal_agent = 0
        self.reports_sent_to_mobile_agent = 0
        self.reports_received = 0
        self.reports_received_from_aggregator = 0
        self.reports_received_from_super_agent = 0
        self.reports_received_from_normal_agent = 0
        self.reports_received_from_mobile_agent = 0

        self.tasks_current_num = 0
        self.tasks_done = 0
        self.tasks_failed = 0
        self.tasks_done_by_type = {}
        self.tasks_failed_by_type = {}

        self.super_agents_num = 0
        self.normal_agents_num = 0
        self.mobile_agents_num = 0
        self.aggregator_fail_num = 0
        self.super_agents_fail_num = 0
        self.normal_agents_fail_num = 0
        self.mobile_agents_fail_num = 0

    def load_from_db(self):
        """
        """
        self.reports_in_queue = int(g_db_helper.get_status("reports_in_queue")) 
        self.reports_generated = int(g_db_helper.get_status("reports_generated")) 
        self.reports_sent = int(g_db_helper.get_status("reports_sent")) 
        self.reports_sent_to_aggregator = int(g_db_helper.get_status("reports_sent_to_aggregator")) 
        self.reports_sent_to_super_agent = int(g_db_helper.get_status("reports_sent_to_super_agent")) 
        self.reports_sent_to_normal_agent = int(g_db_helper.get_status("reports_sent_to_normal_agent")) 
        self.reports_sent_to_mobile_agent = int(g_db_helper.get_status("reports_sent_to_mobile_agent")) 
        self.reports_received = int(g_db_helper.get_status("reports_received")) 
        self.reports_received_from_aggregator = int(g_db_helper.get_status("reports_received_from_aggregator")) 
        self.reports_received_from_super_agent = int(g_db_helper.get_status("reports_received_from_super_agent")) 
        self.reports_received_from_normal_agent = int(g_db_helper.get_status("reports_received_from_normal_agent")) 
        self.reports_received_from_mobile_agent = int(g_db_helper.get_status("reports_received_from_mobile_agent")) 

        self.tasks_current_num = int(g_db_helper.get_status("tasks_current_num")) 
        self.tasks_done = int(g_db_helper.get_status("tasks_done")) 
        self.tasks_failed = int(g_db_helper.get_status("tasks_failed")) 

        self.super_agents_num = int(g_db_helper.get_status("super_agents_num")) 
        self.normal_agents_num = int(g_db_helper.get_status("normal_agents_num")) 
        self.mobile_agents_num = int(g_db_helper.get_status("mobile_agents_num")) 
        self.aggregator_fail_num = int(g_db_helper.get_status("aggregator_fail_num")) 
        self.super_agents_fail_num = int(g_db_helper.get_status("super_agents_fail_num")) 
        self.normal_agents_fail_num = int(g_db_helper.get_status("normal_agents_fail_num")) 
        self.mobile_agents_fail_num = int(g_db_helper.get_status("mobile_agents_fail_num")) 

        tasks_done_by_type = g_db_helper.get_status("tasks_done_by_type")
        tasks_done_by_type = tasks_done_by_type.split(";")
        for item in tasks_done_by_type:
            key = item.split(":")[0]
            value = item.split(":")[1]
            self.tasks_done_by_type[key] = value
                
        tasks_failed_by_type = g_db_helper.get_status("tasks_failed_by_type")
        tasks_failed_by_type = tasks_failed_by_type.split(";")
        for item in tasks_failed_by_type:
            key = item.split(":")[0]
            value = item.split(":")[1]
            self.tasks_failed_by_type[key] = value

    def save_to_db(self):
        """
        """
        g_db_helper.set_status("reports_total",string(self.reports_total))
        g_db_helper.set_status("reports_in_queue",string(self.reports_in_queue))
        g_db_helper.set_status("reports_generated",string(self.reports_generated))
        g_db_helper.set_status("reports_sent",string(self.reports_sent))
        g_db_helper.set_status("reports_sent_to_aggregator",string(self.reports_sent_to_aggregator))
        g_db_helper.set_status("reports_sent_to_super_agent",string(self.reports_sent_to_super_agent))
        g_db_helper.set_status("reports_sent_to_normal_agent",string(self.reports_sent_to_normal_agent))
        g_db_helper.set_status("reports_sent_to_mobile_agent",string(self.reports_sent_to_mobile_agent))
        g_db_helper.set_status("reports_received",string(self.reports_received))
        g_db_helper.set_status("reports_received_from_aggregator",string(self.reports_received_from_aggregator))
        g_db_helper.set_status("reports_received_from_super_agent",string(self.reports_received_from_super_agent))
        g_db_helper.set_status("reports_received_from_normal_agent",string(self.reports_received_from_normal_agent))
        g_db_helper.set_status("reports_received_from_mobile_agent",string(self.reports_received_from_mobile_agent))
        g_db_helper.set_status("tasks_current_num",string(self.tasks_current_num))
        g_db_helper.set_status("tasks_done",string(self.tasks_done))
        g_db_helper.set_status("tasks_failed",string(self.tasks_failed))
        g_db_helper.set_status("super_agents_num",string(self.super_agents_num))
        g_db_helper.set_status("normal_agents_num",string(self.normal_agents_num))
        g_db_helper.set_status("mobile_agents_num",string(self.mobile_agents_num))
        g_db_helper.set_status("aggregator_fail_num",string(self.aggregator_fail_num))
        g_db_helper.set_status("normal_agents_num",string(self.super_agents_fail_num))
        g_db_helper.set_status("mobile_agents_num",string(self.normal_agents_fail_num))
        g_db_helper.set_status("aggregator_fail_num",string(self.mobile_agents_fail_num))       


        self.tasks_done_by_type = {}
        self.tasks_failed_by_type = {}

        
    def snapshot(self):
        pass

