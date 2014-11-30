import gtk
import ConfigParser
import os
from xpn_src.UserDir import get_wdir
from xpn_src.Dialogs import Dialog_OK
from xpn_src.add_tag import Tags_Window

class ID_Win:
    def show(self):
        self.win.show_all()
    
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,obj):
        self.win.destroy()

    def open_filesel_dialog(self,obj):
        def dispatch_response(dialog,id):
            if id==gtk.RESPONSE_OK:
                self.update_sign_entry(None)
            if id==gtk.RESPONSE_CANCEL:
                self.file_dialog.destroy()

        def show_hide_hidden(obj):
            self.file_dialog.set_property("show_hidden",obj.get_active())
        self.file_dialog=gtk.FileChooserDialog(_("Select Signature File"),None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        hidden_checkbutton=gtk.CheckButton(_("Show Hidden Files"))
        self.file_dialog.set_extra_widget(hidden_checkbutton)
        hidden_checkbutton.connect("clicked",show_hide_hidden)
        self.file_dialog.set_local_only(True)
        self.file_dialog.connect("response",dispatch_response)
        path=self.file_dialog.get_current_folder()
        self.file_dialog.set_current_folder(path)
        self.file_dialog.show()

    def update_sign_entry(self,obj):
        filename=self.file_dialog.get_filename()
        self.sign_entry.set_text(filename)
        self.file_dialog.destroy()


    def save_custom_headers(self,id_name):
        bounds=self.custom_headers_buffer.get_bounds()
        if bounds:
            start,stop=bounds
            f=open(os.path.join(get_wdir(),"dats",id_name+"_custom_headers.txt"),"w")
            headers=self.custom_headers_buffer.get_text(start,stop,True).decode("utf-8").split("\n")
            for header in headers:
                if ":" in header:
                    f.write(header.encode("utf-8")+"\n")
            f.close()


    def save_configs(self,obj):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","id.txt"))
        id_name=self.id_entry.get_text().decode("utf-8")
        if id_name!="":
            try: cp.add_section(id_name)
            except: pass
            cp.set(id_name,"nick",self.nick_entry.get_text().decode("utf-8"))
            cp.set(id_name,"email",self.email_entry.get_text().decode("utf-8"))
            if self.use_mail_from.get_active():
                use_mail_from="True"
                mail_nick=self.mail_nick_entry.get_text().decode("utf-8")
                mail_email=self.mail_email_entry.get_text().decode("utf-8")
            else:
                use_mail_from="False"
                mail_nick=""
                mail_email=""
            
            cp.set(id_name,"use_mail_from",use_mail_from)
            cp.set(id_name,"mail_nick",mail_nick)
            cp.set(id_name,"mail_email",mail_email)
            cp.set(id_name,"sign",self.sign_entry.get_text().decode("utf-8"))
            cp.set(id_name,"use_tags",str(bool(self.tags_checkbutton.get_active())))
            cp.set(id_name,"wrap",repr(self.wrap_spinbutton.get_value_as_int()))
            cp.set(id_name,"attribution",self.attribution_entry.get_text().decode("utf-8"))
            cp.set(id_name,"reply-to",self.reply_to_entry.get_text().decode("utf-8"))
            cp.set(id_name,"organization",self.organization_entry.get_text().decode("utf-8"))
            cp.set(id_name,"mail-copies-to",self.mail_copies_to_entry.get_text().decode("utf-8"))
            if self.generate_mid_checkbutton.get_active():
                cp.set(id_name,"gen_mid","True")
                cp.set(id_name,"fqdn",self.fqdn_entry.get_text().decode("utf-8"))
            else:
                cp.set(id_name,"gen_mid","False")
                cp.set(id_name,"fqdn","")
            
            cp.write(file(os.path.join(get_wdir(),"dats","id.txt"),"w"))

            self.save_custom_headers(id_name)

            self.win.destroy()
            self.config_win.refresh_id_list()
        else:
            d=Dialog_OK(_("Please set the Identity Name"))

    def load_configs(self,id_to_load):
        pass
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","id.txt"))
        self.id_entry.set_text(id_to_load)
        self.nick_entry.set_text(cp.get(id_to_load,"nick").encode("utf-8"))
        self.email_entry.set_text(cp.get(id_to_load,"email").encode("utf-8"))

        if cp.get(id_to_load,"use_mail_from")=="True":
            self.use_mail_from.set_active(True)
        else:
            self.use_mail_from.set_active(False)
            self.mail_nick_entry.set_sensitive(False)
            self.mail_email_entry.set_sensitive(False)
            self.mail_nick_label.set_sensitive(False)
            self.mail_email_label.set_sensitive(False)
        self.mail_nick_entry.set_text(cp.get(id_to_load,"mail_nick").encode("utf-8"))
        self.mail_email_entry.set_text(cp.get(id_to_load,"mail_email").encode("utf-8"))
        self.sign_entry.set_text(cp.get(id_to_load,"sign").encode("utf-8"))
        self.tags_checkbutton.set_active(cp.get(id_to_load,"use_tags")=="True")
        self.wrap_spinbutton.set_value(int(cp.get(id_to_load,"wrap")))
        self.attribution_entry.set_text(cp.get(id_to_load,"attribution").encode("utf-8"))
        self.reply_to_entry.set_text(cp.get(id_to_load,"reply-to").encode("utf-8"))
        self.organization_entry.set_text(cp.get(id_to_load,"organization").encode("utf-8"))
        self.mail_copies_to_entry.set_text(cp.get(id_to_load,"mail-copies-to").encode("utf-8"))
       
        if cp.get(id_to_load,"gen_mid")=="True":
            self.generate_mid_checkbutton.set_active(True)
        else:
            self.generate_mid_checkbutton.set_active(False)
            self.fqdn_entry.set_sensitive(False)
        self.fqdn_entry.set_text(cp.get(id_to_load,"fqdn").encode("utf-8"))

        try:
            f=open(os.path.join(get_wdir(),"dats",id_to_load+"_custom_headers.txt"),"r")
        except IOError:
            pass
        else:
            headers=f.read().decode("utf-8")
            self.custom_headers_buffer.set_text(headers.encode("utf-8"))
            f.close()

    def change_mail_from_status(self,obj):
        status=self.use_mail_from.get_active()
        self.mail_nick_entry.set_sensitive(status)
        self.mail_email_entry.set_sensitive(status)
        self.mail_nick_label.set_sensitive(status)
        self.mail_email_label.set_sensitive(status)

    def add_tag_line(self,obj):
        tag_win=Tags_Window()

    def change_mid_status(self,obj):
        status=self.generate_mid_checkbutton.get_active()
        self.fqdn_entry.set_sensitive(status)
        self.fqdn_label.set_sensitive(status)

    def load_defaults(self):
        self.attribution_entry.set_text("%n wrote:")
        self.change_mid_status(None)
        self.change_mail_from_status(None)

    def __init__(self,config_win,id_to_load=None):
        self.config_win=config_win
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("Identity Settings"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/conf.xpm"))
        self.win.set_position(gtk.WIN_POS_CENTER)

        notebook=gtk.Notebook()

        id_page_label=gtk.Label("<b>"+_("Personal Informations")+"</b>")
        id_page_label.set_alignment(0,0.5)
        id_page_label.set_use_markup(True)

        id_vbox=gtk.VBox()
        id_vbox.set_border_width(4)
        win_vbox=gtk.VBox()
        win_vbox.set_border_width(4)

        self.id_entry=gtk.Entry()        
        id_label=gtk.Label(_("Identity"))
        id_label.set_size_request(200,-1)
        id_label.set_alignment(0,0.5)
        id_entry_hbox=gtk.HBox()
        id_entry_hbox.pack_start(self.id_entry,True,True,10)
        id_entry_hbox.pack_start(id_label,True,True,10)


        id_table=gtk.Table(4,2,False)
        id_table.set_border_width(8)

        self.nick_entry=gtk.Entry()
        self.email_entry=gtk.Entry()




        nick_label=gtk.Label(_("Name or NickName"))
        nick_label.set_alignment(0,0.5)
        email_label=gtk.Label(_("E-Mail address"))
        email_label.set_alignment(0,0.5)

        id_table.attach(self.nick_entry,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        id_table.attach(self.email_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        id_table.attach(nick_label,1,2,0,1,gtk.EXPAND|gtk.FILL)
        id_table.attach(email_label,1,2,1,2,gtk.EXPAND|gtk.FILL)

        self.use_mail_from=gtk.CheckButton(_("Use different From field in mail replies"))
        self.use_mail_from.connect("clicked",self.change_mail_from_status)
        self.mail_nick_entry=gtk.Entry()
        self.mail_email_entry=gtk.Entry()
        self.mail_nick_label=gtk.Label(_("Name or NickName (for Mail replies)"))
        self.mail_nick_label.set_size_request(200,-1)
        self.mail_nick_label.set_alignment(0,0.5)
        self.mail_email_label=gtk.Label(_("E-Mail address (for Mail replies)"))
        self.mail_email_label.set_alignment(0,0.5)

        id_table.attach(self.use_mail_from,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        id_table.attach(self.mail_nick_entry,0,1,4,5,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        id_table.attach(self.mail_email_entry,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        id_table.attach(self.mail_nick_label,1,2,4,5,gtk.EXPAND|gtk.FILL)
        id_table.attach(self.mail_email_label,1,2,5,6,gtk.EXPAND|gtk.FILL)

        id_vbox.pack_start(id_table,False,True,4)



        label_posting_profile=gtk.Label("<b>"+_("Body")+"</b>")
        label_posting_profile.set_use_markup(True)
        
        posting_profile_vbox=gtk.VBox()
        
        label_posting_profile_2=gtk.Label("<b>"+_("Headers")+"</b>")
        label_posting_profile_2.set_use_markup(True)
        
        posting_profile_vbox_2=gtk.VBox()

        compose_vbox=gtk.VBox()
        compose_label=gtk.Label("<b>"+_("Compose")+"</b>")
        compose_label.set_alignment(0,0.5)
        compose_label.set_use_markup(True)
        compose_vbox.set_border_width(4)
        compose_vbox.pack_start(compose_label,False,False,4)

        compose_table=gtk.Table(2,2,False)
        compose_table.set_border_width(4)

        wrap_label=gtk.Label(_("  Wrap column"))
        self.wrap_spinbutton=gtk.SpinButton(gtk.Adjustment(value=72,lower=0,upper=79,step_incr=1,page_incr=10))
        wrap_fake_hbox=gtk.HBox()
        wrap_fake_hbox.pack_start(self.wrap_spinbutton,False,False)
        wrap_fake_hbox.pack_start(wrap_label,False,True)
        attribution_label=gtk.Label(_("Attribution line"))
        attribution_label.set_alignment(0,0.5)
        self.attribution_entry=gtk.Entry()
        attribution_label.set_size_request(230,-1)
        attribution_tooltip=gtk.Tooltips()
        attribution_tooltip.set_tip(self.attribution_entry,_("%s = Subject\n%g = Newsgroups\n%f = From\n%n = Nick\n%e = Email\n%d = Date"))

        compose_table.attach(wrap_fake_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.SHRINK,16)
        compose_table.attach(self.attribution_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.SHRINK,16)
        compose_table.attach(attribution_label,1,2,1,2,gtk.FILL,gtk.EXPAND|gtk.FILL,4)

        compose_vbox.pack_start(compose_table,False,False)

        posting_profile_vbox.pack_start(compose_vbox,False,True)

        sign_vbox=gtk.VBox()
        sign_label=gtk.Label("<b>"+_("Signature")+"</b>")
        sign_label.set_alignment(0,0.5)
        sign_label.set_use_markup(True)
        sign_vbox.set_border_width(4)
        sign_table=gtk.Table(2,2,False)
        sign_table.set_border_width(4)
        sign_vbox.pack_start(sign_label,False,False,4)

        self.sign_entry=gtk.Entry()

        self.tags_checkbutton=gtk.CheckButton(_("Use random taglines"))
        sign_button=gtk.Button(_("Change Signature Path"))
        sign_button.set_size_request(230,-1)

        sign_button.connect("clicked",self.open_filesel_dialog)
        tags_button=gtk.Button(_("Add a Tagline"))
        tags_button.connect("clicked",self.add_tag_line)

        sign_table.attach(self.sign_entry,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL|gtk.EXPAND,16)
        sign_table.attach(self.tags_checkbutton,0,1,1,2,gtk.SHRINK|gtk.FILL,gtk.FILL|gtk.EXPAND,16)
        sign_table.attach(sign_button,1,2,0,1,gtk.FILL,gtk.SHRINK,4)
        sign_table.attach(tags_button,1,2,1,2,gtk.FILL,gtk.SHRINK,4)

        sign_vbox.pack_start(sign_table,False,False)
        posting_profile_vbox.pack_start(sign_vbox,False,True)

        #optional headers frame
        opt_headers_vbox=gtk.VBox()
        opt_headers_label=gtk.Label("<b>"+_("Optional Headers")+"</b>")
        opt_headers_label.set_alignment(0,0.5)
        opt_headers_label.set_use_markup(True)
        opt_headers_vbox.pack_start(opt_headers_label,False,False,4)
        opt_headers_vbox.set_border_width(4)

        opt_headers_table=gtk.Table(3,2,False)
        opt_headers_table.set_border_width(4)

        self.reply_to_entry=gtk.Entry()
        self.organization_entry=gtk.Entry()
        self.mail_copies_to_entry=gtk.Entry()

        reply_to_label=gtk.Label(_("Reply-To"))
        reply_to_label.set_alignment(0,0.5)
        reply_to_label.set_size_request(110,-1)
        organization_label=gtk.Label(_("Organization"))
        organization_label.set_alignment(0,0.5)
        mail_copies_to_label=gtk.Label(_("Mail-Copies-To"))
        mail_copies_to_label.set_alignment(0,0.5)

        opt_headers_table.attach(self.reply_to_entry,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        opt_headers_table.attach(self.organization_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        opt_headers_table.attach(self.mail_copies_to_entry,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        opt_headers_table.attach(reply_to_label,1,2,0,1,gtk.EXPAND|gtk.FILL)
        opt_headers_table.attach(organization_label,1,2,1,2,gtk.EXPAND|gtk.FILL)
        opt_headers_table.attach(mail_copies_to_label,1,2,2,3,gtk.EXPAND|gtk.FILL)

        opt_headers_vbox.pack_start(opt_headers_table,False,False)
        
        posting_profile_vbox_2.pack_start(opt_headers_vbox,False,True)
        
        message_id_vbox=gtk.VBox()
        message_id_vbox.set_border_width(4)
        message_id_label=gtk.Label("<b>"+_("Message-ID")+"</b>")
        message_id_label.set_alignment(0,0.5)
        message_id_label.set_use_markup(True)
        message_id_vbox.pack_start(message_id_label,False,False,4)
        message_id_table=gtk.Table(2,2,False)
        message_id_table.set_border_width(4)
        self.generate_mid_checkbutton=gtk.CheckButton(_("Generate Message-ID"))
        self.generate_mid_checkbutton.connect("clicked",self.change_mid_status)
        self.fqdn_entry=gtk.Entry()
        fqdn_tooltip=gtk.Tooltips()
        fqdn_tooltip.set_tip(self.fqdn_entry,_("You can write here a FQDN (Fully Qualified Domain Name) that will be used to compose the Message-ID.\nOtherwise if you leave this field blank XPN will use your Host Name."))

        self.fqdn_label=gtk.Label(_("Fully Qualified Domain Name"))
        self.fqdn_label.set_alignment(0,0.5)
        message_id_table.attach(self.generate_mid_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        message_id_table.attach(self.fqdn_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16)
        message_id_table.attach(self.fqdn_label,1,2,1,2,gtk.EXPAND|gtk.FILL)
        message_id_vbox.pack_start(message_id_table,False,False)
        
        posting_profile_vbox_2.pack_start(message_id_vbox,False,True)
        
        custom_headers_vbox=gtk.VBox()
        custom_headers_vbox.set_border_width(4)
        custom_headers_label=gtk.Label("<b>"+_("Custom Headers (X-Headers)")+"</b>")
        custom_headers_label.set_alignment(0,0.5)
        custom_headers_label.set_use_markup(True)
        custom_headers_vbox.pack_start(custom_headers_label,False,False,4)
        custom_headers_scrolledwin=gtk.ScrolledWindow()
        custom_headers_scrolledwin.set_border_width(4)
        custom_headers_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        custom_headers_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.custom_headers_buffer=gtk.TextBuffer()
        self.custom_headers_textview=gtk.TextView(self.custom_headers_buffer)

        custom_headers_scrolledwin.add(self.custom_headers_textview)
        custom_headers_vbox.pack_start(custom_headers_scrolledwin,True,True)
        
        posting_profile_vbox_2.pack_start(custom_headers_vbox,True,True)

        notebook.append_page(id_vbox,id_page_label)
        notebook.append_page(posting_profile_vbox,label_posting_profile)
        notebook.append_page(posting_profile_vbox_2,label_posting_profile_2)


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


        win_vbox.pack_start(id_entry_hbox,False,False,10)
        win_vbox.pack_start(notebook,False,False,0)
        win_vbox.pack_start(buttons_hbox,False,False,0)
        self.win.add(win_vbox)
        if id_to_load: self.load_configs(id_to_load)
        else: self.load_defaults()


