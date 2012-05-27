#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Tianwei Liu <liutianweidlut@gmail.com>
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
import gtk
import os
import gobject

from deps.higwidgets.higwindows import HIGWindow
from deps.higwidgets.higdialogs import HIGDialog
from deps.higwidgets.higlabels import HIGLabel
from deps.higwidgets.higentries import HIGTextEntry
from deps.higwidgets.higtables import HIGTable
from deps.higwidgets.higboxes import HIGHBox, HIGVBox,hig_box_space_holder
from deps.higwidgets.higbuttons import HIGStockButton,HIGButton,HIGToggleButton
from deps.higwidgets.higprogressbars import HIGLabeledProgressBar

from umit.icm.agent.I18N import _
from umit.icm.agent.Global import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.BasePaths import *
from umit.icm.agent.logger import g_logger
from umit.icm.agent.Version import *

from umit.icm.agent.utils.FileDownloader import FileDownloader
from umit.icm.agent.Upgrade import *

from twisted.web import client
from twisted.web.error import Error
from twisted.internet import error

test_software_text=[
                    ('OpenMonitor','V0.1a','2011-9-1'),
                    ('icm-agent','V0.1b','2011-11-20'),
                    ('icm-agent LTS','V1.0','2012-5-21')] 
has_updated  = 1
no_updated   = 0

check_manually = 1
check_automatically = 2
check_idle = 0
update_check_method = check_idle

class SoftwareUpdateDialog(HIGWindow):
    """"""
    def __init__(self):
        """Constructor"""
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_("Open Monitor Software Update Manager"))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_size_request(480,480)
        self.set_keep_above(True)
        self.set_border_width(10)
        
        self._create_record()
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets() 

    
    def _create_record(self):
        
        self.software_list_dict = {}
        self.software_details_dict ={
                                     "version":"",
                                     "news_date":"",
                                     "software_name":"",
                                     "description":"",
                                     "download_url":"",
                                     "is_update":"",
                                     "check_code":""
                                     } 
        self.current_record = {}
        #get history update information
        self.latest_update_time =  "The lastest update time is " + self._get_value_from_db("update_time")
        
    def _create_widgets(self):
        """"""        
        #vbox
        self.all_box = HIGVBox()
        self.soft_update_info_box = HIGHBox()
        self.soft_update_list_box = HIGVBox()
        self.check_btn_box = gtk.HButtonBox()
        self.soft_update_detail_box = HIGVBox()
        self.bottom_btn_box = gtk.HButtonBox()
            
        #software update information title 
        self.update_icon = gtk.Image()
        self.update_icon.set_from_file(os.path.join(IMAGES_DIR,'software_update.ico'))
        self.version_information_label = HIGLabel(_("The newest open monitor in your computer!"))
        self.latest_time_information_label = HIGLabel(_(self.latest_update_time))
        self.soft_update_table = HIGTable()
             
        #software list
        self.column_names = ['Date','Version','Name']
        
        self.vbox_list = gtk.VBox(False,8)
        self.scroll_window_vbox = gtk.ScrolledWindow()
        self.scroll_window_vbox.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scroll_window_vbox.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.vbox_list.pack_start(self.scroll_window_vbox,True,True,0)
        self.store = gtk.ListStore(str,str,str)
        self.treeview = gtk.TreeView()

        self.treeview.set_rules_hint(True)
        self.treeview.set_sensitive(False)
        self.vbox_list.set_size_request(100,100)
        self.scroll_window_vbox.add(self.treeview)
              
        self._create_colums()
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0,'No update!')
        
        self.vbox_list.pack_start(self.statusbar,False,False,0)
        
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.progress_bar.set_fraction(0.0)
        
        self.vbox_list.pack_start(self.progress_bar,False,False,0)
        #button about the update
        self.check_btn = HIGButton(_("Check"))
        self.install_btn = HIGButton(_("Install"))
        self.install_btn.set_sensitive(False)
        
        #update details 
        self.detail_toggle_button = gtk.ToggleButton(_("Details"))
        self.detail_btn_box = gtk.HButtonBox()
        self.detail_btn_box.set_layout(gtk.BUTTONBOX_START)
        self.details_vbox = HIGVBox()
        self.details_scroll = gtk.ScrolledWindow()
        self.details_textview = gtk.TextView()
        self.details_textview.set_size_request(100,120)
        self.details_textview.set_editable(False)
        self.details_textview.set_buffer(self._set_details_content())
    
        #bottom button
        self.close_btn = HIGButton(_("Close"))
        self.settings_btn = HIGButton(_("Settings"))
        
    def _pack_widgets(self):
        """"""
        self.all_box._pack_noexpand_nofill(self.soft_update_info_box)
        self.all_box._pack_expand_fill(self.soft_update_list_box)   
        self.all_box._pack_noexpand_nofill(self.check_btn_box)
        self.all_box._pack_noexpand_nofill(self.soft_update_detail_box)    
        self.all_box._pack_noexpand_nofill(self.bottom_btn_box)        
        
        self.soft_update_info_box._pack_noexpand_nofill(hig_box_space_holder())
        self.soft_update_info_box._pack_expand_fill(self.soft_update_table)      
        self.soft_update_list_box._pack_expand_fill(self.vbox_list)
                 
        self.soft_update_table.attach_label(self.update_icon,0,2,0,2,)
        self.soft_update_table.attach_label(self.version_information_label,2,4,0,1)
        self.soft_update_table.attach_label(self.latest_time_information_label,2,4,1,2)
        
        self.check_btn_box.set_layout(gtk.BUTTONBOX_END)
        self.check_btn_box.set_spacing(8)       
        self.check_btn_box.pack_start(self.check_btn)
        self.check_btn_box.pack_start(self.install_btn)

        self.detail_btn_box.set_spacing(8)       
        self.detail_btn_box.pack_start(self.detail_toggle_button)
                
        self.details_scroll.add(self.details_textview)
        self.details_vbox._pack_expand_fill(self.details_scroll)
        self.soft_update_detail_box._pack_expand_nofill(self.detail_btn_box) 
        self.soft_update_detail_box._pack_expand_fill(self.details_vbox)         
        
        self.bottom_btn_box.set_layout(gtk.BUTTONBOX_EDGE)
        self.bottom_btn_box.set_spacing(8)  
        self.bottom_btn_box.pack_start(self.settings_btn)         
        self.bottom_btn_box.pack_start(self.close_btn)
        
        self.add(self.all_box)
        
    def _connect_widgets(self):
        """"""
        self.check_btn.connect('clicked',lambda w:self._check_software())
        self.install_btn.connect('clicked',lambda w:self._install_software())
        self.close_btn.connect('clicked',lambda w:self._close()) 
        self.settings_btn.connect('clicked',lambda w:self._settings_windows()) 
        self.detail_toggle_button.connect('clicked',lambda w:self._show_details())
        self.treeview.connect('row-activated',self._on_activated)

    def _load_updates(self):
        """
        load the information from the DB
        """
        self.software_list_dict = {}
        cnt = 0
        #get details from the DB 
        rs = g_db_helper.select("select * from updates where is_update = %d" % no_updated)
        for record in rs:
            self.software_list_dict[cnt] = {}
            self.software_list_dict[cnt]["version"] = record[0]
            self.software_list_dict[cnt]["news_date"] = record[1]
            self.software_list_dict[cnt]["software_name"] = record[2]
            self.software_list_dict[cnt]["description"] = record[3]
            self.software_list_dict[cnt]["download_url"] = record[4] 
            self.software_list_dict[cnt]["is_update"] = record[5]
            self.software_list_dict[cnt]["check_code"] = record[6]
                                                                       
            cnt = cnt + 1    
        g_logger.info("Loaded %d updates from DB." % len(rs))       
        
        #output in the window
        if len(self.software_list_dict) == 0:
            self.install_btn.set_sensitive(False)
            g_logger.info("No new updates from UpdateMoule")
        else:
            self.treeview.set_sensitive(True)
            self.check_btn.set_sensitive(False)
            g_logger.debug("Show the records in the tree-view") 

            self.store.clear()           
            for line in self.software_list_dict.keys():
                self.store.append([self.software_list_dict[line]["news_date"],
                                   self.software_list_dict[line]["version"],
                                   self.software_list_dict[line]["software_name"]])
            
            self.treeview.set_model(self.store) #It must be after the store update
                
    #def create_model(self):
    #    store = gtk.ListStore(str,str,str)
    #    for act in stress:
    #        store.append([act[0],act[1],act[2]])
    #    return store
    
    def _get_value_from_db (self,key):
        """
        get value from the config in DB
        """
        rs = g_db_helper.select("select * from config where key = '%s'" % key)
        if rs == None or len(rs) != 1:
            g_logger.error("Wrong get the value from key:%s in config DB " % (key))   
            return 
        return str(rs[0][1])
    
    def _set_details_content(self,content=None):
        if content == None or content == "":
            content = str(_('Open Monitor Alpha is coming soon!\n Designed by UMIT'))
           
        buf = gtk.TextBuffer()
        buf.set_text(content)
        return buf
    
    def _show_details(self):
        """"""
        if (self.detail_toggle_button.get_active()):
            self.details_vbox.hide_all()
        else:
            self.details_vbox.show_all()
                 
    def _create_colums(self):
        """"""       
        for i in range(0,len(self.column_names)):
            rendererText = gtk.CellRendererText()
            column = gtk.TreeViewColumn(self.column_names[i],rendererText,text = i) #text attributes MUST!
            column.set_sort_column_id(i)
            self.treeview.append_column(column)
    
    def _on_activated(self,widget,row,col):
        """"""
        self.install_btn.set_sensitive(True)
        #choice
        selection = self.treeview.get_selection()
        (model,iter) = selection.get_selected()
        if iter == None:
            return
        else:
            cur_version = self.store.get_value(iter,1)
            #fill self.current_record
            rs = g_db_helper.select("select * from updates where version = '%s'" % cur_version)
            if len(rs) != 1:
                g_logger.error("Record is ERROR in DB!!!! The window will be closed!!!")
                self.destroy()
            self.current_record = {}
            
            self.current_record["version"] = rs[0][0]
            self.current_record["news_date"] = rs[0][1]
            self.current_record["software_name"] = rs[0][2]
            self.current_record["description"] = rs[0][3]
            self.current_record["download_url"] = rs[0][4] 
            self.current_record["is_update"] = rs[0][5]
            self.current_record["check_code"] = rs[0][6]            
              
            
            self.statusbar.push(0,_("You have selected the %s version" % \
                                self.current_record["version"])) 
           
            self.details_textview.set_buffer(self._set_details_content(_(self.current_record["description"] + "\n" + 
                                        "download:"+self.current_record["download_url"] + "\n" +
                                        "Designed by Umit!" 
                                        ))) 
            self.details_textview.show_all()
            g_logger.debug("Selected the item %s" % (self.current_record))              
    
    def _check_software(self):    
        """"""
        defer_ = theApp.aggregator.check_version()
        defer_.addCallback(self._handle_check_software)
        defer_.addErrback(self._handle_errback)
        
        return defer_
    
    def _handle_check_software(self,message):
        if message == None:
            return
        
        g_logger.debug("Finish check the software update.")
        self.progress_bar.set_value(100)
        #self.progress_bar = gtk.ProgressBar(100)
        #show the record        
        self._load_updates()
        
    def _handle_errback(self,failure):
        g_logger.error("Aggregator failure: %s" % str(failure))        
        
    def _check_software_test(self):
        """"""
        p = theApp.aggregator.check_version()
        print p
        self.progress_bar.set_value(100)
        
        #test: create some records
        result = {
                1:{"version":"0.9",
                   "news_date":"2012-1-1",
                   "software_name":"icm-agent",
                   "description":"test software update module icm-agent",
                   "download_url":"http://tianwei-wordpress.stor.sinaapp.com/uploads/2012/05/icm_agent_update.tar.gz",
                   "is_update":"1"},
                2:{"version":"1.1",
                   "news_date":"2012-5-21",
                   "software_name":"open monitor desktop",
                   "description":"test software update module open monitor 1.0",
                   "download_url":"http://tianwei-wordpress.stor.sinaapp.com/uploads/2012/05/icm_agent_update.tar.gz",
                   "is_update":"0"},
                3:{"version":"2.0",
                   "news_date":"2012-8-21",
                   "software_name":"open monitor desktop v2.0",
                   "description":"test software update module open monitor 2.0",
                   "download_url":"http://tianwei-wordpress.stor.sinaapp.com/uploads/2012/05/icm_agent_update.tar.gz",
                   "is_update":"0"},
                }
        #check the db and insert it
        if len(result) == 0:
            self.install_btn.set_sensitive(False)
            g_logger.info("No new updates from UpdateMoule")
            return            
        
        for key in result.keys():
            if not check_update_item_in_db(result[key]["version"]):
                insert_update_item_in_db(result[key])
        
        #show the record        
        self._load_updates()
        
    def _install_software(self):
        """"""
        self.progress_bar.set_value(0)
        if self.current_record == None or len(self.current_record) == 0:
            self.install_btn.set_sensitive(False)
            g_logger.info("No new updates to be installed")
            return

        print self.current_record 
        # download and install 
        if compare_version(self.current_record["version"],VERSION) == higher_version:
            g_logger.debug("The version is right for icm-agent")
            if not os.path.exists(TMP_DIR):
                os.mkdir(TMP_DIR)
            downloader = FileDownloader(
                                        self.current_record["download_url"],
                                        os.path.join(TMP_DIR, "icm-agent_" + self.current_record["version"]+".tar.gz"))
            if self.current_record["check_code"] == "" or \
               self.current_record["check_code"] == None :
                check_code = 0;
            else:
                check_code = self.current_record["check_code"]
            
            downloader.addCallback(update_agent,
                                   self.current_record["version"],
                                   check_code)
            self.install_btn.set_sensitive(False)
            downloader.start()
        else:
            g_logger.debug("The version is low than current icm-agent")
            self.statusbar.push(0,'The current is the lastest version!')
            self.install_btn.set_sensitive(False)
            self.check_btn.set_sensitive(True)
   
    def _close(self):
        """"""
        self.destroy()
    def _settings_windows(self):
        """"""
        theApp.gtk_main.show_preference()
        
    def _auto_update(self):
        """"""
        pass
    def _manually_update(self):
        """"""
        pass

def auto_check_update():
   
    defer_ = theApp.aggregator.check_version()
    defer_.addCallback(handle_auto_check_update)
    defer_.addErrback(handle_auto_errback)
    return defer_

def handle_auto_check_update(message):
    """"""
    if message is None:
        return 
    
    if compare_version(str(message.versionNo),VERSION) == higher_version:
        g_logger.info("New version arrive in Check" )  
        from umit.icm.agent.gui.Notifications import Notifications,new_release_mode,report_mode
        t = Notifications(mode=new_release_mode,text="test",timeout=15000)
    else:
        g_logger.info("Current version is the newest in Check" ) 
  
def handle_auto_errback(failure):
    """"""
    failure.printTraceback()
    g_logger.error("auto check error:" % str(failure))   

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

if __name__ == "__main__":
    dialog =  SoftwareUpdateDialog()
    dialog.connect("delete-event", lambda x,y:gtk.main_quit())
    dialog.show_all()
    
    gtk.main()         
        
 