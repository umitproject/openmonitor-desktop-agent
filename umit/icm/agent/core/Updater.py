#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Luis A. Bastiao Silva <luis.kop@gmail.com>
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



from umit.icm.agent.utils.FileDownloader import FileDownloader
from umit.icm.agent.Application import theApp
from umit.icm.agent.logger import g_logger


def download_update(url=None,check_code = None, version=None):
    """
    download and update 
    """
    downloader = FileDownloader(url,
                                os.path.join(TMP_DIR, "icm-agent_" + str(version) +".tar.gz"))
    if check_code == "" or check_code == None :
        check_code = 0;
    else:
        check_code = check_code
    
    downloader.addCallback(update_agent,
                           str(version),
                           check_code)
    downloader.start()

def auto_check_update(auto_upgrade=None):
   
    defer_ = theApp.aggregator.check_version()
    defer_.addCallback(handle_auto_check_update,auto_upgrade)
    defer_.addErrback(handle_auto_errback)
    return defer_


def handle_auto_check_update(message,auto_upgrade):
    """"""
    if message is None:
        return 
    
    if compare_version(str(message.versionNo),VERSION) == higher_version:
        g_logger.info("New version arrive in Check" ) 
        if auto_upgrade == False: 
            from umit.icm.agent.gui.Notifications import NotificationUpdate,new_release_mode,report_mode
            t = NotificationUpdate(mode=new_release_mode,text="test",timeout=15000)
        else:
            from umit.icm.agent.gui.Notifications import NotificationUpdate,auto_upgrade_mode,report_mode
            t = NotificationUpdate(mode=auto_upgrade_mode,text="test",timeout=30000)
            #software update automatically
            download_update(url=message.downloadURL,version=message.versionNo,check_code=None)
    else:
        g_logger.info("Current version is the newest in Check" ) 
  
def handle_auto_errback(failure):
    """"""
    g_logger.error("auto check error:%s" % str(failure))   

def insert_update_item_in_db(record):
    """"""
    sql_commit = "insert into updates (version,news_date,software_name, "\
                 "description, download_url, is_update, check_code ) "\
                 "values ('%s', '%s' , '%s', '%s','%s', '%s', '%s') " % \
                 (record["version"],
                  record["news_date"],
                  record["software_name"],
                  record["description"],
                  record["download_url"],
                  record["is_update"],
                  record["check_code"]) 
    print  sql_commit             
    g_db_helper.execute(sql_commit) 
    g_db_helper.commit()        
    g_logger.debug("insert a new record(%s) into updates of DB." % sql_commit)

def check_update_item_in_db(version):
    """"""
    rs = g_db_helper.select("select * from updates where version = '%s' " % version)
    if len(rs) == 0:
        return False
    else:
        return True
