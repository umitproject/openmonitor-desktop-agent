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

from email.mime.text import MIMEText

from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator, ClientFactory
from twisted.mail import smtp


class BugReportMailProtocol(smtp.ESMTPClient):
    """"""

    def __init__(self, username, password):
        smtp.ESMTPClient.__init__(self, password, None, username)

    def getMailFrom(self):
        return "icmdesktopagent@gmail.com"

    def getMailTo(self):
        return "nonexist@umitproject.org"

    def sentMail(self, code, resp, numOk, addresses, log):
        if self.reportDeferred:
            result = {'status_code': 0, 'time_end': default_timer()}
            self.reportDeferred.callback(result)
            self.reportDeferred = None
        self._disconnectFromServer()


#---------------------------------------------------------------------
class EmailSender(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, smtp_host, smtp_port, username="", password=""):
        """Constructor"""
        self.host = smtp_host
        self.port = smtp_port
        self.client = ClientCreator(reactor, SMTPClient, username, password)\
            .connectTCP(self.host, self.port)\
            .addErrback(self._connectionFailed)

    #----------------------------------------------------------------------
    def _connectionFailed(self, failure):
        """"""
        print(failure)


    #----------------------------------------------------------------------
    def send_mail(from_addr, to_addr, cc_addr="", title="", body=""):
        """"""
        msg = MIMEText(body)
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['CC'] = cc_addr
        msg['Subject'] = title
        self.client.send


if __name__ == "__main__":
    sender = EmailSender("smtp.gmail.com", 25, "umiticmdesktop", "umiticmdesktop2011")
    sender.send_mail("umiticmdesktop@gmail.com", "wzj401@gmail.com",
                     title="Hello",
                     body="Across the GFW")