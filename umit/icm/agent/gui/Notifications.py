#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
#
# Author:  Tianwei Liu <liutianweidlut@gmail.com>
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
"""
notifications about new software released, system information etc
"""
import gtk
import gobject
import os

from higwidgets.higboxes import hig_box_space_holder
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Application import theApp
from umit.icm.agent.logger import g_logger
from umit.icm.agent.I18N import _

new_release_mode = 1
report_mode = 2
auto_upgrade_mode = 3

URGENT_MSG      = "urgent"
TASK_DOWN_MSG   = "task_download"
TASK_ASSIGN_MSG = "task_assign"
REPORT_MSG      = "report_upload"
SYS_MSG         = "system"

class NotificationUpdate(gtk.Window):
    """
    Software update notification window 
    """
    def __init__(self,mode=new_release_mode,text=None,timeout=10000):
        gtk.Window.__init__(self,gtk.WINDOW_POPUP)
        
        self.mode = mode
        self.text = text
        self.timeout = timeout
        
        self.screen_x = 0
        self.screen_y = 0
        
        self.__create_widgets()
        self.__pack_widgets()
        self.__connect_widgets()
        
        g_logger.info(_("new desktop agent version released! "))
        
    def __create_widgets(self):
        """"""
        if self.mode == new_release_mode:
            self.image = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_DIR,'new_release.png'))
            self.pixmap, self.mask = self.image.render_pixmap_and_mask()
            width,height = self.pixmap.get_size()
        elif self.mode == auto_upgrade_mode:
            self.image = gtk.gdk.pixbuf_new_from_file(os.path.join(IMAGES_DIR,'auto_update.png'))
            self.pixmap, self.mask = self.image.render_pixmap_and_mask()
            width,height = self.pixmap.get_size()            
        else:
            width = 200
            height = 200
            self.pixmap = None
        
        self.set_events(self.get_events() | gtk.gdk.BUTTON_PRESS_MASK)
        
        screen = gtk.gdk.Screen()
        self.screen_x = gtk.gdk.Screen.get_width(screen)
        self.screen_y = gtk.gdk.Screen.get_height(screen) 
        
        #win or linux different position
        if os.name == "nt":
            self.move(self.screen_x - width- 30 ,self.screen_y - 40 - height)  
        else:
            self.move(self.screen_x - width- 30 ,30) 
        self.set_app_paintable(True)
        self.set_size_request(width,height)
        self.set_resizable(False)
        self.realize()
        
        self.fixed = gtk.Fixed()
        self.fixed.set_size_request(width,height)
        self.vbox = gtk.VBox()
        self.hbox = gtk.HBox()
        
        self.label = gtk.Label(self.text)
            
    def __pack_widgets(self):
        """"""
        self.hbox.pack_end(self.label,False,False)
        self.hbox.pack_end(hig_box_space_holder(),True,False)
        
        self.vbox.pack_start(self.hbox,True,False)
        
        self.fixed.put(self.vbox,0,0)
        self.add(self.fixed)
        self.set_background(self, None, self.mask, self.pixmap)
        self.shape_combine_mask(self.mask,0,0)
        self.show_all()
        
        gobject.timeout_add(self.timeout,self.destroy)
    
    def __connect_widgets(self):
        """"""
        self.connect("expose-event",self.set_background,self.mask,self.pixmap)
        self.connect("delete_event",self.destory)
        if self.mode == new_release_mode:
            self.connect("button_press_event",self._navigator_to_update)       
            
    def _navigator_to_update(self, widget, event, data=None):
        """"""
        theApp.gtk_main.show_software_update()
        self.destory()
    
    def destory(self):
        """"""
        gtk.Window.destroy(self)
        return False

    def set_background(self, widget, event, mask, pixmap):
        """"""
        if self.window is not None:
            self.window.set_back_pixmap(pixmap, False)
        else:
            gobject.idle_add(self.set_bg, widget, event, mask, pixmap)          

class NotificationBase(object):
    def __init__(self):
        pass
    def notifyMessage(self):
        raise Exception("Need to implement this interface")
    def close(self):
        raise Exception("Need to implement this interface")
    def stop(self):
        raise Exception("Need to implement this interface")
    def updateForFailed(self):
        raise Exception("Need to implement this interface")                

class Notification():
    """
    """
    def __init__(self):
        self.notify = None
        import platform
        
        if platform.system() == "Linux":
            self.notify = Notification_linux()
        elif platform.system() == "Windows":
            self.notify = Notification_windows()
        elif platform.system() == "Darwin":
            self.notify = Notification_mac()
    
    def notify(self,messages):
        self.notify.notifyMessage(messages)
        
    def failed(self):
        self.notify.updateForFailed()
        
    def close(self):
        self.notify.close()
        
    def stop(self):
        self.notify.stop()
    


class notifyMessageMeta():
    """
    the basic meta of notify message
    """
    def __init__(self):
        self.id = None
        self.title = None
        self.text = None
        self.icon = None

class Notification_linux(NotificationBase):
    """
    Text Notification for Linux
    """
    def __init__(self):
        import pynotify
        
        if not pynotify.init("ICM-agent notifier"):
            raise Exceprion("Could not initialize notification service")
        

        self.urgent_icon = os.path.join(IMAGES_DIR,'urgent.png')
        self.task_download_icon = os.path.join(IMAGES_DIR,'task_assigned_download.png')
        self.task_assign_icon = os.path.join(IMAGES_DIR,'task_recurring.png')
        self.report_upload_icon = os.path.join(IMAGES_DIR,'task_assigned_to.png')
        self.system_icon = os.path.join(IMAGES_DIR,'system.png')
        
        self.icons = {
                      "urgent":self.urgent_icon,
                      "task_download":self.task_download_icon,
                      "task_assign":self.task_assign_icon,
                      "report_upload":self.report_upload_icon,
                      "system":self.system_icon
                      }
        #Add more ...  
        
        
        self.notify = pynotify.Notification('ICM-Agent Notifier','Show status of your icm-agent client') 
        self.notify.set_urgency(pynotify.URGENCY_NORMAL)
 
        self.message_cache = {}       
        self.message = None
        self.currentIndex = 0
        self.disable_notification = False
        self.presenting = False
    
    def notifyMessage(self,message):
        """
        Notification Message Interface
        """
        if self.presenting:
            return #we have already presenting message to the user
        
        disable_notifications = g_config.getboolean('application', 'disable_notifications')
        
        if not disable_notifications:
            self.presenting = True
            
            self.message = self.cache_message(message)
            
            self.currentIndex = 0
            self._show_current()
            
            #Add timeout set in config
            timeout = g_config.getint('notify', 'time_out')
            gobject.timeout_add (timeout,self._next_message)

    def updateForFailed(self):
        self.notify.set_timeout(5000)
        self.notify.update('Error in icm-agent!',
                           'Please check log file to find the reason',
                           self.urgency_icon)
        self.notify.show()
        if self.presenting:
            self.stop()
    
    def _next_message(self):
        disable_notifications = g_config.getboolean('application', 'disable_notifications')
        if disable_notifications:
            self.presenting = False
            return False
        else:
            self.currentIndex += 1
            if self.currentIndex >= len(self.message):
                self.notify.clear_actions()
                self.presenting = False
                return False
            else:
                self._show_current()
            return True
        
    def _show_current(self):
        """
        """
        if self.message:
            msg = self.message[self.currentIndex].title
            text = self.message[self.currentIndex].text
            icon = self.message[self.currentIndex].icon
            
            timeout = g_config.getint('notify', 'time_out')
            self.notify.set_timeout(timeout + 1000)
                        
            if self.notify.update(msg,"",self.icons[icon]):
                to = timeout
                self.notify.set_timeout(to + 1000)
                self.notify.show()
    
    def cacheMessage(self,message):
        """
        check every message
        """
        ret = []
        
        #unmark all messge 
        for k in self.message_cache.keys():
            self.message_cache[k] = False
            
        #mark all known and new message
        for m in message:
            if not self.message_cache.has_key(m.id):
                ret.append(m)
            
            self.message_cache[m.id] = True
        
        for k in self.message_cache.keys():
            if not self.message_cache[k]:
                del self.message_cache[k]
        
        return ret
    
    def stop(self):
        if self.notify:
            self.notify.close()
    
    def clearCache(self):
        self.message_cache.clear()
        
    def close(self):
        self.notify.close()

class Notification_windows(NotificationBase):
    def __init__(self):
        pass
    def notifyMessage(self):
        pass 
    def close(self):
        pass 
    def updateForFailed(self):
        pass                
    def stop(self):
        pass
    
class Notification_mac(NotificationBase):
    def __init__(self):
        pass
    def notifyMessage(self):
        pass 
    def close(self):
        pass  
    def updateForFailed(self):
        pass                 
    def stop(self):
        pass       
    
if __name__ == "__main__":
    t = NotificationUpdate(mode=new_release_mode,text="test",timeout=3000)
    gtk.main()
    
    