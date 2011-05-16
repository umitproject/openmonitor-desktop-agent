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



import webbrowser

from Test import Test
from twisted.internet import reactor
from twisted.web.client import HTTPDownloader
from twisted.python import log

########################################################################
class HTTPFetcher(Test):
    """Fetch a certain URL"""    

    #----------------------------------------------------------------------
    def __init__(self, url, savePath):
        """Constructor"""
        if not url.startswith("http://"):
            raise Exception("URL must start with 'http://'")
        self.url = url
        self.path = savePath
        pass
        
    #----------------------------------------------------------------------
    def setup(self, params):
        """Setup the test"""
        
    #----------------------------------------------------------------------
    def execute(self):
        """"""
        factory = HTTPDownloader(self.url, self.path)
        factory.deferred.addCallback(self.downloadComplete).addErrback(log.err)
        reactor.connectTCP(factory.host, factory.port, factory)
        reactor.run()
        
    def downloadComplete(self, result):
        print("download Complete")
        reactor.stop()
        webbrowser.open(self.path)
                                    
        
        
    
    