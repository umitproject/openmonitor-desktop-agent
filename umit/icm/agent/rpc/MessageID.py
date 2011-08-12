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

from umit.icm.agent.rpc.messages_pb2 import *
from umit.icm.agent.rpc.messages_ext_pb2 import *


message_id_to_type = {
    2001: 'CheckAggregator',
    2002: 'CheckAggregatorResponse',
    2003: 'RegisterAgent',
    2004: 'RegisterAgentResponse',
    2005: 'Login',
    2006: 'LoginResponse',
    2007: 'Logout',
    2009: 'GetPeerList',
    2010: 'GetPeerListResponse',
    2011: 'GetSuperPeerList',
    2012: 'GetSuperPeerListResponse',
    2013: 'GetEvents',
    2014: 'GetEventsResponse',
    2015: 'SendWebsiteReport',
    2016: 'SendReportResponse',
    2017: 'SendServiceReport',
    2019: 'NewVersion',
    2020: 'NewVersionResponse',
    2021: 'NewTests',
    2022: 'NewTestsResponse',
    2023: 'UpgradeToSuper',
    2024: 'UpgradeToSuperResponse',
    2025: 'SendPrivateKey',
    2026: 'SendPrivateKeyResponse',
    2027: 'WebsiteSuggestion',
    2028: 'TestSuggestionResponse',
    2029: 'ServiceSuggestion',
    4001: 'AgentUpdate',
    4002: 'AgentUpdateResponse',
    4003: 'TestModuleUpdate',
    4004: 'TestModuleUpdateResponse',
    4005: 'ForwardingMessage',
    4006: 'ForwardingMessageResponse',
    5001: 'AuthenticatePeer',
    5002: 'AuthenticatePeerResponse',
    5003: 'P2PGetSuperPeerList',
    5004: 'P2PGetSuperPeerListResponse',
    5005: 'P2PGetPeerList',
    5006: 'P2PGetPeerListResponse',
    6001: 'Diagnose',
    6002: 'DiagnoseResponse',
    6003: 'WebsiteReport',
    6004: 'ServiceReport',
}

message_type_to_id = {
    'AgentUpdate': 4001,
    'AgentUpdateResponse': 4002,
    'AuthenticatePeer': 5001,
    'AuthenticatePeerResponse': 5002,
    'CheckAggregator': 2001,
    'CheckAggregatorResponse': 2002,
    'Diagnose': 6001,
    'DiagnoseResponse': 6002,
    'ForwardingMessage': 4005,
    'ForwardingMessageResponse': 4006,
    'GetEvents': 2013,
    'GetEventsResponse': 2014,
    'GetPeerList': 2009,
    'GetPeerListResponse': 2010,
    'GetSuperPeerList': 2011,
    'GetSuperPeerListResponse': 2012,
    'Login': 2005,
    'LoginResponse': 2006,
    'Logout': 2007,
    'NewTests': 2021,
    'NewTestsResponse': 2022,
    'NewVersion': 2019,
    'NewVersionResponse': 2020,
    'P2PGetPeerList': 5005,
    'P2PGetPeerListResponse': 5006,
    'P2PGetSuperPeerList': 5003,
    'P2PGetSuperPeerListResponse': 5004,
    'RegisterAgent': 2003,
    'RegisterAgentResponse': 2004,
    'SendPrivateKey': 2025,
    'SendPrivateKeyResponse': 2026,
    'SendReportResponse': 2016,
    'SendServiceReport': 2017,
    'SendWebsiteReport': 2015,
    'ServiceReport': 6004,
    'ServiceSuggestion': 2029,
    'TestModuleUpdate': 4003,
    'TestModuleUpdateResponse': 4004,
    'TestSuggestionResponse': 2028,
    'UpgradeToSuper': 2023,
    'UpgradeToSuperResponse': 2024,
    'WebsiteReport': 6003,
    'WebsiteSuggestion': 2027,
}

message_creator = {
    'AgentUpdate': AgentUpdate,
    'AgentUpdateResponse': AgentUpdateResponse,
    'AuthenticatePeer': AuthenticatePeer,
    'AuthenticatePeerResponse': AuthenticatePeerResponse,
    'CheckAggregator': CheckAggregator,
    'CheckAggregatorResponse': CheckAggregatorResponse,
    'Diagnose': Diagnose,
    'DiagnoseResponse': DiagnoseResponse,
    'ForwardingMessage': ForwardingMessage,
    'ForwardingMessageResponse': ForwardingMessageResponse,
    'GetEvents': GetEvents,
    'GetEventsResponse': GetEventsResponse,
    'GetPeerList': GetPeerList,
    'GetPeerListResponse': GetPeerListResponse,
    'GetSuperPeerList': GetSuperPeerList,
    'GetSuperPeerListResponse': GetSuperPeerListResponse,
    'Login': Login,
    'LoginResponse': LoginResponse,
    'Logout': Logout,
    'NewTests': NewTests,
    'NewTestsResponse': NewTestsResponse,
    'NewVersion': NewVersion,
    'NewVersionResponse': NewVersionResponse,
    'P2PGetPeerList': P2PGetPeerList,
    'P2PGetPeerListResponse': P2PGetPeerListResponse,
    'P2PGetSuperPeerList': P2PGetSuperPeerList,
    'P2PGetSuperPeerListResponse': P2PGetSuperPeerListResponse,
    'RegisterAgent': RegisterAgent,
    'RegisterAgentResponse': RegisterAgentResponse,
    'SendPrivateKey': SendPrivateKey,
    'SendPrivateKeyResponse': SendPrivateKeyResponse,
    'SendReportResponse': SendReportResponse,
    'SendServiceReport': SendServiceReport,
    'SendWebsiteReport': SendWebsiteReport,
    'ServiceReport': ServiceReport,
    'ServiceSuggestion': ServiceSuggestion,
    'TestModuleUpdate': TestModuleUpdate,
    'TestModuleUpdateResponse': TestModuleUpdateResponse,
    'TestSuggestionResponse': TestSuggestionResponse,
    'UpgradeToSuper': UpgradeToSuper,
    'UpgradeToSuperResponse': UpgradeToSuperResponse,
    'WebsiteReport': WebsiteReport,
    'WebsiteSuggestion': WebsiteSuggestion,
}

