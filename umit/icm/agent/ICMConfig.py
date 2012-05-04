#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Zhongjie Wang <wzj401@gmail.com>
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
from ConfigParser import ConfigParser, DEFAULTSECT, NoOptionError, \
     NoSectionError

class ICMConfig(ConfigParser):
    filenames = None
    fp = None

    def __init__(self, filename):
        ConfigParser.__init__(self)
        filename = self.read(filename)
        if not filename:
            raise IOError("Read %s failed." % filename)

    #def get(self, section, option):
        #try:
            #result = ConfigParser.get(self, section, option)
            #return result
        #except NoOptionError:
            #return None
        #except NoSectionError:
            #return None

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)

        ConfigParser.set(self, section, option, value)
        self.save_changes()

    def read(self, filename):
        self.filenames = ConfigParser.read(self, filename)
        return self.filenames

    def readfp(self, fp, filename=None):
        ConfigParser.readfp(self, fp, filename)
        self.fp = fp
        self.filenames = filename

    def save_changes(self):
        if self.filenames:
            filename = None
            if isinstance(self.filenames, basestring):
                filename = self.filenames
            elif isinstance(self.filenames, list) and len(self.filenames) == 1:
                filename = self.filenames[0]
            else:
                raise Exception("Wrong filename %s" % self.filenames)
            self.write(open(filename, 'w'))
        elif self.fp:
            self.write(self.fp)

    def write(self, fp):
        '''Write alphabetically sorted config files'''
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)

            items = self._defaults.items()
            items.sort()

            for (key, value) in items:
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

        sects = self._sections.keys()
        sects.sort()

        for section in sects:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

'''class CrashSettingConf(object):
   
    #Crash Report Tools Settings
    
    def __init__(self):
        # Constructor Crash Report Conf 
        
        #self.parse = 
        self.section_name = "Crash_report"
        self.attributes = {}
    def create_section(self):
        print "creating general_setting section"
        self.parser.add_section(self.section_name)
        self.crash_report = True
    
    def boolean_sanity(self,attr):
        if attr == True or \
           attr == "True" or \
           attr == "true" or \
           attr == "1"    or \
           attr == "t":
            
            return 1
        
        return 0
        
    def _get_it(self,p_name,default):
        return self.parser.get(self.section_name, p_name, default)
    def _set_it(self,p_name,value):
        self.parser.set(self.section_name, p_name, value)
    #API
    def set_crash_report(self,crash):
        self._set_it("crash_report", self.boolean_sanity(crash))
    def get_crash_report(self):
        return self.boolean_sanity(self._get_it("crash_report", True))
        
        
    crash_report = property(get_crash_report, set_crash_report)   
'''        
        