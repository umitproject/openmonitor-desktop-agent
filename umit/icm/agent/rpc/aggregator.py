#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
#           Adriano Marques <adriano@umitproject.org>
#           Tianwei Liu <liutianweidlut@gmail.com>
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
import random
import time

from twisted.web import client
from twisted.web.error import Error
from twisted.internet import error
from twisted.web.http_headers import Headers
from twisted.web.client import Agent
from twisted.internet import reactor

from google.protobuf.text_format import MessageToString

from umit.icm.agent.rpc.message import *
from umit.icm.agent.rpc.MessageFactory import MessageFactory
from umit.proto import messages_pb2

from umit.icm.agent.logger import g_logger
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.rpc.Session import Session
from umit.icm.agent.core.ReportManager import ReportStatus
from umit.icm.agent.Errors import AggergatorError
from umit.icm.agent.secure.Key import AESKey
from umit.icm.agent.Version import VERSION_NUM
from umit.icm.agent.test import TEST_PACKAGE_VERSION_NUM

from umit.icm.agent.I18N import _

aggregator_api_url = {
    'CheckAggregator': '/api/checkaggregator/',
    'RegisterAgent': '/api/registeragent/',
    'Login': '/api/loginagent/',
    'LoginStep2': '/api/loginagent2/',
    'Logout': '/api/logoutagent/',
    'GetSuperPeerList': '/api/getsuperpeerlist/',
    'GetPeerList': '/api/getpeerlist/',
    'GetEvents': '/api/getevents/',
    'SendWebsiteReport': '/api/sendwebsitereport/',
    'SendServiceReport': '/api/sendservicereport/',
    'WebsiteSuggestion': '/api/websitesuggestion/',
    'ServiceSuggestion': '/api/servicesuggestion/',
    'NewVersion': '/api/checkversion/',
    'NewTests': '/api/checktests/',
    'GetNetlist': '/api/get_netlist/',
    'GetBanlist': '/api/get_banlist/',
    'GetBannets': '/api/get_bannets/',
    #'AssignTask':'/api/assign_task',
}

#---------------------------------------------------------------------
class AggregatorAPI(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, aggregator=None):
        """Constructor"""
        self.base_url = g_config.get('network', 'aggregator_url') \
            if aggregator is None else aggregator
        
        self.available = True
        self.pending_report_ids = []

    def check_aggregator(self):
        request_msg = CheckAggregator()
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, CheckAggregatorResponse)
        defer_.addCallback(self._handle_check_aggregator_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_check_aggregator_response(self, message):
        if message is None:
            return

        if message.status == "ON":
            self.available = True
        else:
            self.available = False
        g_logger.info("Aggregator status: %s" % message.status)
        g_logger.debug("Aggregator version: %s" % message.header.currentVersionNo)
        g_logger.debug("Aggregator test version: %s" % message.header.currentTestVersionNo)

        return message

    def check_aggregator_website(self):
        """
        Run aggregator website test
        """
        g_logger.info("Testing Aggregator website: %s" % self.base_url)
        
        defer_ = Agent(reactor).request('GET',self.base_url,
                                Headers({'User-Agent':['ICM Website Test']}),
                                None)
        defer_.addCallback(self._handle_check_aggregator_website)    
        defer_.addErrback(self._handle_check_aggregator_website_err)
        
        return defer_
        
    def _handle_check_aggregator_website(self,message):
        """
        """
        status_code = message.code
        HTTP_SUCCESS_CODE = (200,302)
        if int(status_code) in HTTP_SUCCESS_CODE:
            g_logger.info("Testing Aggregator website: %s" % status_code)
            self.available = True
        else:
            g_logger.info("Cannot connect Aggregator website: %s" % self.base_url)
            self.available = False
        
        return self.available
    
    def _handle_check_aggregator_website_err(self,failure):
        """
        """
        g_logger.info("Cannot connect Aggregator website: %s" % self.base_url)
        self.available = False
        
        return self.available

    """ Peer """
    #----------------------------------------------------------------------

    def register(self, username, password):
        request_msg = RegisterAgent()
        request_msg.versionNo = VERSION_NUM
        request_msg.agentType = 'DESKTOP'
        request_msg.credentials.username = username
        request_msg.credentials.password = password
        request_msg.agentPublicKey.mod = str(theApp.key_manager.public_key.mod)
        request_msg.agentPublicKey.exp = str(theApp.key_manager.public_key.exp)
        if theApp.peer_info.internet_ip:
            request_msg.ip = theApp.peer_info.internet_ip
        print request_msg
        # send message
        defer_ = self._send_message(request_msg, RegisterAgentResponse)
        defer_.addCallback(self._handle_register_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_register_response(self, message):
        if message is None:
            g_logger.error("Empty response while trying to register.")
            return

        g_logger.info("RegisterAgent response: (%s, %s)" %
                      (message.agentID, message.publicKeyHash))

        return {'id': message.agentID, 'hash': message.publicKeyHash}
    
    def _handle_register_error_response(self,failure):
        if failure is None:
            g_logger.error("Error empty response while trying to register.")
            return 
        
    def login(self, username, password):
        request_msg = Login()
        request_msg.agentID = str(theApp.peer_info.ID)

        self.challenge = str(random.random())
        request_msg.challenge = self.challenge
        request_msg.port = theApp.listen_port
        if theApp.peer_info.internet_ip:
            request_msg.ip = theApp.peer_info.internet_ip

        defer_ = self._send_message(request_msg, LoginStep1)
        defer_.addCallback(self._handle_login_step1)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_login_step1(self, message):
        if message is None:
            return
        #print "------------------login step1--------------"
        #print message
        if not theApp.key_manager.aggregator_public_key.verify(
            self.challenge, message.cipheredChallenge):
            g_logger.warning("Challenge doesn't match. Maybe something wrong "
                             "with aggregator public key or the current "
                             "aggregator is fake.")
            return
        #print "-----------------end------------------------"
        request_msg = LoginStep2()
        request_msg.processID = message.processID
        request_msg.cipheredChallenge = theApp.key_manager.private_key.sign(message.challenge)

        defer_ = self._send_message(request_msg, LoginResponse)
        defer_.addCallback(self._handle_login_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_login_response(self, message):
        if message is None:
            return

        g_logger.info("Login successfully.")

        # Being available, we need to retrieve the bannets and banlist
        d = theApp.aggregator.get_banlist()
        d = theApp.aggregator.get_bannets()

        return True

    def logout(self):
        request_msg = Logout()
        request_msg.agentID = str(theApp.peer_info.ID)
        defer_ = self._send_message(request_msg)
        defer_.addCallback(self._handle_logout)

        return defer_

    def _handle_logout(self, message):
        g_logger.debug("Logout message: %s" % message)

        theApp.peer_info.login = False

        return message

    #def report_peer_info(self):
        #g_logger.info("Sending ReportPeerInfo message to aggregator")
        #url = self.base_url + "/reportpeerinfo/"
        #result = self._send_request('POST', url, data)

    def get_super_peer_list(self, count):
        request_msg = GetSuperPeerList()
        request_msg.count = int(count)

        defer_ = self._send_message(request_msg, GetSuperPeerListResponse)
        defer_.addCallback(self._handle_get_super_peer_list_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_super_peer_list_response(self, message):
        if message is None:
            return
        
        g_logger.info("Got %d super peers from aggregator!"%(len(message.knownSuperPeers)))        
        
        for speer in message.knownSuperPeers:
            theApp.peer_manager.add_super_peer(speer.agentID,
                                               speer.agentIP,
                                               speer.agentPort,
                                               speer.token,
                                               speer.publicKey)
            theApp.peer_manager.connect_to_peer(speer.agentID)
        
        
        return message

    def get_peer_list(self, count):
        url = self.base_url + "/getpeerlist/"
        request_msg = GetPeerList()
        request_msg.count = int(count)

        defer_ = self._send_message(request_msg, GetPeerListResponse)
        defer_.addCallback(self._handle_get_peer_list_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_peer_list_response(self, message):
        if message is None:
            return
        
        g_logger.info("Got %d normal peers from aggregator!"%(len(message.knownPeers))) 
         
        for peer in message.knownPeers:
            theApp.peer_manager.add_normal_peer(peer.agentID,
                                                peer.agentIP,
                                                peer.agentPort,
                                                peer.token,
                                                peer.publicKey)
            theApp.peer_manager.connect_to_peer(peer.agentID)

        return message
    
    """ Assign Task"""
    #----------------------------------------------------------------------
    def get_task(self):
        url = self.base_url + "/gettasks/"
        request_msg = AssignTask()
        request_msg.header.agentID = str(theApp.peer_info.ID)
        defer_ = self._send_message(request_msg, AssignTaskResponse)
        defer_.addCallback(self._handle_get_task_response)
        defer_.addErrback(self._handle_errback)
        
        return defer_
        
    def _handle_get_task_response(self,message):
        if message in None:
            return 
        
        print message
        print message.header
        print message.tests
        
        g_logger.debug("We have got tasks from aggregator")  
        
        return message
                

    """ Event """
    #----------------------------------------------------------------------
    def get_events(self,location_user):
        url = self.base_url + "/getevents/"
        request_msg = GetEvents()
        
        #print location_user.latitude, location_user.longitude
        #repeated 
        location = request_msg.locations.add()
        location.longitude = location_user.longitude
        location.latitude  = location_user.latitude
        
        defer_ = self._send_message(request_msg, GetEventsResponse)
        defer_.addCallback(self._handle_get_events_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_get_events_response(self, message):
        if message is None:
            return
        
        #print message
        #print message.events
        
        g_logger.debug("We have got events from aggregator")
        for event in message.events:
            theApp.event_manager.add_event(event)

        return message

    """ Report """
    #----------------------------------------------------------------------
    def send_report(self, report):
        if isinstance(report, WebsiteReport):
            self.pending_report_ids.append(report.header.reportID)
            self.send_website_report(report)
        elif isinstance(report, ServiceReport):
            print report
            self.pending_report_ids.append(report.header.reportID)
            self.send_service_report(report)
        else:
            g_logger.debug("Unable to recognize the report type.")

    def send_website_report(self, report):
        url = self.base_url + "/sendwebsitereport/"
        request_msg = SendWebsiteReport()
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_website_report_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_send_website_report_response(self, message):
        if message is None:
            return

        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1

        if len(self.pending_report_ids):
            report_id = self.pending_report_ids.pop(0) # assume FIFO
            g_logger.info("WebsiteReport '%s' has been sent to aggregator" % \
                          report_id)
            theApp.report_manager.remove_report(report_id,
                                                ReportStatus.SENT_TO_AGGREGATOR)
        else:
            g_logger.info("WebsiteReport has been sent to aggregator")

        return message

    def send_service_report(self, report):
        url = self.base_url + "/sendservicereport/"
        request_msg = SendServiceReport()
        #print '~__________________________'
        #print report
        request_msg.report.CopyFrom(report)

        defer_ = self._send_message(request_msg, SendReportResponse)
        defer_.addCallback(self._handle_send_service_report_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_send_service_report_response(self, message):
        g_logger.debug("Handle Send Service Report: %s" % message)
        if message is None:
            return

        theApp.statistics.reports_sent_to_aggregator = \
              theApp.statistics.reports_sent_to_aggregator + 1

        if len(self.pending_report_ids):
            report_id = self.pending_report_ids.pop(0) # assume FIFO
            g_logger.info("ServiceReport '%s' has been sent to aggregator" % \
                          report_id)
            theApp.report_manager.remove_report(report_id,
                                                ReportStatus.SENT_TO_AGGREGATOR)
        else:
            g_logger.info("ServiceReport has been sent to aggregator")

        return message

    """ Suggestion """
    #----------------------------------------------------------------------
    def send_website_suggestion(self, website_url):
        url = self.base_url + "/websitesuggestion/"
        request_msg = WebsiteSuggestion()

        request_msg.websiteURL = website_url

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_website_suggestion_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_website_suggestion_response(self, message):
        if message is None:
            return
        g_logger.info("WebsiteSuggestion has been sent to aggregator")

        return message

    def send_service_suggestion(self, service_name, host_name, ip, port):
        url = self.base_url + "/servicesuggestion/"
        request_msg = ServiceSuggestion()

        request_msg.serviceName = service_name
        request_msg.hostName = host_name
        request_msg.ip = ip
        request_msg.port = port

        defer_ = self._send_message(request_msg, TestSuggestionResponse)
        defer_.addCallback(self._handle_service_suggestion_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_service_suggestion_response(self, message):
        if message is None:
            return
        g_logger.info("ServiceSuggestion has been sent to aggregator")

        return message

    """ Version """
    #----------------------------------------------------------------------
    def check_version(self):
        self.check_message = {}
        request_msg = NewVersion()

        request_msg.agentVersionNo = VERSION_NUM
        request_msg.agentType = 'DESKTOP'

        defer_ = self._send_message(request_msg, NewVersionResponse)
        defer_.addCallback(self._handle_check_version_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_check_version_response(self, message):
        
        if message is None:
            return
        g_logger.info("Get check_version_response %s" % message) 
        
        #add the record into the Database
        from umit.icm.agent.gui.SoftwareUpdate import check_update_item_in_db,insert_update_item_in_db,no_updated
        check_message = {}
        
        check_message["download_url"] = message.downloadURL 
        check_message["version"] = str(message.versionNo)   
        check_message["news_date"] = time.strftime("%Y-%m-%d",time.localtime())
        check_message["software_name"] = "OpenMonitor Desktop V" + str(message.versionNo)
        check_message["is_update"] = no_updated
        check_message["description"] = "Open Monitor Desktop Agent!" 
        check_message["check_code"] = ""
         
        if not check_update_item_in_db(check_message["version"]):
            insert_update_item_in_db(check_message)
            g_logger.info("Write a new update record into DB :%s" % check_message) 
          
        return  message

    
    """ Test sets"""
    #----------------------------------------------------------------------   
    def check_tests(self,current_version):
        request_msg = NewTests()
        request_msg.currentTestVersionNo = int(current_version)  #Get current version from DB
        #print 'test:',request_msg.currentTestVersionNo
        defer_ = self._send_message(request_msg, NewTestsResponse)
        defer_.addCallback(self._handle_check_tests_response)
        defer_.addErrback(self._handle_check_tests_error)
        return defer_

    def _handle_check_tests_response(self, message):
        if message is None:
            return
        
        #print message.tests
        #print message.testVersionNo
        
        g_logger.info("Receive Test Sets!")     
        return message
    
    def _handle_check_tests_error(self,failure):
        g_logger.error("check tests error!%s"%str(failure))
        #print failure
        
    """Test Module"""
    def check_test_moduler(self):
        pass
        
    def _handle_check_test_moduler_response(self):
        if message is None:
            return 
        
        g_logger.info("Get Test Moduler Update")             
        return messge

    """ Other Informations """
    #----------------------------------------------------------------------
    def get_netlist(self, count):
        request_msg = GetNetlist()
        request_msg.list = count

        defer_ = self._send_message(request_msg, GetNetlistResponse)
        defer_.addCallback(self._handle_get_netlist_response)
        defer_.addErrback(self._handle_errback)

        return defer_

    def _handle_get_netlist_response(self, message):
        if message is None:
            return

        for net in message.networks:
            id = g_db_helper.insert_network(net.start_ip,
                                            net.end_ip,
                                            net.nodesCount)

            for node in net.nodes:
                theApp.peer_manager.add_normal_peer(node.agentID,
                                                    node.agentIP,
                                                    node.agentPort,
                                                    node.token,
                                                    node.publicKey,
                                                    node.peerStatus,
                                                    id)

            theApp.peer_manager.save_to_db()

        return message

    def get_banlist(self, count=100):
        request_msg = GetBanlist()
        request_msg.count = count

        defer_ = self._send_message(request_msg, GetBanlistResponse)
        defer_.addCallback(self._handle_get_banlist_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_banlist_response(self, message):
        g_logger.info("GET BANLIST RESPONSE: %s" % message)
        if message is None:
            return

        # TODO: Store the banlist locally
        theApp.peer_manager.sync_banlist(message)

        return message

    def get_bannets(self, count=100):
        request_msg = GetBannets()
        request_msg.count = count

        defer_ = self._send_message(request_msg, GetBannetsResponse)
        defer_.addCallback(self._handle_get_bannets_response)
        defer_.addErrback(self._handle_errback)
        return defer_

    def _handle_get_bannets_response(self, message):
        g_logger.info("GET BANNETS RESPONSE: %s" % message)
        if message is None:
            return

        # TODO: Store the bannets locally
        theApp.peer_manager.sync_bannets(message)

        return message

    """ Private """
    #----------------------------------------------------------------------
    def _rsa_encrypt(self, message):
        return base64.b64encode(
            theApp.key_manager.aggregator_public_key.encrypt(
                message.SerializeToString()))

    def _rsa_decrypt(self, text, msg_type):
        if text is None:
            return
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
        if text is None:
            return

        assert theApp.key_manager.aggregator_aes_key

        message = msg_type()
        message.ParseFromString(
            theApp.key_manager.aggregator_aes_key.decrypt(
                base64.b64decode(text)))

        return message

    def _encode(self, message):
        return base64.b64encode(message.SerializeToString())

    def _decode(self, text, msg_type):
        if text is None:
            return

        message = msg_type()
        message.ParseFromString(base64.b64decode(text))

        return message

    """ utils """
    #----------------------------------------------------------------------
    
    def _send_message(self, message, response_msg_type=None):
        postdata = {}
        postdata['crypto_v1'] = 1

        # encode message
        if isinstance(message, CheckAggregator):
            postdata['msg'] = self._encode(message)
        elif isinstance(message, Login) or isinstance(message, LoginStep2):
            postdata['msg'] = self._encode(message)
        elif isinstance(message, RegisterAgent):
            # generate AES key
            theApp.key_manager.aggregator_aes_key = AESKey()
            theApp.key_manager.aggregator_aes_key.generate()
            g_db_helper.set_value('keys', 'aggregator_aes_key',
                                  theApp.key_manager.aggregator_aes_key.get_key())

            postdata['key'] = base64.b64encode(
                theApp.key_manager.aggregator_public_key.encrypt(
                    base64.b64encode(
                        theApp.key_manager.aggregator_aes_key.get_key())))
            postdata['msg'] = self._aes_encrypt(message)            
        else:
            postdata['agentID'] = str(theApp.peer_info.ID)
            postdata['msg'] = self._aes_encrypt(message)

        # send message
        url = self.base_url + aggregator_api_url[message.DESCRIPTOR.name]
        data = urllib.urlencode(postdata)
        defer_ = self._send_request('POST', url, data)

        # decode message
        if response_msg_type is not None:
            if isinstance(message, CheckAggregator):
                defer_.addCallback(self._decode, response_msg_type)
            elif isinstance(message, Login) or isinstance(message, LoginStep2):
                defer_.addCallback(self._decode, response_msg_type)
            else:
                defer_.addCallback(self._aes_decrypt, response_msg_type)

        defer_.addErrback(self._decode_errback)

        return defer_

    def _send_request(self, method, uri, data="", mimeType=None):
        g_logger.info("Sending message to aggregator at %s" % uri)
        headers = {}
        if mimeType:
            headers['Content-Type'] = mimeType
        if data:
            headers['Content-Length'] = str(len(data))
        d = client.getPage(uri, method=method, postdata=data,
                           headers=headers)
        d.addErrback(self._connection_errback)
        return d

    def _connection_errback(self, failure):
        g_logger.error("[AggregatorAPI] - %s" % failure)

        if isinstance(failure, error.ConnectError) or \
           isinstance(failure, error.DNSLookupError):
            g_logger.error("Connecting to the aggregator failed.")
            self.available = False
            theApp.statistics.aggregator_fail_num = \
                  theApp.statistics.aggregator_fail_num + 1

        try:
            failure.raiseException()
        except Exception, err:
            if isinstance(err, Error):
                g_logger.error(">>> The Aggregator had an Internal Error:")
                g_logger.error(err.response)
                self._alter_network_informaiton(err.response)
        
        #self._alter_network_informaiton(err.response)
        
    def _decode_errback(self, failure):
        g_logger.error("[AggregatorAPI] - Failed to decode. %s" % failure)

    def _handle_errback(self, failure):
        g_logger.error("Aggregator failure: %s" % str(failure))
    
    """ alters """
    #----------------------------------------------------------------------    
    def _alter_show(self,primary_text,secondary_text):
        #Add the user-friendly information to the user to check the problem.
        import gtk
        from higwidgets.higwindows import HIGAlertDialog

        alter = HIGAlertDialog(primary_text = primary_text,\
                                       secondary_text = secondary_text)
        
        alter.show()
        alter.run()

        #show login window again
        theApp.gtk_main.show_login()                
        
    def _alter_network_informaiton(self,failure):
        failure_info_first = None
        failure_info_second = None
        
        if 'error.NoRouteError' in str(failure):
            failure_info_first  = 'Disconnect to Internet'
            failure_info_second = 'Please check your network card connection!'
        elif 'TimeoutError' in str(failure):
            failure_info_first = 'Cloud Aggregator Server Connect Error'
            failure_info_second = 'Please check your cloud aggregator URL'         
        elif 'Agent matching query does not exist' in str(failure) :# or\
                           # '500 Internal Server Error' in str(failure) or\
                           # '500 INTERNAL SERVER ERROR' in str(failure):
            failure_info_first = _('Username/Password Error')
            failure_info_second = _('Please check your username or password')
            #clear username and password (there maybe some bugs here)
            theApp.peer_info.clear_db()
        else: 
            print str(failure)
            pass
        
        if failure_info_first == None and failure_info_second == None:
            return
        else:
            self._alter_show(primary_text = failure_info_first,secondary_text =failure_info_second)    


if __name__ == "__main__":
    import time
    api = AggregatorAPI()
    #api = AggregatorAPI('http://www.baidu.com')
    d = api.check_version()

    report = WebsiteReport()
    report.header.reportID = 'xw384kkre'
    report.header.agentID = '10000'
    report.header.testID = '1'
    report.header.timeZone = 8
    report.header.timeUTC = int(time.time())
    report.report.websiteURL = 'http://www.baidu.com'
    report.report.statusCode = 200

    #api.send_report(report)

    #api.register("test1", "test", "test@hotmail.com")

    from twisted.internet import reactor
    reactor.callLater(10, reactor.stop)
    reactor.run()
