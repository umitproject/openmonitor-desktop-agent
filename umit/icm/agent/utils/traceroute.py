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
import re
import socket
import struct

def tracerouteInfomation(object):
    """
    """
    def __init__(self):
        """
        """
        self.randrom_port = 0
        self.recv_bytes = 512
        
        self.icmp = socket.getprotobyname('icmp')
        self.udp  = socket.getprotobyname('udp')
        
    def create_sockets(self,ttl):
        """
        Simulate the traceroute and tracert process
        We should need a receiving socket and a sending socket in every request        
        """
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, self.udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        return recv_socket, send_socket
    
    
    def traceroute(self, target_name , max_hops = 30,port = 33445):
        """
        """
        result = {}
        result["target"] = target_name
        result["hops"] = max_hops
        result["packetsize"] = 60       #in default
        result["trace"] = []
        
        #simulate the traceroute or tracert process
        try: 
            dest_addr = socket.gethostbyname(target_name)
        except:
            print "Please check your network connections!!!"
            return result
        
        ttl = 1     #We will set the ttl from 1 -> max_hops (default: 1 -30)
        
        while True:
            ############
            #socket init
            start_time = time.clock()
            recv_socket, send_socket = self.create_sockets(ttl)
            recv_socket.bind(("",self.randrom_port))
            send_socket.sendto("",(target_name,self.randrom_port))
            curr_addr = None
            
            try:
                _, curr_addr = recv_socket.recvfrom(self.recv_bytes)
                curr_addr = curr_addr[0]    #IP address
            except socket.error:
                pass
            finally:
                recv_socket.close()
                send_socket.close()   
            
            end_time = time.clock()
            
            #################
            #store the result
            trace = {}
            trace["hop"] = int(ttl)
            trace["ip"] = str(curr_addr if curr_addr !=None else "")
            trace["packetsTiming"] = int((end_time - start_time)*1000)   #ms 
            
            print trace
            result["trace"].append(trace)
            
            ttl += 1
            if curr_addr == dest_addr or ttl > max_hops:
                break
            
        
        ##################
        #result statistics
        result["hops"] = ttl if ttl <= max_hops else max_hops  
                    
        return result
        
        
    def traceroute_system(self,target):
        """
        Get traceroute inforamtion in Linux and Mac Platform
        """
        result = {}
        result["target"] = target
        result["hops"] = 30         #in default
        result[""]
        
        p = subprocess.Popen(["traceroute",target],
                             stdout = subprocess.PIPE,
                             stderr = subprocess.STDOUT)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            print "-->",line
            
            
        p.wait()
         
        print "finish Traceroute"
    
    
if __name__ == "__main__":
    t = tracerouteInfomation()
    result = t.traceroute(target ="www.baidu.com")
    print result
    
