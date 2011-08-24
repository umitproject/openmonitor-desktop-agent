#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#          Alan Wang <wzj401@gmail.com>
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


class PreferenceWindow(HIGWindow):
    """
    User Preference
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Preference'))
        self.__create_widgets()
        self.__pack_widgets()
        self.load_preference()

    def __create_widgets(self):
        # Main widgets
        self.hpaned = gtk.HPaned()
        self.add(self.hpaned)
        self.vbox = HIGVBox()
        self.btn_box = gtk.HButtonBox()
        self.ok_button = gtk.Button(stock=gtk.STOCK_OK)
        self.ok_button.connect('clicked', lambda x: self.clicked_ok())
        self.apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        self.apply_button.connect('clicked', lambda x: self.save_preference())
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', lambda x: self.destroy())
        # notebook
        self.notebook = gtk.Notebook()
        # Preference page
        self.pref_page = PreferencePage()
        self.notebook.append_page(self.pref_page, gtk.Label(_("Preference")))
        # Tests page
        self.test_page = TestPage()
        self.notebook.append_page(self.test_page, gtk.Label(_("Tests")))
        # Feedback page
        self.feedback_page = FeedbackPage()
        self.notebook.append_page(self.feedback_page, gtk.Label(_("Feedback")))

    def __pack_widgets(self):
        # Search Notebook
        self.vbox._pack_expand_fill(self.notebook)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.ok_button)
        self.btn_box.pack_start(self.apply_button)
        self.btn_box.pack_start(self.cancel_button)
        self.vbox.pack_start(self.btn_box)

        self.notebook.set_border_width(1)
        self.vbox.set_border_width(12)

        self.hpaned.pack1(self.vbox, True, False)

    def send_suggestion(self):
        if self.suggestion_radiobtn1.get_active():
            website_url = self.feedback_suggestion_entry.get_text()
            theApp.aggregator.send_website_suggestion(website_url)
        elif self.suggestion_radiobtn2.get_active():
            text = self.feedback_suggestion_entry.get_text()
            service_name = text.split(':')[0]
            host_name = text.split(':')[1]
            ip = text.split(':')[2]
            theApp.aggregator.send_service_suggestion(service_name, host_name, ip)

    def send_bug_report(self):
        pass

    def show_super_peer_list_window(self):
        wnd = SuperPeerListWindow()
        wnd.show_all()

    def clicked_ok(self):
        self.save_preference()
        self.destroy()

    def save_preference(self):
        user_email = self.pref_email_entry.get_text()
        if user_email != '': # and is valid
            theApp.peer_info.Email = user_email

        startup_on_boot = self.pref_startup_check.get_active()
        g_config.set('application', 'startup_on_boot', str(startup_on_boot))
        auto_update = self.pref_update_check.get_active()
        g_config.set('application', 'auto_update', str(auto_update))

        aggregator_url = self.pref_cloudagg_entry.get_text()
        theApp.aggregator.base_url = aggregator_url
        g_db_helper.set_value('aggregator_url', aggregator_url)
        # Save test tab
        self.save_tests()

    def load_preference(self):
        self.pref_page.peerid_label2.set_text(str(theApp.peer_info.ID))
        self.pref_page.email_entry.set_text(theApp.peer_info.Email)

        startup_on_boot = g_config.getboolean('application', 'startup_on_boot')
        if startup_on_boot:
            self.pref_page.startup_check.set_active(True)
        else:
            self.pref_page.startup_check.set_active(False)
        auto_update = g_config.getboolean('application', 'auto_update')
        if auto_update:
            self.pref_page.update_check.set_active(True)
        else:
            self.pref_page.update_check.set_active(False)

        self.pref_page.cloudagg_entry.set_text(theApp.aggregator.base_url)
        # load test tab
        self.load_tests()

    def save_tests(self):
        SELECTED_TESTS = [ r[0] for r in self.test_page.subbox.\
                           tree_view_selected_tests.treestore ]
        g_db_helper.set_value('selected_tests', SELECTED_TESTS)

        auto_update_test = self.test_page.checkbtn.get_active()
        g_config.set('application', 'auto_update_test', str(auto_update_test))

    def load_tests(self):
        from umit.icm.agent.test import ALL_TESTS
        ts = self.test_page.subbox.tree_view_installed_tests.treestore
        for tname in ALL_TESTS:
            ts.append(None, [tname])

        SELECTED_TESTS = g_db_helper.get_value('selected_tests')
        if SELECTED_TESTS:
            ts = self.test_page.subbox.tree_view_selected_tests.treestore
            for tname in SELECTED_TESTS:
                ts.append(None, [tname])

        auto_update_test = g_config.getboolean('application', 'auto_update_test')
        if auto_update_test:
            self.test_page.checkbtn.set_active(True)
        else:
            self.test_page.checkbtn.set_active(False)

########################################################################
class PreferencePage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.peerinfo_hbox = HIGHBox()
        self.cloudagg_hbox = HIGHBox()
        self.superpeers_hbox = HIGHBox()

        self.peerinfo_section = HIGSectionLabel(_("Peer Info"))
        self.peerinfo_table = HIGTable()
        self.cloudagg_section = HIGSectionLabel(_("Cloud Aggregator"))
        self.cloudagg_table = HIGTable()
        self.cloudagg_subhbox = HIGHBox()
        self.superpeers_section = HIGSectionLabel(_("Super Peers"))
        self.superpeers_table = HIGTable()

        self.peerid_label = HIGEntryLabel(_("Peer ID:"))
        self.email_label = HIGEntryLabel(_("Email Address:"))
        self.peerid_label2 = HIGEntryLabel()
        self.email_entry = gtk.Entry()
        self.startup_check = gtk.CheckButton(_("Startup on boot"))
        self.update_check = gtk.CheckButton(_("Automatically update"))

        self.cloudagg_entry = gtk.Entry()
        self.cloudagg_button = HIGButton(_("Reset"))
        self.cloudagg_button.connect('clicked', lambda w:
                                          self.pref_cloudagg_entry.set_text(
                                              'http://icm-dev.appspot.com/api'))
        self.cloudagg_button.set_size_request(80, 28)

        self.superpeers_entry = gtk.Entry()
        self.superpeers_entry.set_size_request(300, 26)
        self.superpeers_subhbox = HIGHBox()
        self.btn_box = gtk.HButtonBox()
        self.superpeers_button1 = HIGButton(_("Add"))
        self.superpeers_button1.connect(
            'clicked', lambda w: reactor.connectTCP(peer_entry.IP,
                                                    peer_entry.Port,
                                                    theApp.factory))
        self.superpeers_button2 = HIGButton(_("Show all"))
        self.superpeers_button2.connect('clicked', lambda w:
                                        self.show_super_peer_list_window())

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.peerinfo_section)
        self._pack_noexpand_nofill(self.peerinfo_hbox)
        self._pack_noexpand_nofill(self.cloudagg_section)
        self._pack_noexpand_nofill(self.cloudagg_hbox)
        self._pack_noexpand_nofill(self.superpeers_section)
        self._pack_noexpand_nofill(self.superpeers_hbox)

        self.peerinfo_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.peerinfo_hbox._pack_expand_fill(self.peerinfo_table)
        self.cloudagg_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.cloudagg_hbox._pack_expand_fill(self.cloudagg_table)
        self.superpeers_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.superpeers_hbox._pack_expand_fill(self.superpeers_table)

        self.peerinfo_table.attach_label(self.peerid_label, 0, 1, 0, 1)
        self.peerinfo_table.attach_label(self.email_label, 0, 1, 1, 2)

        self.peerinfo_table.attach_label(self.peerid_label2, 1, 2, 0, 1)
        self.peerinfo_table.attach_entry(self.email_entry, 1, 2, 1, 2)
        self.peerinfo_table.attach_label(self.startup_check, 0, 2, 2, 3)
        self.peerinfo_table.attach_label(self.update_check, 0, 3, 3, 4)

        self.cloudagg_subhbox._pack_expand_fill(self.cloudagg_entry)
        self.cloudagg_subhbox._pack_noexpand_nofill(self.cloudagg_button)
        self.cloudagg_table.attach_entry(self.cloudagg_subhbox, 0, 1, 0, 1)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(8)
        self.btn_box.pack_start(self.superpeers_button1)
        self.btn_box.pack_start(self.superpeers_button2)
        self.superpeers_subhbox._pack_expand_fill(self.superpeers_entry)
        self.superpeers_subhbox._pack_noexpand_nofill(self.btn_box)
        self.superpeers_table.attach_label(self.superpeers_subhbox, 0, 1, 0, 1)

########################################################################
class TestPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.hbox1 = HIGHBox()
        self.hbox2 = HIGHBox()
        self.subbox = Tests()
        self.hbox1.add(self.subbox)
        self.checkbtn = gtk.CheckButton(_("Update tests module automatically"))

    def __pack_widgets(self):
        #self.tests_hbox.set_border_width(12)
        self.pack_start(self.hbox1, True, True, 5)
        self.pack_start(self.hbox2, True, True, 5)

        self.checkbtn.set_border_width(8)
        self.hbox2.add(self.checkbtn)

class Tests(gtk.VBox):
    def __init__(self):
        super(Tests, self).__init__()
        self.set_size_request(520, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        self.tree_view_installed_tests = TestsView(_("Installed Tests"))
        table.attach(self.tree_view_installed_tests, 0, 1, 0, 3,
                     gtk.FILL | gtk.EXPAND, gtk.FILL | gtk.EXPAND, 1, 1)

        updatebtn = gtk.Button(_("Update"))
        updatebtn.connect('clicked', lambda w: self.update_test_mod())
        updatebtn.set_size_request(50, 30)
        table.attach(updatebtn, 0, 1, 3, 4, gtk.FILL | gtk.EXPAND, gtk.SHRINK, 1, 1)

        vbox = gtk.VBox()
        btnbox = gtk.VButtonBox()
        btnbox.set_border_width(5)
        btnbox.set_layout(gtk.BUTTONBOX_START)
        btnbox.set_spacing(5)
        button = gtk.Button(_("Add"))
        button.connect('clicked', lambda w: self.add_test())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Add All"))
        button.connect('clicked', lambda w: self.add_all())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Remove"))
        button.connect('clicked', lambda w: self.remove_test())
        button.set_size_request(50, 30)
        btnbox.add(button)
        button = gtk.Button(_("Remove All"))
        button.connect('clicked', lambda w: self.remove_all())
        button.set_size_request(50, 30)
        btnbox.add(button)
        table.set_row_spacing(1, 3)
        vbox.add(btnbox)
        table.attach(vbox, 3, 4, 1, 2, gtk.FILL, gtk.SHRINK, 1, 1)

        self.tree_view_selected_tests = TestsView(_("Selected Tests"))
        table.attach(self.tree_view_selected_tests, 4, 5, 1, 3)

        self.add(table)

    def add_test(self):
        tree_selection = self.tree_view_installed_tests.treeview.get_selection()
        tree_iter = tree_selection.get_selected()[1]
        if tree_iter:
            tname = self.tree_view_installed_tests.treestore.\
                  get_value(tree_selection.get_selected()[1], 0)
            values = [ r[0] for r in self.tree_view_selected_tests.treestore ]
            if tname not in values:
                self.tree_view_selected_tests.treestore.append(None, [tname])

    def add_all(self):
        self.tree_view_selected_tests.treestore.clear()
        values = [ r[0] for r in self.tree_view_installed_tests.treestore ]
        for tname in values:
            self.tree_view_selected_tests.treestore.append(None, [tname])

    def remove_test(self):
        tree_selection = self.tree_view_selected_tests.treeview.get_selection()
        tree_iter = tree_selection.get_selected()[1]
        if tree_iter:
            self.tree_view_selected_tests.treestore.remove(tree_iter)

    def remove_all(self):
        self.tree_view_selected_tests.treestore.clear()

    def update_test_mod(self):
        theApp.aggregator.check_tests()

class TestsView(HIGVBox):

    def __init__(self, viewName):
        super(TestsView, self).__init__()
        self.set_size_request(180, 180)

        self.treestore = gtk.TreeStore(str)
        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn(viewName)
        self.treeview.append_column(self.tvcolumn)

        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.add(self.treeview)
        self.show_all()

########################################################################
class FeedbackPage(HIGVBox):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        HIGVBox.__init__(self)
        self.__create_widgets()
        self.__pack_widgets()

    def __create_widgets(self):
        self.suggestion_hbox = HIGHBox()
        self.report_hbox = HIGHBox()

        self.suggestion_section = HIGSectionLabel(_("Send Suggestion"))
        self.suggestion_table = HIGTable()
        self.report_section = HIGSectionLabel(_("Bug Report"))
        self.report_table = HIGTable()

        self.suggestion_radiobtn1 = gtk.RadioButton(None, 'Website')
        self.suggestion_radiobtn1.set_active(True)
        self.suggestion_radiobtn2 = gtk.RadioButton(
            self.suggestion_radiobtn1, 'Service')
        #put these two radio button on a boutton box
        self.suggestion_bbox = gtk.HButtonBox()
        self.feedback_suggestion_entry = gtk.Entry()
        self.feedback_suggestion_sendbtn = HIGButton(_('Send'))
        self.feedback_suggestion_sendbtn.connect('clicked',
                                                 lambda x: self.send_suggestion())

        self.feedback_report_namelabel = HIGEntryLabel(_("Your Name:"))
        self.feedback_report_nameentry = gtk.Entry()
        #self.feedback_report_nameentry.set_has_frame(True)
        self.feedback_report_nameentry.set_size_request(100, 26)
        self.feedback_report_emaillabel = HIGEntryLabel(_("Email:"))
        self.feedback_report_emailentry = gtk.Entry()
        self.feedback_report_emailentry.set_size_request(198, 26)
        self.report_subhbox1 = HIGHBox()

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
        self.report_subhbox2 = HIGHBox()
        self.feedback_report_sendbtn = HIGButton(_('Send'))
        self.feedback_report_sendbtn.connect('clicked',
                                             lambda x: self.send_bug_report())
        self.report_subhbox3 = HIGHBox()

    def __pack_widgets(self):
        self.set_border_width(12)

        self._pack_noexpand_nofill(self.suggestion_section)
        self._pack_noexpand_nofill(self.suggestion_hbox)
        self._pack_noexpand_nofill(self.report_section)
        self._pack_noexpand_nofill(self.report_hbox)

        self.suggestion_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.suggestion_hbox._pack_expand_fill(self.suggestion_table)
        self.report_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.report_hbox._pack_expand_fill(self.report_table)

        self.suggestion_bbox.set_layout(gtk.BUTTONBOX_START)
        self.suggestion_bbox.pack_start(self.suggestion_radiobtn1)
        self.suggestion_bbox.pack_start(self.suggestion_radiobtn2)
        self.suggestion_table.attach_label(self.suggestion_bbox, 0, 1, 0, 1)
        self.suggestion_table.attach_entry(self.feedback_suggestion_entry, 0, 1, 1, 2)
        self.suggestion_table.attach(self.feedback_suggestion_sendbtn,
                                              0, 1, 2, 3, gtk.PACK_START)

        self.report_subhbox1.pack_start(self.feedback_report_namelabel, True, True, 0)
        self.report_subhbox1.pack_start(self.feedback_report_nameentry, True, True, 0)
        self.report_subhbox1.pack_start(self.feedback_report_emaillabel, True, True, 0)
        self.report_subhbox1.pack_start(self.feedback_report_emailentry)
        self.report_table.attach(self.report_subhbox1, 0, 1, 0, 1)
        self.report_subhbox2.pack_start(self.feedback_report_sw)
        self.report_table.attach(self.report_subhbox2, 0, 1, 1, 2)
        self.report_subhbox3.pack_start(self.feedback_report_sendbtn)
        self.report_table.attach(self.report_subhbox3, 0, 1, 2, 3, gtk.PACK_START)

class SuperPeerListWindow(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Super Peers'))
        self.__create_widgets()
        self.__pack_widgets()
        self.__load_super_peers()

    def __create_widgets(self):
        self.main_vbox = HIGVBox()
        self.add(self.main_vbox)
        self.btn_box = gtk.HButtonBox()
        self.ok_button = gtk.Button(stock=gtk.STOCK_SAVE)
        self.ok_button.connect('clicked', lambda x: self.__save_super_peers())
        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', lambda x: self.destroy())

        self.SuperPeersBox_vbox = HIGVBox()
        self.SuperPeersBox_hbox1 = HIGHBox()
        self.SuperPeersBox_hbox2 = HIGHBox()
        self.SuperPeersBox_subbox = SuperPeersBox()
        self.SuperPeersBox_hbox1.add(self.SuperPeersBox_subbox)

    def __pack_widgets(self):
        self.main_vbox._pack_expand_fill(self.SuperPeersBox_hbox1)

        self.btn_box.set_layout(gtk.BUTTONBOX_END)
        self.btn_box.set_spacing(3)
        self.btn_box.pack_start(self.ok_button)
        self.btn_box.pack_start(self.cancel_button)
        self.main_vbox.pack_start(self.btn_box)
        self.main_vbox.set_border_width(12)

        self.SuperPeersBox_vbox.pack_start(self.SuperPeersBox_hbox1, True, True, 5)
        self.SuperPeersBox_vbox.pack_start(self.SuperPeersBox_hbox2, True, True, 5)

    def __save_super_peers(self):
        self.destroy()

    def __load_super_peers(self):
        text = ""
        for peer_entry in theApp.peer_manager.super_peers.values():
            text = text + "%s:%d\n" % (peer_entry.IP, peer_entry.Port)
        self.SuperPeersBox_subbox.textbuffer.set_text(text)

class SuperPeersBox(gtk.VBox):
    def __init__(self):
        super(SuperPeersBox, self).__init__()
        self.set_size_request(400, 240)
        self.set_border_width(8)

        table = gtk.Table(8, 5, False)
        table.set_col_spacings(3)

        title = gtk.Label("""\
<span size='12000'>Super Peer List: \n</span>""")

        title.set_use_markup(True)

        halign = gtk.Alignment(0, 0, 0, 0)
        halign.add(title)

        table.attach(halign, 0, 1, 0, 1, gtk.FILL,
                     gtk.FILL, 0, 0);

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        wins = gtk.TextView()
        self.textbuffer = wins.get_buffer()
        wins.set_editable(True)
        wins.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(5140, 5140, 5140))
        wins.set_cursor_visible(True)
        wins.show()
        sw.add(wins)
        sw.show()
        table.attach(sw, 0, 1, 1, 3)
        self.add(table)


if __name__ == "__main__":
    def quit(x, y):
        gtk.main_quit()

    wnd = PreferenceWindow()
    #wnd.set_size_request(520, 440)
    wnd.connect("delete-event", quit)
    wnd.show_all()
    gtk.main()