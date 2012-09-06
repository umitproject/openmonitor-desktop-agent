#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Authors:  Zhongjie Wang <wzj401@gmail.com>
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


class FileConfig(ConfigParser):
    """
    A configuration class using file to persist.
    """
    file_names = None
    fp = None

    def __init__(self, file_name):
        ConfigParser.__init__(self)
        file_name = self.read(file_name)
        if not file_name:
            raise IOError("Read %s failed." % file_name)

    def get(self, section, option):
        try:
            result = ConfigParser.get(self, section, option)
            return result
        except NoOptionError:
            return None
        except NoSectionError:
            return None

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)

        ConfigParser.set(self, section, option, value)
        self.save_changes()

    def read(self, file_name):
        self.file_names = ConfigParser.read(self, file_name)
        return self.file_names

    def readfp(self, fp, file_name=None):
        ConfigParser.readfp(self, fp, file_name)
        self.fp = fp
        self.file_names = file_name

    def save_changes(self):
        if self.file_names:
            file_name = None
            if isinstance(self.file_names, basestring):
                file_name = self.file_names
            elif isinstance(self.file_names, list) and len(self.file_names) == 1:
                file_name = self.file_names[0]
            else:
                raise Exception("Wrong file name %s" % self.file_names)
            self.write(open(file_name, 'w'))
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

#---------------------------------------------------------------------
from umit.icm.agent.db import DBKVPHelper

class DBConfig(object):
    """
    A configuration class using database to persist.
    """

    #----------------------------------------------------------------------
    def __init__(self, db_path):
        """Constructor"""
        self.db_kvp_helper = DBKVPHelper('sqlite')
        self.connect(db_path)

    def connect(self, db_path):
        self.db_kvp_helper.connect(db_path)
        self.db_kvp_helper.use_table('config')

    def attach(self, db_conn):
        self.db_kvp_helper.attach(db_conn)
        self.db_kvp_helper.use_table('config')

    def get(self, section, key, default=None):
        db_key_name = section + '|' + key
        result = self.db_kvp_helper.read(db_key_name, default)
        if result:
            return result
        else:
            return default

    def getint(self, section, key, default=None):
        """To be compatible with FileConfig"""
        return int(self.get(self, section, key, default))

    def getfloat(self, section, key, default=None):
        """To be compatible with FileConfig"""
        return float(self.get(self, section, key, default))

    def getboolean(self, section, key, default=None):
        """To be compatible with FileConfig"""
        return bool(self.get(self, section, key, default))

    def set(self, section, key, value):
        db_key_name = section + '|' + key
        self.db_kvp_helper.write(db_key_name, value)

    def delete(self, section, key):
        db_key_name = section + '|' + key
        self.db_kvp_helper.delete(db_key_name)


def test_file_config():
    from umit.icm.agent.utils import CreateConf
    CreateConf.create_file_conf("test.conf")
    config = FileConfig("test.conf")
    config.set("info", "name", "ABC")
    config.set("info", "age", '10')
    config.set("info", "rate", '3.3')
    raw_input()
    print(config.get("info", "name"))
    print(config.get("info", "age"))
    print(config.get("info", "rate"))
    os.remove("test.conf")

def test_db_config():
    from umit.icm.agent.utils import CreateConf
    CreateConf.create_db_conf("test.db")
    config = DBConfig("test.db")

    config.set("info", "name", "ABC")
    config.set("info", "age", '10')
    config.set("info", "rate", '3.3')
    raw_input()
    print(config.get("info", "name"))
    print(config.get("info", "age"))
    print(config.get("info", "rate"))
    os.remove("test.db")

if __name__ == "__main__":
    test_file_config()
    #test_db_config()