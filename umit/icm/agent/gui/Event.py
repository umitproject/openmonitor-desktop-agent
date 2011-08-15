#!/usr/bin/env python

import os, stat, time
import pygtk
pygtk.require('2.0')
import gtk

class EventWindow:
    column_names = ['test type', 'event type', 'time', 'location', 'reports']

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
 
    def __init__(self, dname = None):
        cell_data_funcs = (None, self.event_type, self.time,
                           self.location, self.report)
 
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
 
        self.window.set_size_request(400, 300)
 
        self.window.connect("delete_event", self.delete_event)
 
        listmodel = self.make_list(dname)
 
        # create the TreeView
        self.treeview = gtk.TreeView()
 
        # create the TreeViewColumns to display the data
        self.tvcolumn = [None] * len(self.column_names)
        cellpb = gtk.CellRendererPixbuf()
        self.tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0], cellpb)
        cell = gtk.CellRendererText()
        self.tvcolumn[0].pack_start(cell, False)
        self.tvcolumn[0].set_cell_data_func(cell, self.test_type)
        self.treeview.append_column(self.tvcolumn[0])
        for n in range(1, len(self.column_names)):
            cell = gtk.CellRendererText()
            self.tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
            if n == 1:
                cell.set_property('xalign', 1.0)
            self.tvcolumn[n].set_cell_data_func(cell, cell_data_funcs[n])
            self.treeview.append_column(self.tvcolumn[n])

        #self.treeview.connect('row-activated', self.open_file)
        #上面这一行代码可以添加一个响应，比如双击某一行弹出一个对话框，显示event的详细信息
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.window.add(self.scrolledwindow)
        self.treeview.set_model(listmodel)
 
        self.window.show_all()
        return

    def make_list(self, dname=None):
        #这个是得到第一列的函数，类似数据库主键的感觉
        #listmodel = [[2],[2],[2],[2]]
        listmodel = gtk.ListStore(object)
        return listmodel

    #往下几个函数都是分别得到每一列的信息，按照cell.set_property的格式添加即可
    def test_type(self, column, cell, model, iter):
        #cell.set_property('text', model.get_value(iter, 0))
        return

    def event_type(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', filestat.st_size)
        return

    def time(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', oct(stat.S_IMODE(filestat.st_mode)))
        return

    def location(self, column, cell, model, iter):
        #filename = os.path.join(self.dirname, model.get_value(iter, 0))
        #filestat = os.stat(filename)
        #cell.set_property('text', time.ctime(filestat.st_mtime))
        return
    
    def report(self, column, cell, model, iter):
        return
    
def main():
    gtk.main()

if __name__ == "__main__":
    flcdexample = EventWindow()
    main()