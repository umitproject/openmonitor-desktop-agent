#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
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

import locale

from umit.icm.agent.BasePaths import *

try:
    # If the content of the environment variable LANG contains a string which
    # represents a language or encoding not supported by the system, the 
    # following line will raise an exception.
    LC_ALL = locale.setlocale(locale.LC_ALL,'')
except locale.Error, error_msg:
    # Here we tell user that it's system is set to an unsupported language,
    # and that Umit will proceed using the system's default.
    # Latter, we call setlocale again, but now providing None as the second
    # argument, avoiding the occourrance of the exception.
    # Gtk will raise a warning in this case, but will work just perfectly.
    print "Your locale setting is not supported. OpenMonitor will continue using \
using your system's preferred language."
    LC_ALL = locale.setlocale(locale.LC_ALL, None)        

######################
#Selected the language
from umit.icm.agent.Global import *
LANG = None
ENC = None
language_text = g_config.get("Language","current_language")
if "English" in language_text:
    LANG = "en_US"
elif "Chinese" in language_text:
    LANG = "zh_CN"
elif "Portuguese" in language_text:
    LANG = "pt"
elif "Japanese" in language_text:
    LANG = "ja"
else:
    #system language
    LANG, ENC = locale.getdefaultlocale()

# If not correct locale could be retrieved, set en_US.utf8 as default
if ENC is None:
    ENC = "utf8"

if LANG is None or LANG == "":
    LANG = "en_US"   
       
#####################
#Install Language
import gettext
lang = gettext.translation("umit", LOCALES_DIR,languages=[LANG], fallback=True)
lang.install()
_ = lang.gettext

if __name__ == "__main__":
    print _("OpenMonitor")
    
    
    