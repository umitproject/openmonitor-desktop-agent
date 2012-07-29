#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Adriano Monteiro Marques
#
# Authors:  Tianwei Liu <liutianweidlut@gmail.com>
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
Auto Starts: Windows(Regedit),Linux(Bash),OSX()
"""
import os,sys,platform


from umit.icm.agent.logger import g_logger
from umit.icm.agent.BasePaths import *
from umit.icm.agent.Global import *

class StartUP(object):
    def __init__(self):
        self.os_name = platform.system()  
        self._load()

    def _load(self):
   
        if self.os_name == 'Windows':
            self.regedit_path =  r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            self.exe_path = str(BIN_DIR)
            self.key_name = "icmagent"
        elif self.os_name == 'Linux':
            self.home_path = os.path.expanduser('~')
            self.auto_sys_path = os.path.join(self.home_path,'.config/autostart/')
            self.desktop_name = 'icm-agent.desktop'
            self.auto_desktop_file = os.path.join(DESKTOP_DIR,self.desktop_name)
        elif self.os_name == 'Darwin':
            pass
        
    def set_startup(self):
        if self.os_name == 'Windows':
            self._win_set()
        elif self.os_name == 'Linux':
            self._linux_set()
        elif self.os_name == 'Darwin': #need to test
            self._mac_set()
            
    def clear_startup(self):
        if self.os_name == 'Windows':
            self._win_clear()
        elif self.os_name == 'Linux':
            self._linux_clear()
        elif self.os_name == 'Darwin': #need to test
            self._mac_clear()
        
    def _win_set(self):
        import _winreg as Regedit
        regedit = Regedit.ConnectRegistry(None,Regedit.HKEY_LOCAL_MACHINE)
        try:
            tag = self.regedit_path
            key = Regedit.OpenKey(regedit,tag,0,Regedit.KEY_WRITE)
            try:
                try:
                    Regedit.SetValueEx(key,
                                       self.key_name,
                                       0,
                                       Regedit.REG_SZ,
                                       self.exe_path)
                    g_logger.info("Auto StartUP icm-agent in Windows (%s,%s,%s)" % (tag,self.key_name,self.exe_path))
                except EnvironmentError:
                    g_logger.error("Write Regedit key Error in Windows (%s,%s,%s)" % (tag,self.key_name,self.exe_path))
                    raise
            finally:
                Regedit.CloseKey(key)
        finally:
            Regedit.CloseKey(regedit)
            
    def _win_clear(self):
        import _winreg as Regedit
        regedit = Regedit.ConnectRegistry(None,Regedit.HKEY_LOCAL_MACHINE)
        try:
            tag = self.regedit_path
            key = Regedit.OpenKey(regedit,tag,0,Regedit.KEY_WRITE)
            try:
                try:
                    Regedit.SetValueEx(key,self.key_name,0,Regedit.REG_SZ,self.exe_path)                    
                    Regedit.DeleteValue(key,self.key_name)
                    g_logger.info("Cancel Auto StartUP")
                except EnvironmentError:
                    g_logger.error("Cancel Auto StartUP Error in Windows (%s,%s)" % (tag,self.key_name))
                    raise
            finally:
                Regedit.CloseKey(key)
        finally:
            Regedit.CloseKey(regedit)    
                
    def _linux_set(self):
        import shutil
        if  not os.path.exists(self.auto_sys_path):
            os.mkdir(self.auto_sys_path)
        try:
            shutil.copy(self.auto_desktop_file, self.auto_sys_path+self.desktop_name)
            g_logger.info("Auto StartUP icm-agent in Linux (%s,%s)" %(self.auto_desktop_file,self.auto_sys_path))
        except Exception,e:
            g_logger.error("[Failed]Auto StartUP icm-agent in Linux (%s,%s,%s)" % (self.auto_desktop_file,self.auto_sys_path,e) )
                      
    def _linux_clear(self):
        file = self.auto_sys_path + self.desktop_name
        if os.path.exists(file):
            try:
                os.remove(file)
                g_logger.info("Cancel Auto StartUP icm-agent in Linux (%s)" %(file)) 
            except Exception,e:
                g_logger.error("[Failed] Cancel Auto StartUP icm-agent in Linux  (%s)" %(file)) 
        else:
            g_logger.info("There are not desktop file in auto folder %s" %(file)) 
        
    def _mac_set(self):
        pass
    def _mac_clear(self):
        pass
    def _print_startup(self):
        pass
    def _win_print(self):
        pass
   
if __name__ == "__main__":
    s = StartUP()
    #s.set_startup()
    #s.clear_startup()
    
    
    












