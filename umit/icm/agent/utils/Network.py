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

import re
import urllib2
from socket import socket, SOCK_DGRAM, AF_INET

local_ip_url = "www.google.com"
internet_ip_url = "http://myip.eu/"

def get_local_ip():
     try:
          s = socket(AF_INET, SOCK_DGRAM)
          s.connect((local_ip_url, 0))
          ip = s.getsockname()[0]
          return ip
     except:
          print("Failed to get local ip.")

def get_internet_ip():
     try:
          content = urllib2.urlopen(internet_ip_url).read()
          ip = re.search('\d+\.\d+\.\d+\.\d+', content).group(0)
          return ip
     except:
          print("Failed to get internet ip.")
