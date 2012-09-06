#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
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

import sys
import traceback

from umit.icm.agent.logger import g_logger


class InitializationError(Exception):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, value):
        """Constructor"""
        self.value = value

    def __str__(self):
        return self.value

class AggergatorError(RuntimeError):
    pass

#---------------------------------------------------------------------
class ErrorHandler(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    @classmethod
    def handle_error(self, error):
        traceback.print_exc()
        #g_logger.error("%s: %s" % (type(error), error))
        if isinstance(error, InitializationError):
            sys.exit(1)

        # send an email
        from twisted.mail.smtp import sendmail
        sendmail("smtp.gmail.com", "umiticmmobile@gmail.com", "wzj401@gmail.com",
                 "Exception occurs in ICM Desktop Agent", "gmail.com")


if __name__ == "__main__":
    pass

