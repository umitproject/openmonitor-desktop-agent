#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#              Tianwei Liu <liutinweidlut@gmail.com>
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
"""
HTTPDownload with progress
"""

from twisted.internet import reactor
from twisted.web.client import HTTPDownloader
from twisted.web import client

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp

class FileDownloader(object):
    """Download file from HTTP server"""

    #----------------------------------------------------------------------
    def __init__(self, url, local_path):
        """Constructor"""
        #if https or ftp?
        if not url.startswith("http://") or url.startswith("https://"):
            raise Exception("URL must start with 'http://' or 'https://'")
        self._url = str(url)
        self._local_path = local_path

    #----------------------------------------------------------------------
    def start(self):
        g_logger.info("URL: %s" % self._url)
        g_logger.info("Local Path: %s" % self._local_path)
        g_logger.info("Download started.")
        print "test"
        
        factory = HTTPDownloader(self._url, self._local_path)
        factory.deferred.addErrback(g_logger.error)
        factory.deferred.addCallback(self._downloadComplete)
        if hasattr(self, '_callback'):
            factory.deferred.addCallback(self._callback, *self._callback_args,
                                         **self._callback_kw)
        
        if self._url.startswith("https://"):
            from twisted.internet import ssl
            content_factory = ssl.ClientContextFactory()
            reactor.connectSSL(factory.host, factory.port, factory, content_factory, timeout, bindAddress)
        else:
            reactor.connectTCP(factory.host, factory.port, factory)

    #----------------------------------------------------------------------
    def addCallback(self, callback, *args, **kw):
        self._callback = callback
        self._callback_args = args
        self._callback_kw = kw

    #----------------------------------------------------------------------
    def _downloadComplete(self, result):
        g_logger.info("Download Completed.")

        
class HTTPProgressDownloader(HTTPDownloader):
    """
    subclass of HTTPDownloader, to show progress of the download
    """
    pass




