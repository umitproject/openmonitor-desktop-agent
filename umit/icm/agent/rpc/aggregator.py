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
import urllib

from twisted.web import client

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory

from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.core.ReportManager import ReportStatus

aggregator_api_url = {
    'CheckAggregator': '/checkaggregator/',
    'RegisterAgent': '/registeragent/',
    'Login': '/loginagent/',
    'Logout': '/logoutagent/',
    'GetSuperPeerList': '/getsuperpeerlist/',
    'GetPeerList': '/getpeerlist/',
    'GetEvents': '/getevents/',
    'SendWebsiteReport': '/sendwebsitereport/',
    'SendServiceReport': '/sendservicereport/',
    'WebsiteSuggestion': '/websitesuggestion/',
    'ServiceSuggestion': '/servicesuggestion/',
    'NewVersion': '/checkversion/',
    'NewTests': '/checktests/',
}

########################################################################
class AggregatorAPI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.base_url = g_db_helper.get_value('aggregator_url')
        self.available = True
        self.pending_report_ids = []

    def _make_request_header(self, header):
        header.token = theApp.peer_info.AuthToken
        header.agentID = theApp.peer_info.ID

    def check_aggregator(self):
        g_logger.info("Sending CheckAggregator message to aggregator")
        request_msg = CheckAggregator()
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, CheckAggregatorResponse)
        defer_.addCallback(self._handle_check_aggregator_response)
        return defer_

    def _handle_check_aggregator_response(self, message):
        if message.status == "ON":
            self.available = True
        else:
            self.available = False
        g_logger.info("Aggregator status: %s" % message.status)

    """ Peer """
    #----------------------------------------------------------------------

    def register(self, username, password):
        from CryptoLib import *
        crypto = CryptoLib()
        AESKey = crypto.generateAESKey()
        mod = 109916896023924130410814755146616820050848287195403807165245502023708307057182505344954954927069297885076677369989575235572225938578405052695849113605912075520043830304524405776689005895802218122674008335365710906635693457269579474788929265226007718176605597921238270933430352422527094012100555192243443310437
        exp = 65537
        d = 53225089572596125525843512131740616511492292813924040166456597139362240024103739980806956293552408080670588466616097320611022630892254518017345493694914613829109122334102313231580067697669558510530796064276699226938402801350068277390981376399696367398946370139716723891915686772368737964872397322242972049953
        p = 9311922438153331754523459805685209527234133766003151707083260807995975127756369273827143717722693457161664179598414082626988492836607535481975170401420233
        q = 11803888697952041452190425894815849667220518916298985642794987864683223570209190956951707407347610933271302068443002899691276141395264850489845154413900989
        u = 4430245984407139797364141151557666474447820733910504072636286162751503313976630067126466513743819690811621510073670844704114936437585335006336955101762559
        
        RSAKEY_D = 62297015822781158796363618856389920569720490554603739852574703225696321267124285722204224123764419501867928817657919519054848555406464849450959012702348251941541095546410973524267691136995700233299378960173993986706088589136001011922024584878399897228054794884245267290619407261307654480907250669720474301281
        RSAKEY_P = 7757705817565141349021648120631369992682141789699152399326127816192467211564791533199816990028647490792876630757010309393888042701542789312864387282715209
        RSAKEY_Q = 12083491681603271568173938267128976608289124671971871656030565887109349091047806314688865045109296709421488821701923256321238599753290254378297945671005479
        RSAKEY_U = 4807166779721366881723532650380832638823203637550840979310831953962905310688603113539132663918756964730460591047978835536521726443169772132990407509799218
        
        RSAKEY_MOD = 93740173714873692520486809225128030132198461438147249362129501889664779512410440220785650833428588898698591424963196756217514115251721698086685512592960422731696162410024157767288910468830028582731342024445624992243984053669314926468760439060317134193339836267660799899385710848833751883032635625332235630111
        RSAKEY_EXP = 65537        
        
        aggregatorKey = RSAKey(RSAKEY_MOD, RSAKEY_EXP, RSAKEY_D, RSAKEY_P, RSAKEY_Q, RSAKEY_U)
        g_logger.info("Sending RegisterAgent message to aggregator")
        registerMsg = RegisterAgent()
        from umit.icm.agent.Version import VERSION_NUM
        registerMsg.versionNo = VERSION_NUM
        registerMsg.agentType = 'DESKTOP'
        registerMsg.credentials.username = username
        registerMsg.credentials.password = password
        registerMsg.agentPublicKey.mod = str(theApp.key_manager.public_key.mod)
        registerMsg.agentPublicKey.exp = str(theApp.key_manager.public_key.exp)
        if theApp.peer_info.internet_ip:
            registerMsg.ip = theApp.peer_info.internet_ip

        registerMsgSerialized = registerMsg.SerializeToString()
        registerMsg_str = crypto.encodeAES(registerMsgSerialized, AESKey)
        
        key_str = crypto.encodeRSAPublicKey(AESKey, aggregatorKey)

        postdata = {}
        postdata['key'] = key_str
        postdata['msg'] = registerMsg_str

        # send message
        url = self.base_url + aggregator_api_url[registerMsg.DESCRIPTOR.name]
        data = urllib.urlencode(postdata)
        d = self._send_request('POST', url, data)
        return d

    def _handle_register_response(self, message):
        g_logger.info("RegisterAgent response: (%d, %s)" %
                      (response_msg.agentID, message.publicKeyHash))
        theApp.peer_info.ID = message.agentID
        theApp.peer_info.CipheredPublicKeyHash = message.publicKeyHash
        theApp.peer_info.registered = True

    def login(self, username, password):
        g_logger.info("Sending Login message to aggregator")
        request_msg = Login()
        request_msg.agentID = theApp.peer_info.ID
        import random
        self.challenge = str(random.random())
        request_msg.challenge = self.challenge
        request_msg.port = theApp.listen_port
        if theApp.peer_info.internet_ip:
            request_msg.ip = theApp.peer_info.internet_ip

        defer_ = self._send_message(request_msg, LoginStep1)
        defer_.addCallback(self._handle_login_step1)
        return defer_

    def _handle_login_step1(self, message):
        g_logger.info("Received LoginStep1 from aggregator.")
        c = theApp.key_manager.aggregator_public_key.decrypt(message.cipheredChallenge)
        if self.challenge != c:
            g_logger.warning("Challenge doesn't match. Maybe something wrong "
                             "with aggregator public key or the current "
                             "aggregator is fake.")
            return
        g_logger.info("Sending LoginStep2 message to aggregator")
        request_msg = LoginStep2()
        request_msg.processID = message.processID
        request_msg.cipheredChallenge = theApp.key_manager.private_key.encrypt(message.challenge)

        defer_ = self._send_message(request_msg, LoginResponse)
        defer_.addCallback(self._handle_login_response)
        return defer_

    def _handle_login_response(self, message):
        g_logger.info("Received LoginResponse from aggregator.")
        theApp.peer_info.login = True

    def logout(self):
        g_logger.info("Sending Logout message to aggregator")
        request_msg = Logout()
        #self._make_request_header(request_msg.header)
        defer_ = self._send_message(request_msg)
        #defer_.addCallback(self._handle_logout)
        return defer_

    #def _handle_logout(self, message):
        #g_logger.info("Received LogoutResponse from aggregator.")
        #theApp.peer_info.login = False

    #def report_peer_info(self):
        #g_logger.info("Sending ReportPeerInfo message to aggregator")
        #url = self.base_url + "/reportpeerinfo/"
        #result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        g_logger.info("Sending GetSuperPeerList message to aggregator")
        request_msg = GetSuperPeerList()
        #self._make_request_header(request_msg.header)

        defer_ = self._send_message(request_msg, GetSuperPeerListResponse)
        defer_.addCallback(self._handle_get_super_peer_list_response)
        return defer_

    def _handle_get_super_peer_list_response(self, message):
        for speer in message.knownSuperPeers:
            theApp.peer_manager.add_super_peer(speer.agentID,
                                               speer.agentIP,
                                               speer.agentPort,
                                               speer.token,
                                               speer.publicKey)
            theApp.peer_manager.connect_to_peer(speer.agentID)

    def get_peer_list(self, count):
        g_logger.info("Sending GetPeerList message to aggregator")
        url = self.base_url + "/getpeerlist/"
        request_msg = GetPeerList()
        #self._make_request_header(request_msg.header)

        defer_ = self._send_message(request_msg, GetPeerListResponse)
        defer_.addCallback(self._handle_get_peer_list_response)
        return defer_

    def _handle_get_peer_list_response(self, message):
        for peer in message.knownPeers:
            theApp.peer_manager.add_normal_peer(peer.agentID,
                                                peer.agentIP,
                                                peer.agentPort,
                                                peer.token,
                                                peer.publicKey)
            theApp.peer_manager.connect_to_peer(peer.agentID)

    """ Event """
    #----------------------------------------------------------------------
    def get_events(self):
        g_logger.info("Sending GetEvents message to aggregator")
        url = self.base_url + "/getevents/"
        request_msg = GetEvents()
        #self._make_request_header(request_msg.header)

        defer_ = self._send_message(request_msg, GetEventsResponse)
        defer_.addCallback(self._handle_get_events_response)
        return defer_

    def _handle_get_events_response(self, message):
        for event in message.events:
            theApp.event_manager.add_event(event)

    """ Report """
    #----------------------------------------------------------------------
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.pending_report_ids.append(report.header.reportID)
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            self.pending_report_ids.append(report.header.reportID)
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        g_logger.debug("Sending WebsiteReport to aggregator")
        url = self.base_url + "/sendwebsitereport/"
        request_msg = SendWebsiteReport()
        #self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_website_report_response)
        return defer_

    def _handle_send_website_report_response(self, message):
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.pending_report_ids.pop(0) # assume FIFO
        g_logger.info("WebsiteReport '%s' has been sent to aggregator" % \
                      report_id)
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_AGGREGATOR)

    def send_service_report(self, report):
        g_logger.debug("Sending ServiceReport to aggregator")
        url = self.base_url + "/sendservicereport/"
        request_msg = SendServiceReport()
        #self._make_request_header(request_msg.header)
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_service_report_response)
        return defer_

    def _handle_send_service_report_response(self, message):
        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1
        report_id = self.pending_report_ids.pop(0) # assume FIFO
        g_logger.info("ServiceReport '%s' has been sent to aggregator" % \
                      report_id)
        theApp.report_manager.remove_report(report_id,
                                            ReportStatus.SENT_TO_AGGREGATOR)

    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        g_logger.info("Sending WebsiteSuggestion message to aggregator")
        url = self.base_url + "/websitesuggestion/"
        request_msg = WebsiteSuggestion()
        #self._make_request_header(request_msg.header)
        request_msg.websiteURL = website_url
        request_msg.emailAddress = theApp.peer_info.Email

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_website_suggestion_response)
        return defer_

    def _handle_website_suggestion_response(self, message):
        g_logger.info("WebsiteSuggestion has been sent to aggregator")
        return True

    def send_service_suggestion(self, service_name, host_name, ip):
        g_logger.info("Sending ServiceSuggestion message to aggregator")
        url = self.base_url + "/servicesuggestion/"
        request_msg = ServiceSuggestion()
        #self._make_request_header(request_msg.header)
        request_msg.serviceName = service_name
        request_msg.emailAddress = theApp.peer_info.Email
        request_msg.hostName = host_name
        request_msg.ip = ip

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_service_suggestion_response)
        return defer_

    def _handle_service_suggestion_response(self, message):
        g_logger.info("ServiceSuggestion has been sent to aggregator")
        return True

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        g_logger.info("Sending NewVersion message to aggregator")
        request_msg = NewVersion()
        #self._make_request_header(request_msg.header)
        from umit.icm.agent.Version import VERSION_NUM
        request_msg.agentVersionNo = VERSION_NUM
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, NewVersionResponse)
        defer_.addCallback(self._handle_check_version_response)
        return defer_

    def _handle_check_version_response(self, message):
        print(message)

    def check_tests(self):
        g_logger.info("Sending NewTests message to aggregator")
        request_msg = NewTests()
        #self._make_request_header(request_msg.header)
        from umit.icm.agent.test import TEST_PACKAGE_VERSION_NUM
        request_msg.currentTestVersionNo = TEST_PACKAGE_VERSION_NUM

        defer_ = self._send_message(request_msg, NewTestsResponse)
        defer_.addCallback(self._handle_check_tests_response)
        return defer_

    def _handle_check_tests_response(self, message):
        print(message)

    """ Private """
    #----------------------------------------------------------------------
    def _rsa_encrypt(self, message):
        return base64.b64encode(
            theApp.key_manager.aggregator_public_key.encrypt(
                message.SerializeToString()))

    def _rsa_decrypt(self, text, msg_type):
        message = msg_type()
        message.ParseFromString(
            theApp.key_manager.private_key.decrypt(
                base64.b64decode(text)))
        return message

    def _aes_encrypt(self, message):
        assert theApp.key_manager.aggregator_aes_key
        return base64.b64encode(
            theApp.key_manager.aggregator_aes_key.encrypt(
                message.SerializeToString()))

    def _aes_decrypt(self, text, msg_type):
        assert theApp.key_manager.aggregator_aes_key
        message = msg_type()
        message.ParseFromString(
            theApp.key_manager.aggregator_aes_key.decrypt(
                base64.b64decode(text)))
        return message

    def _encode(self, message):
        return base64.b64encode(message.SerializeToString())

    def _decode(self, text, msg_type):
        message = msg_type()
        message.ParseFromString(base64.b64decode(text))
        return message

    def _send_message(self, message, response_msg_type=None):
        #if safeSend and not self.available:
            #speer_id = theApp.peer_manager.get_random_speer_connected()
            #if speer_id is not None:
                #return theApp.peer_manager.sessions[speer_id].\
                       #forward_message(0, message)

        postdata = {}

        # encode message
        if isinstance(message, CheckAggregator):
            postdata['msg'] = self._encode(message)
        elif isinstance(message, RegisterAgent):
            # generate AES key
            from umit.icm.agent.secure.Key import AESKey
            theApp.key_manager.aggregator_aes_key = AESKey()
            theApp.key_manager.aggregator_aes_key.generate()
            g_db_helper.set_value('aggregator_aes_key',
                                  theApp.key_manager.aggregator_aes_key.get_key())

            postdata['key'] = base64.b64encode(
                theApp.key_manager.aggregator_public_key.encrypt(
                    base64.b64encode(
                        theApp.key_manager.aggregator_aes_key.get_key())))
            postdata['msg'] = self._aes_encrypt(message)
        else:
            postdata['msg'] = self._aes_encrypt(message)

        # send message
        url = self.base_url + aggregator_api_url[message.DESCRIPTOR.name]
        data = urllib.urlencode(postdata)
        print url
        print message.DESCRIPTOR.name
        defer_ = self._send_request('POST', url, data)
        print "here"
        # decode message
        if response_msg_type is not None:
            if isinstance(message, CheckAggregator):
                defer_.addCallback(self._decode, response_msg_type)
            else:
                defer_.addCallback(self._aes_decrypt, response_msg_type)
        return defer_


    def _send_request(self, method, uri, data="", mimeType=None):
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data:
            headers['Content-Length'] = str(len(data))
        d = client.getPage(uri, method=method, postdata=data,
                           headers=headers)
        d.addErrback(self._handle_error)
        return d

    def _handle_error(self, failure):
        print("[AggregatorAPI] - %s" % failure)
        from twisted.internet import error
        failure.trap(error.ConnectError, error.DNSLookupError)
        g_logger.error("Connecting to the aggregator failed.")
        self.available = False
        theApp.statistics.aggregator_fail_num = \
              theApp.statistics.aggregator_fail_num + 1


if __name__ == "__main__":
    import time
    api = AggregatorAPI()
    #api = AggregatorAPI('http://www.baidu.com')
    d = api.check_version()

    report = WebsiteReport()
    report.header.reportID = 'xw384kkre'
    report.header.agentID = 10000
    report.header.testID = 1
    report.header.timeZone = 8
    report.header.timeUTC = int(time.time())
    report.report.websiteURL = 'http://www.baidu.com'
    report.report.statusCode = 200

    #api.send_report(report)

    #api.register("test1", "test", "test@hotmail.com")

    from twisted.internet import reactor
    reactor.callLater(10, reactor.stop)
    reactor.run()
