#!/usr/bin/env python
import gtk
import os
from xpn_src.UserDir import get_wdir


class Logs_Window:
    def delete_event(self,widget,event,data=None):
        return False  

    def destroy(self,widget):
        self.window.destroy()
        if __name__=="__main__":
            gtk.mainquit()

    def insert(self,string):
        mark=self.buffer.get_insert()
        iter=self.buffer.get_iter_at_mark(mark)
        time,log=string.split("::")
        if ">>" in string:
            self.buffer.insert_with_tags_by_name(iter,(time+"::").encode("utf-8"),"time")
            mark=self.buffer.get_insert()
            iter=self.buffer.get_iter_at_mark(mark)
            self.buffer.insert_with_tags_by_name(iter,log.encode("utf-8"),"blue")
        else:
            self.buffer.insert_with_tags_by_name(iter,(time+"::").encode("utf-8"),"time")
            mark=self.buffer.get_insert()
            iter=self.buffer.get_iter_at_mark(mark)
            self.buffer.insert_with_tags_by_name(iter,log.encode("utf-8"),"red")
            

    def load_logs(self):
        try:
            f=open(self.FILENAME,"r")
        except IOError:
            length="0"
        else:
            logs=f.readlines()
            for line in logs:
                self.insert(line)
            f.close()
        
    def __init__(self,main_win):
        self.FILENAME=os.path.join(get_wdir(),"server_logs.dat")
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Server Logs Viewer"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        if main_win!=None:
            self.window.set_modal(True)    
            self.window.set_transient_for(main_win)
        vbox=gtk.VBox(False,0)
        vbox.set_border_width(2)
        label=gtk.Label("\n<b>"+_("Server Logs")+"</b>\n")
        label.set_use_markup(True)
        vbox.pack_start(label,False,True,0)
        self.buffer=gtk.TextBuffer()
        scrolledwin=gtk.ScrolledWindow()
        scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolledwin.set_border_width(4)
        self.view=gtk.TextView(self.buffer)
        self.view.set_wrap_mode(gtk.WRAP_WORD)
        self.view.set_justification(gtk.JUSTIFY_LEFT)
        self.view.set_cursor_visible(False)
        self.view.set_editable(False)
        self.view.set_indent(2)
        scrolledwin.add(self.view)

        blue_color=gtk.gdk.color_parse("blue")
        red_color=gtk.gdk.color_parse("red")
        black_color=gtk.gdk.color_parse("black")
        self.tag_table=self.buffer.get_tag_table()
        self.blue_tag=gtk.TextTag("blue")
        self.red_tag=gtk.TextTag("red")
        self.time_tag=gtk.TextTag("time")
        self.tag_table.add(self.blue_tag)
        self.tag_table.add(self.red_tag)
        self.tag_table.add(self.time_tag)
        self.blue_tag.set_property("foreground-gdk",blue_color)
        self.red_tag.set_property("foreground-gdk",red_color)
        self.time_tag.set_property("foreground-gdk",black_color)

        vbox.pack_start(scrolledwin,True,True,0)
        self.button=gtk.Button(None,gtk.STOCK_OK)
        self.button.set_border_width(4)
        self.button.connect("clicked",self.destroy)
        vbox.pack_start(self.button,False,True,0)
        self.window.add(vbox)
        self.window.set_default_size(550,500)
        self.window.show_all()
        self.load_logs()

if __name__=="__main__":
    logs_win=Logs_Window(None)
    gtk.mainloop()
