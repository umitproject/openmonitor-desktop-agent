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

import gtk
import sys

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higboxes import HIGSpacer, hig_box_space_holder
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp
from umit.icm.agent.Global import *
from umit.icm.agent.test import test_name_by_id
from umit.icm.agent.test import ALL_TESTS
from umit.icm.agent.utils.Startup import StartUP

###################################
#Feedback Page in Preference Window
class FeedbackPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()
        self.__set_values()

    def __create_widgets(self):
        self.suggestion_hbox = HIGHBox()
        self.report_hbox = HIGHBox()

        self.suggestion_section = HIGSectionLabel(_("Test Suggestion"))
        self.suggestion_table = HIGTable()
        self.report_section = HIGSectionLabel(_("Bug Report"))
        self.report_table = HIGTable()

        # Website Suggestion
        self.website_suggestion_table = HIGTable()
        self.website_suggestion_slabel = HIGSectionLabel(_("Website Suggestion"))
        self.website_url_subhbox = HIGHBox()
        self.website_url_label = HIGEntryLabel(_("URL:"))
        self.website_url_entry = gtk.Entry()
        self.website_suggestion_sendbtn = HIGButton(_('Send'))
        self.website_suggestion_sendbtn.set_size_request(60, 25)
        self.website_suggestion_sendbtn.connect(
            'clicked', lambda x: self.send_website_suggestion())
        # Service Suggestion
        self.service_suggestion_table = HIGTable()
        self.service_suggestion_slabel = HIGSectionLabel(_("Service Suggestion"))
        self.service_name_subhbox = HIGHBox()
        self.service_name_label = HIGEntryLabel(_("Name:"))
        self.service_list_store = gtk.ListStore(str)
        self.service_name_entry = gtk.ComboBoxEntry(self.service_list_store, 0)
        self.service_host_subhbox = HIGHBox()
        self.service_host_label = HIGEntryLabel(_("Hostname:"))
        self.service_host_entry = gtk.Entry()
        self.service_ip_subhbox = HIGHBox()
        self.service_ip_label = HIGEntryLabel(_("IP:"))
        self.service_ip_entry = gtk.Entry()
        self.service_port_label = HIGEntryLabel(_("PORT:"))
        self.service_port_entry = gtk.Entry()        
        self.service_suggestion_sendbtn = HIGButton(_('Send'))
        self.service_suggestion_sendbtn.set_size_request(60, 25)
        self.service_suggestion_sendbtn.connect(
            'clicked', lambda x: self.send_service_suggestion())

        self.report_namelabel = HIGEntryLabel(_("Your Name:"))
        self.report_nameentry = gtk.Entry()
        #self.report_nameentry.set_has_frame(True)
        self.report_nameentry.set_size_request(100, 26)
        self.report_emaillabel = HIGEntryLabel(_("Email:"))
        self.report_emailentry = gtk.Entry()
        self.report_emailentry.set_size_request(198, 26)
        self.report_subhbox1 = HIGHBox()

        self.report_sw = gtk.ScrolledWindow()
        self.report_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.report_textview = gtk.TextView()
        self.report_textbuffer = self.report_textview.get_buffer()
        self.report_textview.set_editable(True)
        self.report_textview.set_wrap_mode(True)
        self.report_textview.set_border_width(2)
        self.report_sw.add(self.report_textview)
        self.report_sw.show()
        self.report_textview.show()
        self.report_subhbox2 = HIGHBox()
        self.report_sendbtn = HIGButton(_('Send'))
        self.report_sendbtn.set_size_request(60, 25)
        self.report_sendbtn.connect('clicked', lambda x: self.send_bug_report())
        self.report_subhbox3 = HIGHBox()

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.suggestion_section)
        self._pack_noexpand_nofill(self.suggestion_hbox)
        self._pack_noexpand_nofill(self.report_section)
        self._pack_noexpand_nofill(self.report_hbox)

        #self.suggestion_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.suggestion_hbox._pack_expand_fill(self.suggestion_table)
        #self.report_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.report_hbox._pack_expand_fill(self.report_table)


        self.suggestion_hbox._pack_expand_fill(self.suggestion_table)
        #self.suggestion_hbox._pack_expand_fill(self.service_suggestion_table)

        self.suggestion_table.attach_label(self.website_suggestion_slabel,
                                           0, 2, 0, 1)
        self.suggestion_table.attach_label(self.website_url_label,
                                           0, 1, 1, 2)
        self.suggestion_table.attach_entry(self.website_url_entry,
                                           1, 2, 1, 2)
        self.suggestion_table.attach(self.website_suggestion_sendbtn,
                                     0, 2, 2, 3, gtk.PACK_START)

        self.suggestion_table.attach_label(self.service_suggestion_slabel,
                                           2, 4, 0, 1)
        self.suggestion_table.attach_label(self.service_name_label,
                                           2, 3, 1, 2)
        self.suggestion_table.attach_entry(self.service_name_entry,
                                           3, 4, 1, 2)
        self.suggestion_table.attach_label(self.service_host_label,
                                           2, 3, 2, 3)
        self.suggestion_table.attach_entry(self.service_host_entry,
                                           3, 4, 2, 3)
        self.suggestion_table.attach_label(self.service_ip_label,
                                           2, 3, 3, 4)
        self.suggestion_table.attach_entry(self.service_ip_entry,
                                           3, 4, 3, 4)
        self.suggestion_table.attach_label(self.service_port_label,
                                           2, 3, 4, 5)
        self.suggestion_table.attach_entry(self.service_port_entry,
                                           3, 4, 4, 5)        
        
        self.suggestion_table.attach(self.service_suggestion_sendbtn,
                                     2, 4, 5, 6, gtk.PACK_START)

        self.report_subhbox1.pack_start(self.report_namelabel, True, True, 0)
        self.report_subhbox1.pack_start(self.report_nameentry, True, True, 0)
        self.report_subhbox1.pack_start(self.report_emaillabel, True, True, 0)
        self.report_subhbox1.pack_start(self.report_emailentry)
        self.report_table.attach(self.report_subhbox1, 0, 1, 0, 1)
        self.report_subhbox2.pack_start(self.report_sw)
        self.report_table.attach(self.report_subhbox2, 0, 1, 1, 2)
        self.report_subhbox3.pack_start(self.report_sendbtn)
        self.report_table.attach(self.report_subhbox3, 0, 1, 2, 3, gtk.PACK_START)

    def __set_values(self):
        from umit.icm.agent.test import SUPPORTED_SERVICES
        for each in SUPPORTED_SERVICES:
            self.service_list_store.append([each])

    def send_website_suggestion(self):
        website_url = self.website_url_entry.get_text()
        if website_url == '':
            alert = HIGAlertDialog(message_format=_("Missing fields."),
                                   secondary_text=_("Please input all fields "
                                                    "for website suggestion."))
            alert.run()
            alert.destroy()
            return
        d = theApp.aggregator.send_website_suggestion(website_url)
        d.addCallback(self.show_result)

    def send_service_suggestion(self):
        service_name = self.service_name_entry.child.get_text()
        host_name = self.service_host_entry.get_text()
        ip = self.service_ip_entry.get_text()
        port = int(self.service_port_entry.get_text())
        if service_name == '' or host_name == '' or ip == '' or port == "":
            alert = HIGAlertDialog(message_format=_("Missing fields."),
                                   secondary_text=_("Please input all fields "\
                                                    "for service suggestion."))
            alert.run()
            alert.destroy()
            return
        d = theApp.aggregator.send_service_suggestion(service_name, host_name, ip,port)
        d.addCallback(self.show_result)

    def send_bug_report(self):
        pass

    def show_result(self, result):
        if result is True:
            alert = HIGAlertDialog(message_format=_("Succuss."),
                                   secondary_text=_("Send to aggregaetor successfully."))
            alert.run()
            alert.destroy()
        else:
            alert = HIGAlertDialog(message_format=_("Error."),
                                   secondary_text=_("Send to aggregaetor failed."))
            alert.run()
            alert.destroy()
