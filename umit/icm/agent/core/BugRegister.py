#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
# Author: Tianwei Liu <liutianweidlut@gmail.com>
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

from pyactiveresource.activeresource import ActiveResource
import time

#from umit.icm.agent.Version import VERSION

redmine_site="http://dev.umitproject.org/"
redmine_login=redmine_site +"login"
redmine_project=redmine_site + "projects/desktop-agent/"
redmine_new_issue=redmine_project + "issues/new"
redmine_submit=redmine_new_issue

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
        self.input =  ""
        self.file_description = ""
        self.assignedID = ""
        self.username = ""
        self.passwd = ""
        
        self.component = ""
        self.summary = ""
        self.details = ""
        self.reporter = ""
     
    def report(self):
        '''
        using Activeresource to create a new issue in Redmin
        '''
        # Get time 
        self.start_date = time.strftime("%Y-%m-%d",time.localtime())
        # Write Content
        self.subject = "[BugCrashReport]" +self.summary 
        self.description = "From: "+self.reporter +"\r\n" +self.details   
        # Create Issue
        attributes ={
             "description":self.description,
             "subject":self.subject,
             "start_date":self.start_date,
             }
        ret = Issue.create(attributes)
        return ret

class Issue(ActiveResource):
    _site = redmine_project
    
if __name__ == "__main__":
    bug = BugRegister()
    bug.report()