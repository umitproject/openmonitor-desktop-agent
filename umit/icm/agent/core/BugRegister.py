#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Tianwei Liu <liutianweidlut@gmail.com>
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

import time
import re
import urllib
import urllib2
from tempfile import mktemp

#from umit.icm.agent.Version import VERSION

redmine_site="http://dev.umitproject.org/"
redmine_project=redmine_site + "projects/desktop-agent/"
redmine_new_ticket=redmine_site + "newticket"
redmine_submit=redmine_new_ticket

class BugRegister(object):
    def __init__(self):
        self.tracker = "Bug"
        self.subject = ""
        self.description = ""
        self.status = ""
        self.priority = ""
        self.target_version = "0.1b"    #Desktop Agent Version 
        self.start_date=""
        self.due_date=""
        self.estimated_time = "" 
        self.done = ""
        self.input_file =  ""
        self.file_description = ""
        self.assignedID = ""
        self.submit = "submit"
        self.keywords = "user crash report"
        self.type = "defect"
        self.milestone = "0.1b"
        
        self.component = "test"
        self.summary = "test"
        self.details = "test"
        self.reporter = "user"
    
    # Function to get the cookie of headers
    def __get_cookie(self, header, name):
        """
        Receive header and the name intended to find
        Returns the value or None if not found
        """
        try:
            pattern = r".*%s=([^;]+)[;]{0,1}.*" % name 
            return re.findall(pattern, header['Set-cookie'])[0]
        except Exception, ex:
            return None    
     
    def report(self):
        ''''''
        f = urllib2.urlopen(redmine_new_ticket)
        # Get cookie redmine_session
        redmine_session = self.__get_cookie(f.headers, "redmine_session")
        # Get cookie trac_session
        trac_session = self.__get_cookie(f.headers, "trac_session")
        # Get value of __FORM_TOKEN
        trac_form = self.__get_cookie(f.headers, "trac_form_token")
        if (trac_form is None or trac_session is None):
            return None
        
        # Get time 
        self.start_date = time.strftime("%Y-%m-%d",time.localtime())
        # Write Content
        self.subject = "[BugCrashReport]" +self.summary 
        self.description = "From: "+self.reporter +"\r\n" +self.details   

        query = {
                #"description":self.description,
                #"subject":self.subject,
                #"start_date":self.start_date
                "field_summary": self.summary,
                "__FORM_TOKEN": trac_form,
                "field_type": self.type,
                "field_description": self.details,
                "field_milestone": self.milestone,
                #"field_component":self.component,
                "field_version": self.target_version,
                "field_keywords": self.keywords,
                #"owner":self.assigned_to,
                "cc": self.assignedID,
                "author": self.reporter,
                #"attachment":self.input_file,
                "field_status": "new",
                "action": "create",
                "submit": self.submit
                }
        if self.component:
            query['field_component'] = self.component
        data = urllib.urlencode(query)

        request = urllib2.Request(redmine_new_ticket, data)
        #request.add_header("Cookie", "_redmine_session=%s;"% (redmine_session))
        request.add_header("Cookie", "_redmine_session=%s;\
                            trac_session=%s\
                            trac_form_token=%s" % (redmine_session,trac_session,trac_form))

        response = urllib2.urlopen(request)
        return response.geturl()
    
if __name__ == "__main__":
    bug = BugRegister()
    bug.report()
