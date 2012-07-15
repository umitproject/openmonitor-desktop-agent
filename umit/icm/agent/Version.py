#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Zhongjie Wang <wzj401@gmail.com>
#          Tianwei Liu <liutianweidlut@gmail.com>
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

from umit.icm.agent.Global import *

VERSION = g_db_helper.get_information(key='version',default="Dev")
VERSION_NUM = int(g_db_helper.get_information(key='version_num',default="1"))

higher_version = 1
lower_version  = -1
equal_version  = 0

def compare_version(ver1, ver2):
    #filter meaningless '0' ‘.’
    ver1 = ver1.rstrip('0').rstrip('.')
    ver2 = ver2.rstrip('0').rstrip('.')   
     
    array1 = ver1.split('.')
    array2 = ver2.split('.')
    i = 0
    for i in range(min(len(array1), len(array2))):
        if array1[i] > array2[i]:
            return higher_version
        elif array1[i] < array2[i]:
            return lower_version
    
    #Add '1' compare '1.1'
    if len(array1) < len(array2):
        return lower_version
    elif len(array1) > len(array2):
        return higher_version
    else:
        return equal_version

if __name__ == "__main__":
    print compare_version('1.0','1.1')
    print compare_version('1','1.1')
    print compare_version('1','0.9')
    print compare_version('1','1')
    print compare_version('1','1.0')
    print compare_version('1.....','1....0')
