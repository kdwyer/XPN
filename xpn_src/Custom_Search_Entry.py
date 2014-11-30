import gtk,gobject

class Custom_Search_Entry(gtk.HBox):
    __gsignals__ = {
      'do_search':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,gobject.TYPE_STRING)),
      'search_focus_in':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,)),
      'search_focus_out':(gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,))
    }

    def __init__(self):
        gtk.HBox.__init__(self)

        self.entry=gtk.Entry()
        self.entry.set_size_request(80,-1)
        self.entry.connect("focus-in-event",self.entry_focus_in)
        self.entry.connect("focus-out-event",self.entry_focus_out)

        bar=gtk.MenuBar()
        self.search=gtk.MenuItem("search")
        button=gtk.Button("",gtk.STOCK_FIND)
        
        menu=gtk.Menu()
        item=None
        for name in ("Subject","From","Body"):
            item=gtk.RadioMenuItem(item,name)
            item.connect("toggled",self.change_search_type,name)
            menu.append(item)
            if name=="Subject": item.set_active(True)

        self.search.set_submenu(menu)

        bar.append(self.search)
        
        #self.pack_start(gtk.VSeparator(),False,False,2)
        self.pack_start(bar,False,False,0)
        self.pack_start(self.entry,False,False,0)
        self.pack_start(button,False,False,0)
        #self.pack_start(gtk.VSeparator(),False,False,2)


        button.connect("clicked",self.on_search_clicked)

        self.search_type="Subject"
    
    def grab_focus(self):
        self.entry.grab_focus()
    
    def on_search_clicked(self,obj):
        self.emit("do_search",self.search_type,self.entry.get_text().decode("utf-8"))

    def change_search_type(self,obj,name):
        self.search_type=name
        self.search.get_child().set_label(name)

    def entry_focus_in(self,obj,event):
        self.emit("search_focus_in","focus_in")

    def entry_focus_out(self,obj,event):
        self.emit("search_focus_out","focus_out")
