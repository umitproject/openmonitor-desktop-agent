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
        pass

    def save_to_db(self):
        pass

    def snapshot(self):
        pass

