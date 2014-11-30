import gtk
import gobject 
import ConfigParser
import os
from xpn_src.UserDir import get_wdir


class About_Dialog:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget,event):
        self.dialog.destroy()

    def show(self):
        self.dialog.show_all()

    def __init__(self,NUMBER):
        self.dialog=gtk.Dialog(_("About"),None,0,(gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.set_default_size(300,280)
        self.dialog.connect("delete_event",self.delete_event)
        self.dialog.connect("response",self.destroy)
        self.dialog.set_has_separator(True)
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.image=gtk.Image()
        self.image.set_from_file("pixmaps/xpn-logo-small.png")
        self.dialog.vbox.pack_start(self.image,True,True)
        string="<span size='x-large' weight='heavy'>X Python Newsreader %s</span>\n<span weight='heavy' style='italic'>Italian Style</span>\n\nWritten by Antonio 'Nemesis' Caputo\nxpn@altervista.org\n\nhttp://xpn.altervista.org" % (NUMBER,)
        self.label=gtk.Label(string)
        self.label.set_use_markup(True)
        self.label.set_justify(gtk.JUSTIFY_CENTER)
        self.dialog.vbox.pack_start(self.label,True,True,8)

class Dialog_YES_NO:

    def delete_event(self,widget,event,data=None):
        return False

    def __init__(self,message):
        self.resp=""
        self.dialog=gtk.MessageDialog(None,0,gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,message)
        self.dialog.connect("delete_event",self.delete_event)
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.dialog.label.set_use_markup(True)
        resp=self.dialog.run()
        if resp==gtk.RESPONSE_YES:
            self.resp=True
        else:
            self.resp=False
        self.dialog.destroy()

class Dialog_OK:

    def delete_event(self,widget,event,data=None):
        return False

    def __init__(self,message):
        self.resp=""
        self.dialog=gtk.MessageDialog(None,0,gtk.MESSAGE_INFO,gtk.BUTTONS_OK,message)
        self.dialog.connect("delete_event",self.delete_event)
        self.dialog.set_position(gtk.WIN_POS_CENTER)
        self.dialog.label.set_use_markup(True)
        self.resp=self.dialog.run()
        self.dialog.destroy()

class Dialog_Import_Newsrc(gtk.Dialog):
    def __init__(self,message,server_name):
        gtk.Dialog.__init__(self,_("Choose the Server"),None,0,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.label=gtk.Label(message)
        self.label.set_use_markup(True)
        self.set_position(gtk.WIN_POS_CENTER)
        self.server_combo=gtk.combo_box_new_text()
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        positions=dict()
        i=0
        for server in cp.sections(): 
            self.server_combo.append_text(cp.get(server,"server"))
            positions[server]=i
            i=i+1
        
        if server_name: self.server_combo.set_active(positions.get(server_name,0))
        else: self.server_combo.set_active(0)
        
        self.vbox.pack_start(self.label,True,True,8)
        self.vbox.pack_start(self.server_combo,False,False,8)
        self.server_combo.show()
        self.label.show()
        self.label.set_line_wrap(True)
        if len(positions)== 0:
            Dialog_OK(_("First you have to configure at least one Server"))
            self.resp=gtk.RESPONSE_CLOSE
            self.destroy()
        else:
            self.resp=self.run()
            self.server_name=self.server_combo.get_active_text()
            self.destroy()

class Error_Dialog(gtk.Dialog):
    def __init__(self,string,log):
        gtk.Dialog.__init__(self,_("Error Dialog"),None,0,(gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.set_default_size(350,350)
        self.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/dialog-error.xpm"))
        self.set_has_separator(True)
        self.set_position(gtk.WIN_POS_CENTER)
        self.buffer=gtk.TextBuffer()
        self.buffer.set_text(string)
        self.view=gtk.TextView(self.buffer)
        self.view.set_wrap_mode(gtk.WRAP_WORD)
        self.view.set_cursor_visible(False)
        self.view.set_border_width(5)
        self.view.set_editable(False)
        self.scrolled_win=gtk.ScrolledWindow()
        self.scrolled_win.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolled_win.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scrolled_win.add(self.view)
        self.buffer_log=gtk.TextBuffer()
        self.buffer_log.set_text(log)
        self.view_log=gtk.TextView(self.buffer_log)
        self.view_log.set_wrap_mode(gtk.WRAP_WORD)
        self.view_log.set_cursor_visible(False)
        self.view_log.set_border_width(5)
        self.view_log.set_editable(False)
        self.scrolled_win_log=gtk.ScrolledWindow()
        self.scrolled_win_log.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolled_win_log.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.scrolled_win_log.add(self.view_log)
        self.notebook=gtk.Notebook()
        self.label_error=gtk.Label("<b>"+_("Last Error")+"</b>")
        self.label_error.set_use_markup(True)
        self.label_error_log=gtk.Label("<b>"+_("Errors Log")+"</b>")
        self.label_error_log.set_use_markup(True)
        self.notebook.append_page(self.scrolled_win,self.label_error)
        self.notebook.append_page(self.scrolled_win_log,self.label_error_log)
        self.notebook.show_all()

        self.vbox.pack_start(self.notebook,True,True,0)

class MidDialog(gtk.Dialog):
    def __init__(self,mid):
        gtk.Dialog.__init__(self,_("Message-ID Search Dialog"),None,0,(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE,gtk.STOCK_OK,gtk.RESPONSE_OK))

        self.label=gtk.Label("<b>"+_("Message-ID to search")+"</b>")
        self.label.set_use_markup(True)
        self.entry=gtk.Entry()
        self.entry.set_text(mid)
        self.entry.show()
        self.label.show()
        self.vbox.pack_start(self.label,True,True)
        self.vbox.pack_start(self.entry,True,True)
        self.r1=gtk.RadioButton(None,_("Search in current group"))
        self.r2=gtk.RadioButton(self.r1,_("Search in subscribed groups"))
        self.r3=gtk.RadioButton(self.r1,_("Search on Google"))
        self.r1.show()
        self.r2.show()
        self.r3.show()
        self.vbox.pack_start(self.r1,True,True)
        self.vbox.pack_start(self.r2,True,True)
        self.vbox.pack_start(self.r3,True,True)
        self.set_size_request(350,200)

        self.resp=self.run()
        self.sel=self.r1.get_active(),self.r2.get_active(),self.r3.get_active()
        self.destroy()

class Shortcut_Dialog(gtk.Dialog):
    def grab_shortcut(self,obj,event):
        comb=""
        name=gtk.gdk.keyval_name(event.keyval)
        string_name=event.string
        if event.state & gtk.gdk.CONTROL_MASK:
            comb=comb+"<Control>"
        if event.state & gtk.gdk.MOD1_MASK:
            comb=comb+"<Alt>"
        if event.state & gtk.gdk.SHIFT_MASK:
            comb=comb+"<Shift>"
        comb=comb+name
        admitted=["delete",]+["f"+str(i) for i in range(1,13)]
        if string_name or comb.lower() in admitted:
            self.entry.set_text(comb)
            self.shortcut=comb
        else:
            self.entry.set_text("")
            self.shortcut=""

    def __init__(self):
        gtk.Dialog.__init__(self,_("Shortcut Dialog"),None,0,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE))
        self.label1=gtk.Label("<b>"+_("Type your Shortcut")+"</b>")
        self.label1.set_use_markup(True)
        self.label2=gtk.Label("<b>"+_("Press OK to confirm it")+"</b>")
        self.label2.set_use_markup(True)
        self.entry=gtk.Entry()
        self.entry.set_sensitive(False)
        self.entry.show()
        self.label1.show()
        self.label2.show()
        self.vbox.pack_start(self.label1,True,True,4)
        self.vbox.pack_start(self.label2,True,True,4)
        self.vbox.pack_start(self.entry,True,True,4)
        self.shortcut=""        
        self.connect("key-press-event",self.grab_shortcut)
        self.resp=self.run()
        self.destroy()

class Shortcut_Error_Warning_Dialog(gtk.MessageDialog):
    def __init__(self,warning,list,message):
        if warning:
            type=gtk.MESSAGE_WARNING
        else:
            type=gtk.MESSAGE_ERROR
        gtk.MessageDialog.__init__(self,None,0,type,gtk.BUTTONS_OK,message)
        self.set_size_request(500,400)
        self.set_resizable(True)
        self.label.set_use_markup(True)
        scrolledwin=gtk.ScrolledWindow()
        self.treeview=gtk.TreeView()
        self.treeview.set_border_width(4)
        scrolledwin.add(self.treeview)
        self.model=gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.treeview.set_model(self.model)
        text_renderer=gtk.CellRendererText()
        column1=gtk.TreeViewColumn(_("Window"),text_renderer,text=0)
        column1.set_resizable(True)
        column2=gtk.TreeViewColumn(_("Shortcut"),text_renderer,text=1)
        column2.set_resizable(True)
        column3=gtk.TreeViewColumn(_("Action"),text_renderer,text=2)
        self.treeview.append_column(column1)
        self.treeview.append_column(column2)
        self.treeview.append_column(column3)
        self.treeview.set_rules_hint(True)
        for line in list: self.model.append(line)
        self.vbox.add(scrolledwin)
        self.vbox.show_all()
        self.resp=self.run()
        self.destroy()


