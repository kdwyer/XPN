import gtk
import ConfigParser
import os
from xpn_src.UserDir import get_wdir
from xpn_src.Dialogs import Dialog_OK

class NNTPServer_Win:
    def show(self):
        self.win.show_all()
    
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,obj):
        self.win.destroy()

    def change_auth_status(self,obj):
        status=self.server_auth_checkbutton.get_active()
        self.server_username.set_sensitive(status)
        self.server_password.set_sensitive(status)
        self.username_label.set_sensitive(status)
        self.password_label.set_sensitive(status)

    def change_ssl_status(self,checkbutton):
        status=checkbutton.get_active()
        if status:
            self.port_entry.set_text("563")
        else:
            self.port_entry.set_text("119")

    def save_configs(self,button):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        server_name=self.server_entry.get_text()
        if server_name!="":
            try: cp.add_section(server_name)
            except: pass
            cp.set(server_name,"server",server_name)
            cp.set(server_name,"port",self.port_entry.get_text())
            cp.set(server_name,"nntp_use_ssl",str(self.server_use_ssl_checkbutton.get_active()))
            if self.server_auth_checkbutton.get_active():
                cp.set(server_name,"auth","True")
                cp.set(server_name,"username",self.server_username.get_text())
                cp.set(server_name,"password",self.server_password.get_text())
            else:
                cp.set(server_name,"auth","False")
                cp.set(server_name,"username","")
                cp.set(server_name,"password","")
            cp.write(file(os.path.join(get_wdir(),"dats","servers.txt"),"w"))
            self.win.destroy()
            self.config_win.refresh_server_list()
        else:
            d=Dialog_OK(_("Please set the Server Name"))

    def load_configs(self,server_to_load):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.server_entry.set_text(cp.get(server_to_load,"server"))
        self.port_entry.set_text(cp.get(server_to_load,"port"))
        if cp.get(server_to_load,"nntp_use_ssl")=="True":
            self.server_use_ssl_checkbutton.set_active(True)
        else:
            self.server_use_ssl_checkbutton.set_active(False)
        if cp.get(server_to_load,"auth")=="True":
            self.server_auth_checkbutton.set_active(True)
        else:
            self.server_auth_checkbutton.set_active(False)
            self.server_username.set_sensitive(False)
            self.server_password.set_sensitive(False)
            self.username_label.set_sensitive(False)
            self.password_label.set_sensitive(False)
        self.server_username.set_text(cp.get(server_to_load,"username"))
        self.server_password.set_text(cp.get(server_to_load,"password"))



    def __init__(self,config_win,server_to_load=None):
        self.config_win=config_win
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("Server Settings"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/conf.xpm"))
        self.win.set_position(gtk.WIN_POS_CENTER)

        server_label=gtk.Label("<b>"+_("NNTP Server")+"</b>")
        server_label.set_alignment(0,0.5)
        server_label.set_use_markup(True)
        server_vbox=gtk.VBox()
        server_vbox.set_border_width(4)
        server_vbox.pack_start(server_label,False,True,4)
        server_table=gtk.Table(4,2,False)
        server_table.set_border_width(8)

        self.server_entry=gtk.Entry()
        self.port_entry=gtk.Entry()
        self.port_entry.set_text("119")
        self.server_username=gtk.Entry()
        self.server_password=gtk.Entry()
        self.server_password.set_visibility(False)
        self.server_auth_checkbutton=gtk.CheckButton(_("Server requires authentication"))
        self.server_auth_checkbutton.connect("clicked",self.change_auth_status)
        self.server_use_ssl_checkbutton=gtk.CheckButton(_("Use SSL (Secure Socket Layer)"))
        self.server_use_ssl_checkbutton.connect("clicked",self.change_ssl_status)
        try: from socket import ssl
        except: self.server_use_ssl_checkbutton.set_sensitive(False)

        address_label=gtk.Label(_("NNTP Server Address"))
        port_label=gtk.Label(_("Port Number"))
        address_label.set_alignment(0,0.5)
        port_label.set_alignment(0,0.5)        
        self.username_label=gtk.Label(_("Username"))
        self.username_label.set_alignment(0,0.5)
        self.password_label=gtk.Label(_("Password"))
        self.password_label.set_alignment(0,0.5)
        
        server_table.attach(address_label,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        server_table.attach(port_label,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        server_table.attach(self.username_label,0,1,4,5,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        server_table.attach(self.password_label,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL,18)

        server_table.attach(self.server_entry,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL)
        server_table.attach(self.port_entry,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL)
        server_table.attach(self.server_use_ssl_checkbutton,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL)
        server_table.attach(self.server_auth_checkbutton,1,2,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL)
        server_table.attach(self.server_username,1,2,4,5,gtk.EXPAND|gtk.FILL,gtk.FILL)
        server_table.attach(self.server_password,1,2,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL)

        self.change_auth_status(None)
        
        #buttons hbox
        buttons_hbox=gtk.HBox()

        #cancel_button
        self.cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        self.cancel_button_tooltip=gtk.Tooltips()
        self.cancel_button_tooltip.set_tip(self.cancel_button,_("Close window. Discard changes"))
        self.cancel_button.connect("clicked",self.destroy)
        buttons_hbox.pack_start(self.cancel_button,True,True,0)
        #ok_button
        self.ok_button=gtk.Button(None,gtk.STOCK_OK)
        self.ok_button.connect("clicked",self.save_configs)
        self.ok_button_tooltip=gtk.Tooltips()
        self.ok_button_tooltip.set_tip(self.ok_button,_("Close window and save settings"))
        buttons_hbox.pack_start(self.ok_button,True,True,0)
        self.ok_button.set_border_width(5)
        self.cancel_button.set_border_width(5)

        server_vbox.pack_start(server_table,False,False)
        server_vbox.pack_start(buttons_hbox,False,False,0)
        self.win.add(server_vbox)
        if server_to_load: self.load_configs(server_to_load)
