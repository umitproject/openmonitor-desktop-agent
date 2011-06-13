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
import os
import sys

from twisted.web import client

from umit.icm.agent.rpc.messages_pb2 import *

from umit.icm.agent.Application import theApp

########################################################################
class AggregatorAPI(object):    
    """"""    

    #----------------------------------------------------------------------
    def __init__(self, url):
        """Constructor"""
        self.base_url = url
    
    """ Peer """
    #----------------------------------------------------------------------
    def register(self):
        url = self.base_url + "/registeragent"
        self._send_request('POST', url, data)
    
    def report_peer_info(self):
        url = self.base_url + "/reportpeerinfo"
        self._send_request('POST', url, data)
    
    def get_super_peer_list(self):
        url = self.base_url + "/getsuperpeerlist"
        self._send_request('POST', url, data)
    
    def get_peer_list(self):
        url = self.base_url + "/getpeerlist"
        self._send_request('POST', url, data)
    
    def get_events(self):
        url = self.base_url + "/getevents"
        self._send_request('POST', url, data)
    
    """ Report """
    #----------------------------------------------------------------------
    def send_report(self):
        url = self.base_url + "/report"
        self._send_request('POST', url, data)
    
    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        url = self.base_url + "/websitesuggestion"
        message = WebsiteSuggestion()
        message.header.token = theApp.peer_info.AuthToken
        message.header.agentID = theApp.peer_info.ID
        message.websiteURL = website_url
        message.emailAddress = theApp.peer_info.Email
        data = base64.b64encode(message.SerializeToString())
        self._send_request('POST', url, data)
    
    def send_service_suggestion(self, service_name, host_name, ip):
        url = self.base_url + "/servicesuggestion"
        message = ServiceSuggestion()
        message.header.token = theApp.peer_info.AuthToken
        message.header.agentID = theApp.peer_info.ID
        message.serviceName = service_name
        message.emailAddress = theApp.peer_info.Email
        message.hostName = host_name
        message.ip = ip
        data = base64.b64encode(message.SerializeToString())
        self._send_request('POST', url, data)
    
    def _send_request(self, method, uri, data="", mimeType=None):
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data:
            headers['Content-Length'] = str(len(data))
        return client.getPage(uri, method=method, postdata=data, 
                              headers=headers)
    

if __name__ == "__main__":
    pass
    
        
        
    
    