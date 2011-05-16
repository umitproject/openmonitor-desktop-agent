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


import os
import sys

from umit.icm.tests.WebsiteTest import WebsiteTest
from umit.icm.tests.HTTPFetcher import HTTPFetcher

#----------------------------------------------------------------------
def Main():
    """
    The Main function 
    """
    CreateGUI();
    WaitForEnd();
    
#----------------------------------------------------------------------
def CreateGUI():
    """"""
    pass
    
#----------------------------------------------------------------------
def WaitForEnd():
    """"""
    pass    

if __name__ == "__main__":
    test = HTTPFetcher("http://www.baidu.com", "baidu.html")
    test.execute()
    