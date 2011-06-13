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
"""
This will create a thread for sending test reports
"""

import threading
import time

from umit.icm.agent.Application import theApp
from umit.icm.agent.core.ReportUploader import ReportUploader
from umit.icm.agent.Global import g_logger

########################################################################
class ReportThread(threading.Thread):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name='ReportThread'):
        """Constructor"""
        threading.Thread.__init__(self, name=name)
        self.manager = theApp.report_manager
        self.uploader = ReportUploader(self.manager)
        
    def run(self):        
        g_logger.info("Report thread started.")
        self.uploader.run()
    
    def stop(self):
        g_logger.info("Report thread is stopping.")
        self.uploader.stop()
    
if __name__ == "__main__":
    rt = ReportThread()
    rt.start()
    print('hello')