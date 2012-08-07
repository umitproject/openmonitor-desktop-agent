#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors:  tianwei liu <liutianweidlut@gmail.com>

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

import os,sys
import subprocess
import time
import socket
import re
import platform
from umit.icm.agent.logger import g_logger

class tracerouteInfomation():
    """
    """
    def __init__(self):
        """
        """
        self.os_name = platform.system()

    def create_sockets(self,ttl):
        """
        Simulate the traceroute and tracert process
        We should need a receiving socket and a sending socket in every request        
        """
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, self.udp)
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.icmp)
        send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, ttl)
        
        return recv_socket, send_socket
    
    
    def traceroute(self, target_name , max_hops = 30,port = 33445):
        """
        """
        result = {}
        result["target"] = target_name
        result["hops"] = max_hops
        result["packetsize"] = 60       #in default
        result["trace"] = []
        
        #####
        #Init 
        self.randrom_port = 0
        self.recv_bytes = 16
        
        self.icmp = socket.getprotobyname('icmp')
        self.udp  = socket.getprotobyname('udp')
        
        ###########################################
        #simulate the traceroute or tracert process
        try: 
            dest_addr = socket.gethostbyname(target_name)
        except:
            print "Please check your network connections!!!"
            return result
        
        ttl = 1     #We will set the ttl from 1 -> max_hops (default: 1 -30)
        
        while True:
            #print "start: --> "
            ############
            #socket init
            start_time = time.time()
            recv_socket, send_socket = self.create_sockets(ttl)
            recv_socket.bind(("",port))
            send_socket.sendto("",(target_name,port))
            curr_addr = None
            
            try:
                _, curr_addr = recv_socket.recvfrom(self.recv_bytes)
                curr_addr = curr_addr[0]    #IP address
            except socket.error:
                pass
            finally:
                recv_socket.close()
                send_socket.close()   
            
            end_time = time.time()
            
            #################
            #store the result
            trace = {}
            trace["hop"] = int(ttl)
            trace["ip"] = str(curr_addr if curr_addr !=None else "")
            trace["packetsTiming"] = int((end_time - start_time)*1000.0)   #ms 
            
            #print trace
            result["trace"].append(trace)
            
            ttl += 1
            if curr_addr == dest_addr or ttl > max_hops:
                break
            
        
        ##################
        #result statistics
        result["hops"] = (ttl-1) if ttl <= max_hops else max_hops  
                    
        return result
        
        
    def traceroute_system(self,target_name,max_hops = 30):
        """
        Get traceroute inforamtion in Linux and Mac Platform
        """
        if target_name.startswith("http://") or target_name.startswith("https://"):
            target_name = target_name.split("://")[1].rstrip("/")
        
        result = {}
        result["target"] = "0.0.0.0"      
        result["packetsize"] = 60   #in default
        result["trace"] = []
        result["hops"] = 30
        
        ttl = 1
        
        if self.os_name == "Windows":
            command_name = "tracert"
        elif self.os_name == "Linux" or  self.os_name == "Darwin":
            command_name = "traceroute"
        else:
            print "Sorry, the current desktop agent cannot support this platform!"
        
        p = subprocess.Popen([command_name,target_name],\
                             stdout = subprocess.PIPE,\
                             stderr = subprocess.STDOUT)
        
        while True:
            line = p.stdout.readline()
            if not line:
                break
            
            g_logger.debug("[Traceroute]" + line)
            
            #######################
            #get first number: hops
            try:
                ttl = int(line.strip(" ").split(" ")[0])
            except:
                continue
            
            ###############
            #get ip address
            curr_addr = re.findall("(?:\d{1,3}\.){3}\d{1,3}", line)
            if curr_addr != []:
                curr_addr = curr_addr[0]
            else:
                curr_addr = None
                
            ###############
            #Get time in ms
            curr_time = re.findall("(\d+)(\.){0,1}(\d*) ms",line)
            if curr_time == []:
                curr_time = [(0,),(0,),(0,)]
            #print curr_time
            #################
            #store the result
            trace = {}
            trace["hop"] = ttl
            trace["ip"] = str(curr_addr if curr_addr !=None else "")
            print trace["ip"]
            trace["packetsTiming"] = []
            
            for item in curr_time:
                trace["packetsTiming"].append(int(item[0]))
            
            result["trace"].append(trace)
            
        p.wait()
        
        ##################
        #result statistics        
        result["hops"] = ttl if ttl <= max_hops else max_hops 
        
        ##########
        #DNS Parse
        try:
            resultAddr = socket.getaddrinfo(target_name, None)
            result["target"] = str(resultAddr[0][4][0])
        except socket.herror,e:
            g_logger.debug("Notice:Cannot resolve host ip, we will fill '0.0.0.0'")
            pass
            
        g_logger.debug(result)
        return result
    
    
if __name__ == "__main__":
    t = tracerouteInfomation()
    result = t.traceroute_system(target_name ="www.google.com")
    print result
    
