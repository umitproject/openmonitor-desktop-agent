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
import time

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.message import WebsiteReportDetail, ServiceReportDetail
from umit.icm.agent.rpc.MessageFactory import MessageFactory


class EventEntry(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.TestType = ''
        self.EventType = ''
        self.TimeUTC = 0
        self.SinceTimeUTC = 0
        self.Locations = []
        self.WebsiteReport = None
        self.ServiceReport = None

#---------------------------------------------------------------------
class EventManager(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.event_repository = []
        from_time = int(time.time()) - 604800 # load recent events (7 days)
        self.load_events_from_db(from_time)

    def add_event(self, message):
        
        event_entry = EventEntry()
        event_entry.TestType = message.testType
        event_entry.EventType = message.eventType
        event_entry.TimeUTC = message.timeUTC
        event_entry.SinceTimeUTC = message.sinceTimeUTC
        for location in message.locations:
            event_entry.Locations.append((location.longitude, location.latitude))
        if message.HasField('websiteReport'):
            event_entry.WebsiteReport = WebsiteReportDetail()
            event_entry.WebsiteReport.CopyFrom(message.websiteReport)
        if message.HasField('serviceReport'):
            event_entry.ServiceReport = ServiceReportDetail()
            event_entry.ServiceReport.CopyFrom(message.serviceReport)

        self.event_repository.append(event_entry)
        self.save_event_to_db(event_entry)
        g_logger.debug("Add one message into database. Details:(%s,%s)"%(message.testType,message.eventType))

    def load_events_from_db(self, from_time):
        rs = g_db_helper.select("select * from events where time>%d" % from_time)
        for record in rs:
            event_entry = EventEntry()
            event_entry.TestType = record[1]
            event_entry.EventType = record[2]
            event_entry.TimeUTC = record[3]
            event_entry.SinceTimeUTC = record[4]
            event_entry.Locations = []
            for loc in record[5].split(';'):
                event_entry.Locations.append((float(loc.split(',')[0]),
                                              float(loc.split(',')[1])))
            if record[6] != 'None':
                event_entry.WebsiteReport = \
                           MessageFactory.decode(base64.b64decode(record[6]))
            if record[7] != 'None':
                event_entry.ServiceReport = \
                           MessageFactory.decode(base64.b64decode(record[7]))
            if event_entry not in self.event_repository:
                self.event_repository.append(event_entry)
        g_logger.info("Loaded %d events from DB." % len(rs))

    def save_event_to_db(self, event_entry):
        locs = []
        for loc in event_entry.Locations:
            locs.append("%f,%f" % loc)
        loc_str = ';'.join(locs)
        wr_str = None
        if event_entry.WebsiteReport:
            wr_str = base64.b64encode(
                MessageFactory.encode(event_entry.WebsiteReport))
        sr_str = None
        if event_entry.ServiceReport:
            sr_str = base64.b64encode(
                MessageFactory.encode(event_entry.ServiceReport))
        sql_stmt = "insert into events (test_type, event_type, time, "\
                   "since_time, locations, website_report, service_report) "\
                   "values ('%s', '%s', %d, %d, '%s', '%s', '%s')" % \
                   (event_entry.TestType,
                    event_entry.EventType,
                    event_entry.TimeUTC,
                    event_entry.SinceTimeUTC,
                    loc_str, wr_str, sr_str)

        g_db_helper.execute(sql_stmt)
        g_db_helper.commit()
        #g_logger.debug("Save report '%s' to table '%s'." % (report_entry.ID,
                                                            #table_name))


if __name__ == "__main__":
    event_entry = EventEntry()
    event_entry.TestType = 'WEB'
    event_entry.EventType = 'CENSOR'
    event_entry.TimeUTC = int(time.time())
    event_entry.SinceTimeUTC = int(time.time())
    event_entry.Locations.append((10.10, 20.20))
    event_entry.Locations.append((30.30, 40.40))
    event_entry.WebsiteReport = WebsiteReportDetail()
    event_entry.WebsiteReport.websiteURL = 'http://www.qq.com/'
    event_entry.WebsiteReport.statusCode = 0

    from umit.icm.agent.rpc.message import *
    message = Event()
    message.testType = 'SERVICE'
    message.eventType = 'CENSOR'
    import time
    message.timeUTC = int(time.time())
    message.sinceTimeUTC = int(time.time())
    l1 = message.locations.add()
    l1.longitude = 55.55
    l1.latitude = 66.66
    l2 = message.locations.add()
    l2.longitude = 77.77
    l2.latitude = 88.88
    message.serviceReport.serviceName = 'ftp'
    message.serviceReport.statusCode = 0

    em = EventManager()
    em.add_event(message)


