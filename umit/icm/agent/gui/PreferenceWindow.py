#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
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

class PreferenceWindow(HIGWindow):
    """
    User Preference
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Preference'))
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        # Main widgets
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)
        self.main_vbox = HIGVBox()
        self.btn_box = gtk.HButtonBox()
        self.ok_button = gtk.Button(stock=gtk.STOCK_OK)
        self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)

        # notebook
        self.preference_vbox = HIGVBox()
        self.preference_notebook = gtk.Notebook()

        # Preference page
        self.pref_vbox = HIGVBox()
        self.pref_peerinfo_hbox = HIGHBox()
        self.pref_cloudagg_hbox = HIGHBox()
        self.pref_superpeers_hbox = HIGHBox()

        self.pref_peerinfo_section = HIGSectionLabel("Peer Info")
        self.pref_peerinfo_table = HIGTable()
        self.pref_cloudagg_section = HIGSectionLabel("Cloud Aggregator")
        self.pref_cloudagg_table = HIGTable()
        self.pref_cloudagg_subhbox = HIGHBox()
        self.pref_superpeers_section = HIGSectionLabel("Super Peers")
        self.pref_superpeers_table = HIGTable()

        self.pref_peerid_label = HIGEntryLabel("Peer ID:")
        self.pref_email_label = HIGEntryLabel("Email Address:")
        self.pref_peerid_label2 = HIGEntryLabel("peer id")
        self.pref_email_entry = gtk.Entry()
        self.pref_startup_check = gtk.CheckButton("Startup on the boot")
        self.pref_update_check = gtk.CheckButton("Automatically update plugins")

        self.pref_cloudagg_label = HIGEntryLabel("this is test")
        self.pref_cloudagg_button = HIGButton("change")
        self.pref_cloudagg_button.set_size_request(80, 28)

        self.pref_superpeers_entry = gtk.Entry()
        self.pref_superpeers_entry.set_size_request(200, 26)
        self.pref_superpeers_subhbox = HIGHBox()
        self.pref_btn_box = gtk.HButtonBox()
        self.pref_superpeers_button1 = HIGButton("add")
        self.pref_superpeers_button2 = HIGButton("show all")

        # Tests page
        self.tests_vbox = HIGVBox()
        self.tests_hbox1 = HIGHBox()
        self.tests_hbox2 = HIGHBox()
        self.tests_subbox = Tests()
        self.tests_hbox1.add(self.tests_subbox)
        self.tests_checkbtn = gtk.CheckButton("Update plugins automatically")

        #Feedback page
        self.feedback_vbox = HIGVBox()
        self.feedback_suggestion_hbox = HIGHBox()
        self.feedback_report_hbox = HIGHBox()

        self.feedback_suggestion_section = HIGSectionLabel(("Send Suggestion"))
        self.feedback_suggestion_table = HIGTable()
        self.feedback_report_section = HIGSectionLabel(("Bug Report"))
        self.feedback_report_table = HIGTable()

        self.feedback_suggestion_radiobtn1 = gtk.RadioButton(None, 'Website')
        self.feedback_suggestion_radiobtn1.set_active(True)
        self.feedback_suggestion_radiobtn2 = gtk.RadioButton(self.feedback_suggestion_radiobtn1, 'Service')
        #put these two radio button on a boutton box
        self.feedback_suggestion_bbox = gtk.HButtonBox()
        self.feedback_suggestion_entry = gtk.Entry()
        self.feedback_suggestion_sendbtn = HIGButton('Send')

        self.feedback_report_namelabel = HIGEntryLabel("Your Name:")
        self.feedback_report_nameentry = gtk.Entry()
        self.feedback_report_nameentry.set_size_request(100, 26)
        self.feedback_report_emaillabel = HIGEntryLabel("Email:")
        self.feedback_report_emailentry = gtk.Entry()
        self.feedback_report_emailentry.set_size_request(198, 26)
        self.feedback_report_subhbox1 = HIGHBox()

        self.feedback_report_sw = gtk.ScrolledWindow()
        self.feedback_report_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.feedback_report_textview = gtk.TextView()
        self.feedback_report_textbuffer = self.feedback_report_textview.get_buffer()
        self.feedback_report_textview.set_editable(True)
        self.feedback_report_textview.set_wrap_mode(True)
        self.feedback_report_textview.set_border_width(2)
        self.feedback_report_sw.add(self.feedback_report_textview)
        self.feedback_report_sw.show()
        self.feedback_report_textview.show()
        self.feedback_report_subhbox2 = HIGHBox()
        self.feedback_report_sendbtn = HIGButton('Send')
        self.feedback_report_subhbox3 = HIGHBox()

    def __pack_widgets(self):
        # Search Notebook
        self.preference_vbox._pack_expand_fill(self.preference_notebook)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.ok_button)
        self.btn_box.pack_start(self.apply_button)
        self.btn_box.pack_start(self.cancel_button)
        self.preference_vbox.pack_start(self.btn_box)
        #self.add(self.vbox)

        self.preference_notebook.set_border_width(1)
        self.preference_vbox.set_border_width(12)

        # Preference page
        self.pref_vbox.set_border_width(12)

        self.pref_vbox._pack_noexpand_nofill(self.pref_peerinfo_section)
        self.pref_vbox._pack_noexpand_nofill(self.pref_peerinfo_hbox)
        self.pref_vbox._pack_noexpand_nofill(self.pref_cloudagg_section)
        self.pref_vbox._pack_noexpand_nofill(self.pref_cloudagg_hbox)
        self.pref_vbox._pack_noexpand_nofill(self.pref_superpeers_section)
        self.pref_vbox._pack_noexpand_nofill(self.pref_superpeers_hbox)

        self.pref_peerinfo_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.pref_peerinfo_hbox._pack_expand_fill(self.pref_peerinfo_table)
        self.pref_cloudagg_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.pref_cloudagg_hbox._pack_expand_fill(self.pref_cloudagg_table)
        self.pref_superpeers_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.pref_superpeers_hbox._pack_expand_fill(self.pref_superpeers_table)

        self.pref_peerinfo_table.attach_label(self.pref_peerid_label, 0, 1, 0, 1)
        self.pref_peerinfo_table.attach_label(self.pref_email_label, 0, 1, 1, 2)

        self.pref_peerinfo_table.attach_label(self.pref_peerid_label2, 1, 2, 0, 1)
        self.pref_peerinfo_table.attach_entry(self.pref_email_entry, 1, 2, 1, 2)
        self.pref_peerinfo_table.attach_label(self.pref_startup_check, 0, 2, 2, 3)
        self.pref_peerinfo_table.attach_label(self.pref_update_check, 0, 3, 3, 4)

        self.pref_cloudagg_subhbox._pack_expand_fill(self.pref_cloudagg_label)
        self.pref_cloudagg_subhbox._pack_noexpand_nofill(self.pref_cloudagg_button)
        self.pref_cloudagg_table.attach_entry(self.pref_cloudagg_subhbox, 0, 1, 0, 1)

        self.pref_btn_box.set_layout(gtk.BUTTONBOX_END)
        self.pref_btn_box.set_spacing(8)
        self.pref_btn_box.pack_start(self.pref_superpeers_button1)
        self.pref_btn_box.pack_start(self.pref_superpeers_button2)
        self.pref_superpeers_subhbox._pack_expand_fill(self.pref_superpeers_entry)
        self.pref_superpeers_subhbox._pack_noexpand_nofill(self.pref_btn_box)
        self.pref_superpeers_table.attach_label(self.pref_superpeers_subhbox, 0, 1, 0, 1)

        self.preference_notebook.append_page(self.pref_vbox,
                                         gtk.Label("Preference"))

        #Test page
        #self.tests_hbox.set_border_width(12)
        self.tests_vbox.pack_start(self.tests_hbox1, True, True, 5)
        self.tests_vbox.pack_start(self.tests_hbox2, True, True, 5)

        self.tests_checkbtn.set_border_width(8)
        self.tests_hbox2.add(self.tests_checkbtn)
        self.preference_notebook.append_page(self.tests_vbox,
                                         gtk.Label("Tests"))

        #Feedback page
        self.feedback_vbox.set_border_width(12)

        self.feedback_vbox._pack_noexpand_nofill(self.feedback_suggestion_section)
        self.feedback_vbox._pack_noexpand_nofill(self.feedback_suggestion_hbox)
        self.feedback_vbox._pack_noexpand_nofill(self.feedback_report_section)
        self.feedback_vbox._pack_noexpand_nofill(self.feedback_report_hbox)

        self.feedback_suggestion_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.feedback_suggestion_hbox._pack_expand_fill(self.feedback_suggestion_table)
        self.feedback_report_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.feedback_report_hbox._pack_expand_fill(self.feedback_report_table)

        self.feedback_suggestion_bbox.set_layout(gtk.BUTTONBOX_START)
        self.btn_box.set_spacing(5)
        self.feedback_suggestion_bbox.pack_start(self.feedback_suggestion_radiobtn1)
        self.feedback_suggestion_bbox.pack_start(self.feedback_suggestion_radiobtn2)
        self.feedback_suggestion_table.attach_label(self.feedback_suggestion_bbox, 0, 1, 0, 1)
        self.feedback_suggestion_table.attach_entry(self.feedback_suggestion_entry, 0, 1, 1, 2)
        self.feedback_suggestion_table.attach(self.feedback_suggestion_sendbtn,
                                                    0, 1, 2, 3, gtk.PACK_START)

        self.feedback_report_subhbox1.pack_start(self.feedback_report_namelabel, True, True, 0)
        self.feedback_report_subhbox1.pack_start(self.feedback_report_nameentry, True, True, 0)
        self.feedback_report_subhbox1.pack_start(self.feedback_report_emaillabel, True, True, 0)
        self.feedback_report_subhbox1.pack_start(self.feedback_report_emailentry)
        self.feedback_report_table.attach(self.feedback_report_subhbox1, 0, 1, 0, 1)
        self.feedback_report_subhbox2.pack_start(self.feedback_report_sw)
        self.feedback_report_table.attach(self.feedback_report_subhbox2, 0, 1, 1, 2)
        self.feedback_report_subhbox3.pack_start(self.feedback_report_sendbtn)
        self.feedback_report_table.attach(self.feedback_report_subhbox3, 0, 1, 2, 3, gtk.PACK_START)

        self.preference_notebook.append_page(self.feedback_vbox,
                                         gtk.Label("Feedback"))

        self.hpaned.pack1(self.preference_vbox, True, False)

class PreferenceWindowA(gtk.HPaned, object):
    def __init__(self, notebook):
        gtk.HPaned.__init__(self)

        self._create_widgets()
        self._pack_widgets()
        #self._connect_events()

        self.parsed_results = {}
        #self._set_result_view()
        self.scan_num = 1
        self.id = 0
        self.notebook = notebook

    #def _connect_events(self):
        #self.os_osclass_combo.connect("changed", self.update_osmatch)
        #self.pref_email_entry.connect("focus-out-event",self.update_extension_entry)
        #self.pref_startup_check.connect("toggled", self.update_save_check)
        #self.pref_update_check.connect("toggled", self.update_search_check)
        ##1self.pref_path_entry.connect_entry_change(self.update_path_entry)
        #self.pref_savetime_entry.connect_entry_change(self.update_savetime_entry)

class Tests(gtk.VBox):
    def __init__(self):
        super(Tests, self).__init__()
        self.set_size_request(520, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("Installed Tests")

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 0, 1, 0, 1, gtk.FILL,
            gtk.FILL, 0, 0);

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        wins = gtk.TextView()
        textbuffer = wins.get_buffer()
        wins.set_editable(True)
        wins.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        wins.set_cursor_visible(True)
        wins.show()
        sw.add(wins)
        sw.show()
        #table.attach(wins, 0, 2, 1, 3, gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)
        table.attach(sw, 0, 1, 1, 3)
        updatebtn = gtk.Button("update")
        updatebtn.set_size_request(50, 30)
        table.attach(updatebtn, 0, 1, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK, 1, 1)

        vbox = gtk.VBox()
        btnbox = gtk.VButtonBox()
        btnbox.set_border_width(5)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btnbox.set_spacing(5)
        button = gtk.Button("add >>")
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button("add all")
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button("<< remove")
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button("remove all")
        button.set_size_request(50, 30)
        btnbox.add(button)
        table.set_row_spacing(1, 3)
        vbox.add(btnbox)
        table.attach(vbox, 3, 4, 1, 2, gtk.FILL, gtk.SHRINK, 1, 1)

        title = gtk.Label("Selected Tests")

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 4, 5, 0, 1, gtk.FILL,
            gtk.FILL, 0, 0);

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        wins2 = gtk.TextView()
        textbuffer = wins2.get_buffer()
        wins2.set_editable(True)
        wins2.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        wins2.set_cursor_visible(True)
        wins2.show()
        sw.add(wins2)
        sw.show()
        table.attach(sw, 4, 5, 1, 3)
        halign2 = gtk.Alignment(0, 1, 0, 0)
        self.add(table)


if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = PreferenceWindow()
    #wnd.set_size_request(520, 440)
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()