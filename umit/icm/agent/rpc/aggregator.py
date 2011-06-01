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

__all__ = ['AssignTaskResponser']

import os
import sys

from twisted.web import client

import umit.icm.rpc.messages_pb2

########################################################################
class AggregatorAPI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        pass
    
    """ Peer """
    #----------------------------------------------------------------------
    def sendRegistration(self):
        pass
    
    def sendPeerInfo(self):
        pass
    
    def getSuperPeerList(self):
        pass
    
    def getPeerList(self):
        pass
    
    def getEvents(self):
        pass
    
    """ Report """
    #----------------------------------------------------------------------
    def sendReport(self):
        pass
    
    """ Suggestion """
    #----------------------------------------------------------------------
    def sendWebsiteSuggestion(self):
        pass
    
    def sendServiceSuggestion(self):
        pass
    
    def _sendRequest(self, method, uri, data="", mimeType=None):
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data:
            headers['Content-Length'] = str(len(data))
        return client.getPage(uri, method=method, postdata=data, 
                              headers=headers)
    

########################################################################
class AggregatorResponser(object):
    """"""

    def __init__(self, message):
        """Constructor"""
        pass
        
    def execute(self):
        pass
        
########################################################################
class AssignTaskResponser(AggregatorResponser):
    """"""
    #from umit.icm.rpc.messages_pb2 import AssignTask
    from umit.icm.TaskEntry import TaskEntry
    from umit.icm.TaskManager import TaskManager
    
    def __init__(self, message):
        """Constructor"""
        self.message = message
        
    def execute(self):
        assignTaskMsg = messages_pb2.AssignTask()
        print(assignTaskMsg)
    

if __name__ == "__main__":
    print(sys.modules)
    assignTaskMsg = messages_pb2.AssignTask()    
    pass
    
        
        
    
    