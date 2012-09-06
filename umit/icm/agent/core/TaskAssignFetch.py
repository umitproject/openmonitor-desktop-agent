#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import time

from zope.interface import implements
from twisted.internet.interfaces import IConsumer

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *

class TaskAssignFetch(object):
    """"""
    
    implements(IConsumer)
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
    
    def task_append(self,message):
        print 'append test'
        
        #self.task_manager.add_test(1, '*/3 * * * *', {'url':'http://www.sina.com.cn'}, 2)
        pass
    
    def fetch_task(self):
        """
        fetch task from Aggregator by using Aggregator AssignTask API
        """
        if theApp.aggregator.available:
            g_logger.info("Fetching assigned task from aggregator")
           # defer_ = theApp.aggregator.get_task()
           # defer_.addCallback(self.task_append)
           # defer_.addErrback(self._handler_error(failure))
        else:
            g_logger.error("Cannot connect to Aggregator")
            
    def _handler_error(self,failure):
        
        g_logger.error("fetch task error %s"%str(failure))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        