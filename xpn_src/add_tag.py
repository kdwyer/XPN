#!/usr/bin/env python
import gtk
import os
from locale import getdefaultlocale
from xpn_src.UserDir import get_wdir


class Tags_Window:
    def delete_event(self,widget,event,data=None):
        return False  

    def destroy(self,widget):
        self.window.destroy()
        if __name__=="__main__":
            gtk.main_quit()
    
    def append_tag(self,widget):
        try:
            f=open(self.FILENAME,"a")
        except IOError:
            f=open(self.FILENAME,"w")
        try: system_enc=getdefaultlocale()[1]
        except: system_enc="US-ASCII"
        tag=self.entry.get_text().decode("utf-8").encode(system_enc,"replace")
        if tag!="":
            f.write(tag+"\n")
            self.statusbar.push(1,_("TagLine Added"))
            self.entry.set_text("")
        f.close()

    def show_length(self,widget):
        length=len(self.entry.get_text().decode("utf-8"))
        self.statusbar.push(1,_("TagLine length: ")+repr(length))

    def load_state(self):
        try:
            f=open(self.FILENAME,"r")
        except IOError:
            length="0"
        else:
            length=repr(len(f.readlines()))
            f.close()
        self.statusbar.push(1,_("Found %s tags") % (length,))
        
    def __init__(self):
        self.FILENAME=os.path.join(get_wdir(),"tags.txt")
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("XPN TagLines Manager"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        vbox=gtk.VBox(False,0)
        vbox.set_border_width(2)
        label=gtk.Label(_("\n<b>Insert here a tagline</b>\n"))
        label.set_use_markup(True)
        vbox.pack_start(label,True,True,0)
        self.entry=gtk.Entry()
        self.entry.connect("changed",self.show_length)
        vbox.pack_start(self.entry,False,True,0)
        hbox_buttons=gtk.HBox()
        hbox_buttons.set_border_width(4)
        self.button_ok=gtk.Button(None,gtk.STOCK_ADD)
        self.button_ok.connect("clicked",self.append_tag)
        self.button_close=gtk.Button(None,gtk.STOCK_CLOSE)
        self.button_close.connect("clicked",self.destroy)
        hbox_buttons.pack_start(self.button_close,True,True,2)
        hbox_buttons.pack_start(self.button_ok,True,True,2)
        vbox.pack_start(hbox_buttons,True,True,0)
        self.statusbar=gtk.Statusbar()
        vbox.pack_start(self.statusbar,False,True,0)
        self.window.add(vbox)
        self.window.set_default_size(550,60)
        self.window.show_all()
        self.load_state()

if __name__=="__main__":
    tags_win=Tags_Window()
    gtk.main()
