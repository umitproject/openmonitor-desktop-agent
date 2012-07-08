# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author:  Tianwei Liu <liutianweidlut@gmail.com> 
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import datetime

from umit.icm.agent.gui.dashboard.timeline.Calendar import mdays
from umit.icm.agent.gui.dashboard.timeline.Calendar import isleap

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.logger import g_logger

from umit.icm.agent.gui.dashboard.DashboardListBase import  *


DATA_GRAB_MODES = {
    "yearly_sum": "changes_in_year",
    "monthly_sum": "changes_in_month",
    "daily_sum": "changes_in_day",
    "hourly_sum": "changes_in_hour",
    "category": "changes_by_category_in_range"
    }

class DataGrabber(object):
    """
    Grab data from Reports and Tasks in Database, for a time
    range and format it to be used in Timeline.
    
    The timestamp format is : 2013-01-01 00:00:00 
    
    """

    def __init__(self, calendar):
        """
        """
        self.calendar = calendar

    def standard_sum_filter(self):
        """
        Standard filter to use when we are grabbing data in Changes Sum kind.
        """
        return {0: (True, 'changes_sum')}
    
    def changes_by_category_in_range(self, args,choice_tab=None):
        """
        Generic function for changes_anything 
        (choice_tab can provide report, task tab choice)
        (This method also received the range )
        """
        print "New:",args,choice_tab
        
        if len(args) == 1: # yearly
            return self.changes_in_year(args[0], choice_tab)
        elif len(args) == 2: # monthly
            return self.changes_in_month(args[0], args[1], choice_tab)
        elif len(args) == 3: # daily
            return self.changes_in_day(args[0], args[1], args[2], choice_tab)
        elif len(args) == 4: # hourly
            return self.changes_in_hour(args[0], args[1], args[2], args[3],choice_tab)
        else:
            g_logger.error("Invalid number of parameters specified")

    def timerange_changes_count_generic(self,start,end,choice_tab):
        """
        Selects what method to use to grab changes count.
        """
        
        #start and end should always 
        if not start or not end:
            g_logger.error("You should specify range start and range end")
            return
        
        #check choice_tab
        if not choice_tab:
            g_logger.error("You should specify choice_tab")
            return
        
        #Call DB 
        return g_db_helper.timerange_changes_count_generic(start,end,choice_tab)

    def changes_in_year(self, year, choice_tab=None):
        """
        Gets changes per "week" in an entire year.
        """
        if isleap(year):
            mdays[2] = 29
        else:
            mdays[2] = 28

        # get last amount of events in past year, or, better:
        # amount of events that occuried in (year - 1) at December, from
        # numberOfDaysInDecember / 2 + (numberOfDaysInDecember / 4) till
        # final of month.

        if year == self.calendar.year_range[0]:
            start_value = 0

        else:
            half = mdays[12] / 2
            quarter = half / 2
            start = datetime.datetime(year - 1, 12, quarter + half)
            end = datetime.datetime(year, 1, 1)

            start_value = self.timerange_changes_count_generic(start,end,choice_tab)

        # get events for year
        year_events = { }

        for m in range(12):
            half = (mdays[m + 1] / 2) + 1
            quarter = (half / 2)

            # months with 31 or 30 days:
            # half = (31/2) + 1 = 16
            # quarter = 8
            # will grab 1 -> 8, 8 -> 16, 16 -> 24, 24 -> end month
            # month with 28 or 29 days:
            # half = (29/2) + 1 = 15
            # quarter = 7
            # will grab 1 -> 7, 7 -> 15, 15 -> 22, 22 -> end month

            days = (1, quarter, half, half + quarter, 1)

            mcount = [ ]

            for i in range(len(days) - 1):
                start = datetime.datetime(year, m + 1, days[i])

                if i == len(days) - 2:
                    dyear = year
                    dmonth = m + 2
                    if m == 11:
                        dyear += 1
                        dmonth = 1

                    end = datetime.datetime(dyear, dmonth, days[i + 1])
                else:
                    end = datetime.datetime(year, m + 1, days[i + 1])

                count = self.timerange_changes_count_generic(start,end,choice_tab)

                mcount.append([count, ])

            year_events[m] = mcount

        
        g_logger.debug("Year Events: %d, %s"%(start_value,year_events))       
        return self.standard_sum_filter(), (start_value, ), year_events


    def changes_in_month(self, year, month, choice_tab=None):
        """
        Get changes in a month.
        """
        month_events = { }

        if isleap(year) and month == 2: # month range from 1 to 12
            mdays[2] = 29
        else:
            mdays[2] = 28

        # get last amount of events in past month, or, better:
        # amount of events that occuried in (month - 1) at last day, from
        # 12 PM to 23:59 PM
        self.calendar.dryrun = True
        self.calendar.dec_date(1) # 1 indicates it is a month decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value

        month_range = self.calendar.get_monthrange(prev_year, prev_month)[1]
        start = datetime.datetime(prev_year, prev_month, month_range, 12)
        end = datetime.datetime(year, month, 1)

        start_value = self.timerange_changes_count_generic(start,end,choice_tab)

        for day in range(mdays[month]):
            day_count = [ ]

            # for each day, grab data for 0 AM .. 11:59 AM, 12 PM .. 23:59 PM
            start = datetime.datetime(year, month, day + 1)
            end = datetime.datetime(year, month, day + 1, 12)

            count1 = self.timerange_changes_count_generic(start,end,choice_tab)

            start = datetime.datetime(year, month, day + 1, 12)

            dyear = year
            dmonth = month
            dday = day

            if day == mdays[month] - 1:
                self.calendar.dryrun = True
                self.calendar.inc_date(1)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                dday = 1
                for key, value in next_date.items():
                    if key == "year":
                        dyear = value
                    elif key == "month":
                        dmonth = value

            else:
                dday += 2

            end = datetime.datetime(dyear, dmonth, dday)

            count2 = self.timerange_changes_count_generic(start,end,choice_tab)

            day_count.append([count1, ])
            day_count.append([count2, ])
            month_events[day] = day_count

        g_logger.debug("Month Events: %d, %s"%(start_value,month_events)) 
        return self.standard_sum_filter(), (start_value, ), month_events


    def changes_in_day(self, year, month, day, choice_tab=None):
        """
        Get changes in a day.
        """
        day_events = { }

        # get last amount of events in past day, or, better:
        # amount of events that occuried in (day - 1) at last hour, from
        # 23:30 to current date 0 hour, 0 minute, 0 second
        self.calendar.dryrun = True
        self.calendar.dec_date(2) # 2 indicates it is a day decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month
        prev_day = day - 1

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value
            elif key == "day":
                prev_day = value

        start = datetime.datetime(prev_year, prev_month, prev_day, 23, 30)
        end = datetime.datetime(year, month, day)

        start_value = self.timerange_changes_count_generic(start,end,choice_tab)

        # hour by hour
        for hour in range(24):
            hour_count = [ ]

            # first half hour
            start = datetime.datetime(year, month, day, hour)
            end = datetime.datetime(year, month, day, hour, 30)

            count1 = self.timerange_changes_count_generic(start,end,choice_tab)

            # other half
            start = datetime.datetime(year, month, day, hour, 30)

            if hour == 23:
                next_year = year
                next_month = month
                next_day = day

                self.calendar.dryrun = True
                self.calendar.inc_date(2)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                for key, value in next_date.items():
                    if key == "year":
                        next_year = value
                    elif key == "month":
                        next_month = value
                    elif key == "day":
                        next_day = value

                end = datetime.datetime(next_year, next_month, next_day, 0)

            else:
                end = datetime.datetime(year, month, day, hour + 1)

            count2 = self.timerange_changes_count_generic(start,end,choice_tab)

            hour_count.append([count1])
            hour_count.append([count2])

            day_events[hour] = hour_count

        g_logger.debug("Day Events: %d, %s"%(start_value,day_events)) 
        return self.standard_sum_filter(), (start_value, ), day_events


    def changes_in_hour(self, year, month, day, hour, choice_tab=None):
        """
        Get changes in a especific hour.
        """
        hour_events = { }

        # get last amount of events in past hour, or, better:
        # amount of events that occuried in (hour - 1) at last minute
        self.calendar.dryrun = True
        self.calendar.dec_date(3) # 3 indicates it is an hour decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month
        prev_day = day
        prev_hour = hour - 1

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value
            elif key == "day":
                prev_day = value
                prev_hour = 23

        start = datetime.datetime(prev_year, prev_month, prev_day, prev_hour,59)
        end = datetime.datetime(year, month, day, hour, 0)

        start_value = self.timerange_changes_count_generic(start,end,choice_tab)

        # minute by minute
        for minute in range(60):
            start = datetime.datetime(year, month, day, hour, minute)

            if minute == 59:
                next_year = year
                next_month = month
                next_day = day
                next_hour = hour + 1

                self.calendar.dryrun = True
                self.calendar.inc_date(3)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                for key, value in next_date.items():
                    if key == "year":
                        next_year = value
                    elif key == "month":
                        next_month = value
                    elif key == "day":
                        next_day = value
                        next_hour = 0

                end = datetime.datetime(next_year, next_month, next_day,next_hour)
            else:
                end = datetime.datetime(year, month, day, hour, minute + 1)

            count = self.timerange_changes_count_generic(start, end,choice_tab)

            hour_events[minute] = [[count, ]]

        g_logger.debug("Hour Events: %d, %s"%(start_value,hour_events)) 
        return self.standard_sum_filter(), (start_value, ), hour_events

