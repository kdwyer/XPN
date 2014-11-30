import gtk
import pango
import gobject
import webbrowser
import os
import gettext
import ConfigParser
from xpn_src.Config_File import Config_File
from xpn_src.add_tag import Tags_Window
from xpn_src.Charset_List import encodings_list, encodings_tip, CharsetList
from xpn_src.Headers_List import HeadersList
from xpn_src.UserDir import get_wdir
from xpn_src.Connections_Handler import Connection, SSLConnection
from xpn_src.Server_Win import NNTPServer_Win
from xpn_src.ID_Win import ID_Win


class Config_Win:
    def show(self):
        self.win.show_all()

    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,obj):
        self.win.destroy()


    def gdkcolor_to_hex(self,gdk_color):
        colors=[gdk_color.red,gdk_color.green,gdk_color.blue]
        colors= [("0"+str(hex(col*255/65535))[2:])[-2:].upper() for col in (colors)]
        color = "#"+colors[0]+colors[1]+colors[2]
        return color

    def update_text_color_entry(self,obj):
        color=obj.get_color()
        color=self.gdkcolor_to_hex(color)
        if obj==self.text_color_button:
            self.apply_text_color(self.text_color_entry,obj,color)
        elif obj==self.quote1_color_button:
            self.apply_text_color(self.quote1_color_entry,obj,color)
        elif obj==self.quote2_color_button:
            self.apply_text_color(self.quote2_color_entry,obj,color)
        elif obj==self.quote3_color_button:
            self.apply_text_color(self.quote3_color_entry,obj,color)
        elif obj==self.sign_color_button:
            self.apply_text_color(self.sign_color_entry,obj,color)
        elif obj==self.url_color_button:
            self.apply_text_color(self.url_color_entry,obj,color)
        else:
            self.apply_text_color(self.headers_color_entry,obj,color)


    def update_back_color_entry(self,obj):
        color=obj.get_color()
        color=self.gdkcolor_to_hex(color)
        self.apply_back_color(obj,color)

    def apply_text_color(self,widget,button,color):
        style=widget.get_style().copy()
        gdk_color=gtk.gdk.color_parse(color)
        style.text[gtk.STATE_NORMAL]=gdk_color
        button.set_color(gdk_color)
        widget.set_style(style)

    def apply_back_color(self,button,color):
        if not button==self.headers_bg_color_button:
            style=self.text_color_entry.get_style().copy()
            gdk_color=gtk.gdk.color_parse(color)
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.text_color_entry.set_style(style)
            style=self.quote1_color_entry.get_style().copy()
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.quote1_color_entry.set_style(style)
            style=self.quote2_color_entry.get_style().copy()
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.quote2_color_entry.set_style(style)
            style=self.quote3_color_entry.get_style().copy()
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.quote3_color_entry.set_style(style)
            style=self.sign_color_entry.get_style().copy()
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.sign_color_entry.set_style(style)
            self.background2_color_label.set_text(color)
            style=self.url_color_entry.get_style().copy()
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.url_color_entry.set_style(style)
        else:
            style=self.headers_color_entry.get_style().copy()
            gdk_color=gtk.gdk.color_parse(color)
            style.base[gtk.STATE_NORMAL]=gdk_color
            self.headers_color_entry.set_style(style)
            self.headers2_bg_color_label.set_text(color)
        button.set_color(gdk_color)


    def get_text_color(self,widget):
        style=widget.get_style().copy()
        gdk_color=style.text[gtk.STATE_NORMAL]
        color=self.gdkcolor_to_hex(gdk_color)
        return color

    def get_back_color(self,widget):
        style=widget.get_style().copy()
        gdk_color=style.base[gtk.STATE_NORMAL]
        color=self.gdkcolor_to_hex(gdk_color)
        return color


    def update_all(self,configs):
        self.mail_server_entry.set_text(configs["smtp_server"])
        self.mail_port_entry.set_text(configs["smtp_port"])
        if configs["smtp_auth"]=="True":
            self.mail_server_auth_checkbutton.set_active(True)
        else:
            self.mail_server_auth_checkbutton.set_active(False)
            self.mail_server_username.set_sensitive(False)
            self.mail_server_password.set_sensitive(False)
            self.mail_username_label.set_sensitive(False)
            self.mail_password_label.set_sensitive(False)
        self.mail_server_username.set_text(configs["smtp_username"])
        self.mail_server_password.set_text(configs["smtp_password"])


        self.font_article_button.set_font_name(configs["font_name"].encode("utf-8"))
        self.font_threads_button.set_font_name(configs["font_threads_name"].encode("utf-8"))
        self.font_groups_button.set_font_name(configs["font_groups_name"].encode("utf-8"))
        self.use_system_fonts_checkbutton.set_active(configs.get("use_system_fonts","True")=="True")
        self.change_fonts_status(None)

        self.apply_back_color(self.background_color_button,configs["background_color"])
        self.text_color_entry.set_text("Text Color")
        self.apply_text_color(self.text_color_entry,self.text_color_button,configs["text_color"])
        self.quote1_color_entry.set_text(">Quoted Text Level 1 Color")
        self.apply_text_color(self.quote1_color_entry,self.quote1_color_button,configs["quote1_color"])
        self.quote2_color_entry.set_text(">Quoted Text Level 2 Color")
        self.apply_text_color(self.quote2_color_entry,self.quote2_color_button,configs["quote2_color"])
        self.quote3_color_entry.set_text(">Quoted Text Level 3 Color")
        self.apply_text_color(self.quote3_color_entry,self.quote3_color_button,configs["quote3_color"])
        self.sign_color_entry.set_text("Sign Color")
        self.apply_text_color(self.sign_color_entry,self.sign_color_button,configs["sign_color"])
        self.url_color_entry.set_text("http://xpn.altervista.org")
        self.apply_text_color(self.url_color_entry,self.url_color_button,configs["url_color"])
        self.headers_color_entry.set_text("Header: sample")
        self.apply_text_color(self.headers_color_entry,self.headers_fg_color_button,configs["headers_fg_color"])
        self.apply_back_color(self.headers_bg_color_button,configs["headers_bg_color"])
        self.layout_radiobuttons[0].set_active(True)
        layout_number=int(self.configs["layout"])
        self.layout_radiobuttons[layout_number-1].set_active(True)
        if self.configs["exp_column"]=="From":
            self.thread_exp_radiobutton2.set_active(True)
        else:
            self.thread_exp_radiobutton1.set_active(True)
        self.headers_checkbutton.set_active(configs.get("show_headers","False")=="True")
        self.oneclick_checkbutton.set_active(configs.get("oneclick","False")=="True")
        self.advance_on_mark_checkbutton.set_active(configs.get("advance_on_mark","False")=="True")
        self.oneclick_article_checkbutton.set_active(configs.get("oneclick_article","False")=="True")
        self.expand_groups_checkbutton.set_active(configs.get("expand_group","False")=="True")
        self.one_key_spin.set_value(int(configs["scroll_fraction"]))
        self.sort_order_checkbutton.set_active(configs.get("ascend_order","False")=="True")
        self.sort_combo.child.set_text(configs["sort_col"].encode("utf-8").capitalize())
        self.fallback_charset_combo.child.set_text(configs["fallback_charset"])
 

        if configs["custom_browser"]=="True":
            self.browser_checkbutton.set_active(True)
            self.browser_entry.set_text(configs["browser_launcher"].encode("utf-8"))
        else:
            self.browser_checkbutton.set_active(False)
            self.browser_entry.set_sensitive(False)

      
            
        self.editor_checkbutton.set_active(eval(configs["external_editor"]))
        self.editor_entry.set_text(configs["editor_launcher"].encode("utf-8"))

        self.purge_read_spinbutton.set_value(int(configs["purge_read"]))
        self.purge_unread_spinbutton.set_value(int(configs["purge_unread"]))

        
            
        self.download_bodies_checkbutton.set_active(eval(configs["download_bodies"]))

        
        if configs["limit_articles"]=="True":
            self.limit_articles_checkbutton.set_active(True)
            self.limit_articles_spinbutton.set_sensitive(True)
        else:
            self.limit_articles_spinbutton.set_sensitive(False)

        self.limit_articles_spinbutton.set_value(int(configs["limit_articles_number"]))
        if configs["automatic_download"]=="True":
            self.auto_download_checkbutton.set_active(True)
            self.auto_download_spinbutton.set_sensitive(True)
        else:
            self.auto_download_spinbutton.set_sensitive(False)

        self.auto_download_spinbutton.set_value(int(configs["download_timeout"]))
        
        try: self.configs["threading_method"]               # upgrading check 
        except KeyError: self.config["threading_method"]=2 # upgrading check 
        
        if self.configs["threading_method"]=="1":
            self.threading_method_radiobutton1.set_active(True)
        else:
            self.threading_method_radiobutton2.set_active(True)
        
        if self.configs["lang"]=="en":
            self.lang_en_radiobutton.set_active(True)
        elif configs["lang"]=="it":
            self.lang_it_radiobutton.set_active(True)
        elif configs["lang"]=="fr":
            self.lang_fr_radiobutton.set_active(True)
        elif configs["lang"]=="de":
            self.lang_de_radiobutton.set_active(True)
        else:
            self.lang_en_radiobutton.set_active(True)




    def save_configs(self,object,conf):
        conf.configs["smtp_server"]=self.mail_server_entry.get_text().decode("utf-8")
        conf.configs["smtp_port"]=self.mail_port_entry.get_text()
        if self.mail_server_auth_checkbutton.get_active():
            conf.configs["smtp_auth"]="True"
            conf.configs["smtp_username"]=self.mail_server_username.get_text()
            conf.configs["smtp_password"]=self.mail_server_password.get_text()
        else:
            conf.configs["smtp_auth"]="False"
            conf.configs["smtp_username"]=""
            conf.configs["smtp_password"]=""



        conf.configs["font_name"]=self.font_article_button.get_font_name()
        conf.configs["font_threads_name"]=self.font_threads_button.get_font_name()
        conf.configs["font_groups_name"]=self.font_groups_button.get_font_name()
        conf.configs["use_system_fonts"]=str(bool(self.use_system_fonts_checkbutton.get_active()))
        conf.configs["text_color"]=self.get_text_color(self.text_color_entry)
        conf.configs["quote1_color"]=self.get_text_color(self.quote1_color_entry)
        conf.configs["quote2_color"]=self.get_text_color(self.quote2_color_entry)
        conf.configs["quote3_color"]=self.get_text_color(self.quote3_color_entry)
        conf.configs["sign_color"]=self.get_text_color(self.sign_color_entry)
        conf.configs["background_color"]=self.get_back_color(self.text_color_entry)
        conf.configs["url_color"]=self.get_text_color(self.url_color_entry)
        conf.configs["headers_fg_color"]=self.get_text_color(self.headers_color_entry)
        conf.configs["headers_bg_color"]=self.get_back_color(self.headers_color_entry)
        for rbutton in self.layout_radiobuttons:
            if rbutton.get_active():
                conf.configs["layout"]=str(self.layout_radiobuttons.index(rbutton)+1)
                break
        if self.thread_exp_radiobutton1.get_active():
            conf.configs["exp_column"]="Subject"
        else:
            conf.configs["exp_column"]="From"
        conf.configs["show_headers"]=str(bool(self.headers_checkbutton.get_active()))
        conf.configs["oneclick"]=str(bool(self.oneclick_checkbutton.get_active()))
        conf.configs["advance_on_mark"]=str(bool(self.advance_on_mark_checkbutton.get_active()))
        conf.configs["oneclick_article"]=str(bool(self.oneclick_article_checkbutton.get_active()))
        conf.configs["expand_group"]=str(bool(self.expand_groups_checkbutton.get_active()))
        conf.configs["scroll_fraction"]=repr(self.one_key_spin.get_value_as_int())
        conf.configs["sort_col"]=self.sort_combo.child.get_text().decode("utf-8")
        conf.configs["ascend_order"]=str(bool(self.sort_order_checkbutton.get_active()))
        conf.configs["fallback_charset"]=self.fallback_charset_combo.child.get_text()

#        if self.browser_checkbutton.get_active() and self.browser_entry.get_text().strip() and \
#           self.exists(self.browser_entry.get_text().strip()):
        if self.browser_checkbutton.get_active() and self.browser_entry.get_text().strip():
            conf.configs["custom_browser"]="True"
            conf.configs["browser_launcher"]=self.browser_entry.get_text().decode("utf-8")
        else:
            conf.configs["custom_browser"]="False"
            conf.configs["browser_launcher"]=""
        if self.exists(self.editor_entry.get_text().strip()):
            conf.configs["editor_launcher"]=self.editor_entry.get_text().decode("utf-8")
        else:
            conf.configs["editor_launcher"]=""
        conf.configs["external_editor"]=str(bool(self.editor_checkbutton.get_active()))

        conf.configs["purge_read"]=repr(self.purge_read_spinbutton.get_value_as_int())
        conf.configs["purge_unread"]=repr(self.purge_unread_spinbutton.get_value_as_int())
        conf.configs["download_bodies"]=repr(bool(self.download_bodies_checkbutton.get_active()))
        conf.configs["limit_articles"]=repr(bool(self.limit_articles_checkbutton.get_active()))
        conf.configs["limit_articles_number"]=repr(self.limit_articles_spinbutton.get_value_as_int())

        conf.configs["automatic_download"]=repr(bool(self.auto_download_checkbutton.get_active()))
        conf.configs["download_timeout"]=repr(self.auto_download_spinbutton.get_value_as_int())
        
        if self.threading_method_radiobutton1.get_active():
            conf.configs["threading_method"]="1"
        else:
            conf.configs["threading_method"]="2"
            
        if self.lang_en_radiobutton.get_active():
            conf.configs["lang"]="en"
        elif self.lang_it_radiobutton.get_active():
            conf.configs["lang"]="it"
        elif self.lang_fr_radiobutton.get_active():
            conf.configs["lang"]="fr"
        elif self.lang_de_radiobutton.get_active():
            conf.configs["lang"]="de"
        else:
            conf.configs["lang"]="en"

        conf.write_configs()
        self.win.destroy()
        self.apply_changes(conf.configs)


    def exists(self, text):
        result=text.rfind("%s")
        ## if the string doesn't exist result=-1, we return 0
        return result+1

    def apply_changes(self,configs):
        #change the font
        if self.use_system_fonts_checkbutton.get_active():
            self.main_win.article_pane.textview.modify_font(pango.FontDescription(""))
            self.main_win.threads_pane.threads_tree.modify_font(pango.FontDescription(""))
            self.main_win.groups_pane.groups_list.modify_font(pango.FontDescription(""))
        else:
            if configs["fixed"]=="False":
                self.main_win.article_pane.textview.modify_font(pango.FontDescription(configs["font_name"]))
            self.main_win.threads_pane.threads_tree.modify_font(pango.FontDescription(configs["font_threads_name"]))
            self.main_win.groups_pane.groups_list.modify_font(pango.FontDescription(configs["font_groups_name"]))

        #show-hide headers
        to_show = configs["show_headers"]=="True"
        self.main_win.article_pane.expander.set_expanded(to_show)
        #update_colors
        self.main_win.article_pane.set_text_color(configs["text_color"])
        self.main_win.article_pane.set_quote_color(configs["quote1_color"],1)
        self.main_win.article_pane.set_quote_color(configs["quote2_color"],2)
        self.main_win.article_pane.set_quote_color(configs["quote3_color"],3)
        self.main_win.article_pane.set_sign_color(configs["sign_color"])
        self.main_win.article_pane.set_background(configs["background_color"])
        self.main_win.article_pane.set_url_color(configs["url_color"])
        self.main_win.article_pane.set_headers_colors(configs["headers_bg_color"],configs["headers_fg_color"])        
        self.main_win.groups_pane.set_background(configs["background_color"])
        self.main_win.groups_pane.set_foreground(configs["text_color"])
        self.main_win.threads_pane.set_background(configs["background_color"])
        self.main_win.threads_pane.set_foreground(configs["text_color"])

        #show thread cause possible sorting changes
        self.main_win.show_threads(self.main_win.groups_pane.get_first_selected_group())
            


        #update expander column
        
        self.main_win.threads_pane.threads_tree.remove_column(self.main_win.threads_pane.column2)
        self.main_win.threads_pane.threads_tree.remove_column(self.main_win.threads_pane.column3)
        if configs["exp_column"]=="From":
            self.main_win.threads_pane.threads_tree.insert_column(self.main_win.threads_pane.column3,1)
            self.main_win.threads_pane.threads_tree.insert_column(self.main_win.threads_pane.column2,2)
            self.main_win.threads_pane.threads_tree.set_expander_column(self.main_win.threads_pane.column3)
            
        else:
            self.main_win.threads_pane.threads_tree.insert_column(self.main_win.threads_pane.column2,1)
            self.main_win.threads_pane.threads_tree.insert_column(self.main_win.threads_pane.column3,2)
            self.main_win.threads_pane.threads_tree.set_expander_column(self.main_win.threads_pane.column2)




        #update browser launcher
        if configs["custom_browser"]=="True":
            self.main_win.article_pane.use_custom_browser=True
            webbrowser.register("xpn_launcher",None,webbrowser.GenericBrowser(configs["browser_launcher"]))
        else:
            self.main_win.article_pane.use_custom_browser=False

        #udatep headers shown
        self.main_win.article_pane.repopulate_headers()
        #update connection
        for connection in self.main_win.connectionsPool.itervalues():
            connection.closeConnection()

        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.main_win.connectionsPool=dict()
        for server in cp.sections():
            if cp.get(server,"nntp_use_ssl")=="True":
                self.main_win.connectionsPool[server]=SSLConnection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
            else:
                self.main_win.connectionsPool[server]=Connection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))

    def update_layout(self,obj,configs=None,layout_number=0):
        #update_layout
        layout_methods = {"1":self.main_win.build_layout_type_1,
                          "2":self.main_win.build_layout_type_2,
                          "3":self.main_win.build_layout_type_3,
                          "4":self.main_win.build_layout_type_4
                         }
        if configs:
            r,c=divmod(int(configs["layout"])-1,6)
        else:
            r,c=divmod(layout_number-1,6)
        layout_builder = layout_methods.get(str(r+1), None)
        if layout_builder: layout_builder(c+1)
        else: self.main_win.build_layout_type_1(1)   # If there is no layout associated to
                                            # self.configs["layout"] then build 1
        self.main_win.set_sizes()
        
    def change_fonts_status(self,obj):
        status=self.use_system_fonts_checkbutton.get_active()
        self.font_article_hbox.set_sensitive(not status)
        self.font_threads_hbox.set_sensitive(not status)
        self.font_groups_hbox.set_sensitive(not status)

    def change_mid_status(self,obj):
        status=self.generate_mid_checkbutton.get_active()
        self.fqdn_entry.set_sensitive(status)
        self.fqdn_label.set_sensitive(status)

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

        
    def change_mail_auth_status(self,obj):
        status=self.mail_server_auth_checkbutton.get_active()
        self.mail_server_username.set_sensitive(status)
        self.mail_server_password.set_sensitive(status)
        self.mail_username_label.set_sensitive(status)
        self.mail_password_label.set_sensitive(status)
    

            
    def change_browser_status(self,obj):
        status=self.browser_checkbutton.get_active()
        self.browser_label.set_sensitive(status)
        self.browser_entry.set_sensitive(status)

    def change_limit_status(self,obj):
        status=self.limit_articles_checkbutton.get_active()
        self.limit_articles_spinbutton.set_sensitive(status)

    def change_auto_download_status(self,obj):
        status=self.auto_download_checkbutton.get_active()
        self.auto_download_spinbutton.set_sensitive(status)

    def add_tag_line(self,obj):
        tag_win=Tags_Window()

    def open_charset_list_win(self,obj):
        charset_list_win=CharsetList()
    
    def open_headers_list_win(self,obj):
        headers_list_win=HeadersList()

    def insert_rb(self,name,icon_name,shortname,tooltip,group=None):
        icon=gtk.Image()
        icon.set_from_file("pixmaps/"+icon_name)
        label=gtk.Label("<b>"+name+"</b>")

        label.set_use_markup(True)
        radiobutton=gtk.RadioButton(group)
        radiobutton.set_mode(False)
        radiobutton.set_relief( gtk.RELIEF_NONE )
        b_vbox=gtk.VBox()
        radiobutton.add(b_vbox)
        b_vbox.pack_start(icon,True,True,2)
        b_vbox.pack_start(label,True,True,2)
        self.left_buttons.pack_start(radiobutton,True,True,2)
        self.buttons[shortname]=radiobutton
        radiobutton.connect("released",self.show_config_pages,shortname)

    def show_config_pages(self,obj,name):
        current_notebook=self.main_hbox.get_children()[1]
        self.main_hbox.remove(current_notebook)
        if name=="server":
            self.main_hbox.pack_start(self.server_page,True,True,4)
        if name=="user":
            self.main_hbox.pack_start(self.user_page,True,True,4)        
        if name=="display":
            self.main_hbox.pack_start(self.display_page,True,True,4)
        if name=="groups":
            self.main_hbox.pack_start(self.groups_page,True,True,4)
        if name=="misc":
            self.main_hbox.pack_start(self.misc_page,True,True,4)
        self.main_hbox.show_all()

    def refresh_server_list(self):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.server_model.clear()
        for server in cp.sections():self.server_model.append([server])

    def refresh_id_list(self):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","id.txt"))
        self.id_model.clear()
        for id in cp.sections():self.id_model.append([id])

    def build_server_page(self):
        notebook=gtk.Notebook()
        label_server=gtk.Label("<b>"+_("Servers")+"</b>")
        label_server.set_use_markup(True)
        
        server_profile_vbox=gtk.VBox()
        
        
        server_label=gtk.Label("<b>"+_("NNTP Servers")+"</b>")
        server_label.set_alignment(0,0.5)
        server_label.set_use_markup(True)
        server_vbox=gtk.VBox()
        server_vbox.set_border_width(4)
        server_table=gtk.Table(5,2,False)
        server_table.set_border_width(4)
        server_vbox.pack_start(server_label,True,True)
        server_vbox.pack_start(server_table,True,True)

        def add_edit_server(button):
            if button==edit_button:
                model,iter_selected= server_list.get_selection().get_selected()
                if iter_selected:
                    server= self.server_model.get_value(iter_selected,0)
                    win=NNTPServer_Win(self,server)
                    win.show()            
            else:
                win=NNTPServer_Win(self)
                win.show()
            self.refresh_server_list()
                    
                

        def remove_server(button):
            model,iter_selected= server_list.get_selection().get_selected()
            if iter_selected:
                server= self.server_model.get_value(iter_selected,0)
                cp=ConfigParser.ConfigParser()
                cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
                cp.remove_section(server)
                cp.write(file(os.path.join(get_wdir(),"dats","servers.txt"),"w"))
            self.refresh_server_list()

        def server_list_row_clicked(*params):
            add_edit_server(edit_button)

        add_button=gtk.Button(None,gtk.STOCK_ADD)
        add_button_tooltip=gtk.Tooltips()
        add_button_tooltip.set_tip(add_button,_("Add a Server"))
        add_button.connect("clicked",add_edit_server)
        add_button.set_border_width(5)

        edit_button=gtk.Button(None,gtk.STOCK_EDIT)
        edit_button_tooltip=gtk.Tooltips()
        edit_button_tooltip.set_tip(edit_button,_("Edit Selected Server"))
        edit_button.connect("clicked",add_edit_server)
        edit_button.set_border_width(5)

        remove_button=gtk.Button(None,gtk.STOCK_REMOVE)
        remove_button_tooltip=gtk.Tooltips()
        remove_button_tooltip.set_tip(remove_button,_("Remove Selected Server"))
        remove_button.connect("clicked",remove_server)
        remove_button.set_border_width(5)


        server_scrolledwin=gtk.ScrolledWindow()
        server_scrolledwin.set_border_width(4)
        server_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        server_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        server_list=gtk.TreeView() 
        server_list.connect("row_activated",server_list_row_clicked)
        server_list.set_border_width(4)
        self.server_model=gtk.ListStore(gobject.TYPE_STRING)
        server_scrolledwin.add(server_list)
        server_list.set_model(self.server_model)
        text_renderer=gtk.CellRendererText()
        server_column=gtk.TreeViewColumn(_("List"),text_renderer,text=0)
        server_list.append_column(server_column)
        server_list.set_rules_hint(True)
        server_list.set_headers_visible(False)
        self.refresh_server_list()
        server_table.attach(server_scrolledwin,0,1,0,3,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        server_table.attach(add_button,1,2,0,1,gtk.FILL)
        server_table.attach(edit_button,1,2,1,2,gtk.FILL)
        server_table.attach(remove_button,1,2,2,3,gtk.FILL)

        server_profile_vbox.pack_start(server_vbox,True,True)

        mail_server_label=gtk.Label("<b>"+_("SMTP Server")+"</b>")
        mail_server_label.set_alignment(0,0.5)
        mail_server_label.set_use_markup(True)
        mail_server_vbox=gtk.VBox()
        mail_server_vbox.set_border_width(4)
        mail_server_vbox.pack_start(mail_server_label,False,True)
        
        mail_server_table=gtk.Table(4,2,False)
        mail_server_table.set_border_width(8)


        self.mail_port_entry=gtk.Entry()
        self.mail_port_entry.set_size_request(30,-1)
        self.mail_server_entry=gtk.Entry()
        mail_server_port_hbox=gtk.HBox()
        mail_server_port_hbox.pack_start(self.mail_server_entry,True,True)
        mail_server_port_hbox.pack_start(self.mail_port_entry,False,False,4)
        self.mail_server_username=gtk.Entry()
        self.mail_server_password=gtk.Entry()
        self.mail_server_password.set_visibility(False)
        self.mail_server_auth_checkbutton=gtk.CheckButton(_("Server requires authentication"))
        self.mail_server_auth_checkbutton.connect("clicked",self.change_mail_auth_status)

        mail_server_entry_label=gtk.Label(_("SMTP Server Address | Port Number"))
        mail_server_entry_label.set_size_request(230,-1)
        mail_server_entry_label.set_alignment(0,0.5)
        self.mail_username_label=gtk.Label(_("Username"))
        self.mail_username_label.set_size_request(230,-1)
        self.mail_username_label.set_alignment(0,0.5)
        self.mail_password_label=gtk.Label(_("Password"))
        self.mail_password_label.set_alignment(0,0.5)
        mail_auth_label=gtk.Label("")

        mail_server_table.attach(mail_server_port_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        mail_server_table.attach(self.mail_server_auth_checkbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        mail_server_table.attach(self.mail_server_username,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        mail_server_table.attach(self.mail_server_password,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        mail_server_table.attach(mail_server_entry_label,1,2,0,1,gtk.EXPAND|gtk.FILL)
        mail_server_table.attach(mail_auth_label,1,2,1,2,gtk.EXPAND|gtk.FILL)
        mail_server_table.attach(self.mail_username_label,1,2,2,3,gtk.EXPAND|gtk.FILL)
        mail_server_table.attach(self.mail_password_label,1,2,3,4,gtk.EXPAND|gtk.FILL)

        mail_server_vbox.pack_start(mail_server_table,False,False)
        
        server_profile_vbox.pack_start(mail_server_vbox,True,True)
       
        notebook.append_page(server_profile_vbox,label_server)

        return notebook

        
    def build_user_page(self):
        notebook=gtk.Notebook()
        label_user=gtk.Label("<b>"+_("User Profile")+"</b>")
        label_user.set_use_markup(True)




        def add_edit_id(button):
            if button==edit_button:
                model,iter_selected= id_list.get_selection().get_selected()
                if iter_selected:
                    id= self.id_model.get_value(iter_selected,0)
                    win=ID_Win(self,id)
                    win.show()            
            else:
                win=ID_Win(self)
                win.show()
            self.refresh_id_list()
                    
                

        def remove_id(button):
            model,iter_selected= id_list.get_selection().get_selected()
            if iter_selected:
                id= self.id_model.get_value(iter_selected,0)
                cp=ConfigParser.ConfigParser()
                cp.read(os.path.join(get_wdir(),"dats","id.txt"))
                cp.remove_section(id)
                cp.write(file(os.path.join(get_wdir(),"dats","id.txt"),"w"))
            self.refresh_id_list()

        def id_list_row_clicked(*params):
            add_edit_id(edit_button)

        add_button=gtk.Button(None,gtk.STOCK_ADD)
        add_button_tooltip=gtk.Tooltips()
        add_button_tooltip.set_tip(add_button,_("Add an Identity"))
        add_button.connect("clicked",add_edit_id)
        add_button.set_border_width(5)

        edit_button=gtk.Button(None,gtk.STOCK_EDIT)
        edit_button_tooltip=gtk.Tooltips()
        edit_button_tooltip.set_tip(edit_button,_("Edit Selected Identity"))
        edit_button.connect("clicked",add_edit_id)
        edit_button.set_border_width(5)

        remove_button=gtk.Button(None,gtk.STOCK_REMOVE)
        remove_button_tooltip=gtk.Tooltips()
        remove_button_tooltip.set_tip(remove_button,_("Remove Selected Identity"))
        remove_button.connect("clicked",remove_id)
        remove_button.set_border_width(5)

        user_profile_vbox=gtk.VBox()
        user_profile_vbox.set_border_width(4)
        personal_table=gtk.Table(4,2,False)
        personal_table.set_border_width(8)

        id_scrolledwin=gtk.ScrolledWindow()
        id_scrolledwin.set_border_width(4)
        id_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        id_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        id_list=gtk.TreeView() 
        id_list.connect("row_activated",id_list_row_clicked)
        id_list.set_border_width(4)
        self.id_model=gtk.ListStore(gobject.TYPE_STRING)
        id_scrolledwin.add(id_list)
        id_list.set_model(self.id_model)
        text_renderer=gtk.CellRendererText()
        id_column=gtk.TreeViewColumn(_("List"),text_renderer,text=0)
        id_list.append_column(id_column)
        id_list.set_rules_hint(True)
        id_list.set_headers_visible(False)
        self.refresh_id_list()
        personal_table.attach(id_scrolledwin,0,1,0,3,gtk.EXPAND|gtk.FILL,gtk.FILL,18)
        personal_table.attach(add_button,1,2,0,1,gtk.FILL)
        personal_table.attach(edit_button,1,2,1,2,gtk.FILL)
        personal_table.attach(remove_button,1,2,2,3,gtk.FILL)
 
        user_profile_vbox.pack_start(personal_table,False,False)
        notebook.append_page(user_profile_vbox,label_user)

        return notebook


    
    def build_display_page(self):
        notebook=gtk.Notebook()
        label_display_profile=gtk.Label("<b>"+_("Fonts and Colors")+"</b>")
        label_display_profile.set_use_markup(True)

        
        display_profile_vbox=gtk.VBox()
        display_profile_vbox_2=gtk.VBox()


        font_vbox=gtk.VBox()
        font_label=gtk.Label("<b>"+_("Fonts")+"</b>")
        font_label.set_alignment(0,0.5)
        font_label.set_use_markup(True)
        font_vbox.pack_start(font_label,False,False,4)
        font_vbox.set_border_width(4)
        self.font_article_hbox=gtk.HBox()
        self.font_article_hbox.set_border_width(4)
        font_article_label=gtk.Label(_("Article"))
        font_article_label.set_size_request(68,-1)
        font_article_label.set_alignment(0,0.5)
        self.font_article_hbox.pack_start(font_article_label,False,False,16)
        self.font_article_button=gtk.FontButton(None)
        self.font_article_button.set_use_font(True)
        self.font_article_button.set_use_size(True)
        self.font_article_hbox.pack_start(self.font_article_button,True,True,0)
        
        self.font_threads_hbox=gtk.HBox()
        self.font_threads_hbox.set_border_width(4)
        font_threads_label=gtk.Label(_("Threads"))
        font_threads_label.set_size_request(68,-1)
        font_threads_label.set_alignment(0,0.5)
        self.font_threads_hbox.pack_start(font_threads_label,False,False,16)
        self.font_threads_button=gtk.FontButton(None)
        self.font_threads_button.set_use_font(True)
        self.font_threads_button.set_use_size(True)
        self.font_threads_hbox.pack_start(self.font_threads_button,True,True,0)
        
        self.font_groups_hbox=gtk.HBox()
        self.font_groups_hbox.set_border_width(4)
        font_groups_label=gtk.Label(_("Groups"))
        font_groups_label.set_size_request(68,-1)
        font_groups_label.set_alignment(0,0.5)
        self.font_groups_hbox.pack_start(font_groups_label,False,False,16)
        self.font_groups_button=gtk.FontButton(None)
        self.font_groups_button.set_use_font(True)
        self.font_groups_button.set_use_size(True)
        self.font_groups_hbox.pack_start(self.font_groups_button,True,True,0)
        
        use_system_fonts_hbox=gtk.HBox()
        use_system_fonts_hbox.set_border_width(4)
        self.use_system_fonts_checkbutton=gtk.CheckButton(_("Use System Fonts"))
        use_system_fonts_hbox.pack_start(self.use_system_fonts_checkbutton,False,False,16)
        self.use_system_fonts_checkbutton.connect("clicked",self.change_fonts_status)

        font_vbox.pack_start(use_system_fonts_hbox,False,False)
        font_vbox.pack_start(self.font_article_hbox,False,False)
        font_vbox.pack_start(self.font_threads_hbox,False,False)
        font_vbox.pack_start(self.font_groups_hbox,False,False)


        colors_vbox=gtk.VBox()
        colors_label=gtk.Label("<b>"+_("Colors")+"</b>")
        colors_label.set_alignment(0,0.5)
        colors_label.set_use_markup(True)
        colors_vbox.pack_start(colors_label)

        colors_vbox.set_border_width(4)
        colors_table=gtk.Table(5,3,False)
        colors_table.set_border_width(4)
        text_color_label=gtk.Label(_("Text"))
        text_color_label.set_alignment(0,0.5)
        quote1_color_label=gtk.Label(_("Quote Level 1"))
        quote1_color_label.set_alignment(0,0.5)
        quote1_color_label.set_size_request(80,-1)
        quote2_color_label=gtk.Label(_("Quote Level 2"))
        quote2_color_label.set_alignment(0,0.5)
        quote3_color_label=gtk.Label(_("Quote Level 3"))
        quote3_color_label.set_alignment(0,0.5)
        sign_color_label=gtk.Label(_("Sign"))
        sign_color_label.set_alignment(0,0.5)
        background_color_label=gtk.Label(_("Background"))
        background_color_label.set_alignment(0,0.5)
        self.background2_color_label=gtk.Label("")
        url_color_label=gtk.Label(_("URL"))
        url_color_label.set_alignment(0,0.5)
        self.text_color_entry=gtk.Entry()
        self.text_color_entry.set_editable(False)
        self.quote1_color_entry=gtk.Entry()
        self.quote1_color_entry.set_editable(False)
        self.quote2_color_entry=gtk.Entry()
        self.quote2_color_entry.set_editable(False)
        self.quote3_color_entry=gtk.Entry()
        self.quote3_color_entry.set_editable(False)
        self.sign_color_entry=gtk.Entry()
        self.sign_color_entry.set_editable(False)
        self.url_color_entry=gtk.Entry()
        self.url_color_entry.set_editable(False)
        self.text_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.text_color_button.set_size_request(100,25)
        self.text_color_button.set_title(_("Select Text Color"))
        self.text_color_button.connect("color_set",self.update_text_color_entry)
        self.quote1_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.quote1_color_button.set_size_request(100,25)
        self.quote1_color_button.set_title(_("Select Quote Level 1 Color"))
        self.quote1_color_button.connect("color_set",self.update_text_color_entry)
        self.quote2_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.quote2_color_button.set_size_request(100,25)
        self.quote2_color_button.set_title(_("Select Quote Level 2 Color"))
        self.quote2_color_button.connect("color_set",self.update_text_color_entry)
        self.quote3_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.quote3_color_button.set_size_request(100,25)
        self.quote3_color_button.set_title(_("Select Quote Level 3 Color"))
        self.quote3_color_button.connect("color_set",self.update_text_color_entry)
        self.sign_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.sign_color_button.set_size_request(100,25)
        self.sign_color_button.set_title(_("Select Sign Color"))
        self.sign_color_button.connect("color_set",self.update_text_color_entry)
        self.background_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.background_color_button.set_size_request(100,25)
        self.background_color_button.set_title(_("Select Background Color"))
        self.background_color_button.connect("color_set",self.update_back_color_entry)
        self.url_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.url_color_button.set_size_request(100,25)
        self.url_color_button.set_title(_("Select URL Color"))
        self.url_color_button.connect("color_set",self.update_text_color_entry)




        colors_table.attach(text_color_label,0,1,0,1,gtk.FILL,gtk.FILL,16)
        colors_table.attach(quote1_color_label,0,1,1,2,gtk.FILL,gtk.FILL,16)
        colors_table.attach(quote2_color_label,0,1,2,3,gtk.FILL,gtk.FILL,16)
        colors_table.attach(quote3_color_label,0,1,3,4,gtk.FILL,gtk.FILL,16)
        colors_table.attach(sign_color_label,0,1,4,5,gtk.FILL,gtk.FILL,16)
        colors_table.attach(url_color_label,0,1,5,6,gtk.FILL,gtk.FILL,16)
        colors_table.attach(background_color_label,0,1,6,7,gtk.FILL,gtk.FILL,16)

        colors_table.attach(self.text_color_entry,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.quote1_color_entry,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.quote2_color_entry,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.quote3_color_entry,1,2,3,4,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.sign_color_entry,1,2,4,5,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.url_color_entry,1,2,5,6,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        colors_table.attach(self.background2_color_label,1,2,6,7,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)

        colors_table.attach(self.text_color_button,2,3,0,1,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.quote1_color_button,2,3,1,2,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.quote2_color_button,2,3,2,3,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.quote3_color_button,2,3,3,4,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.sign_color_button,2,3,4,5,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.url_color_button,2,3,5,6,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        colors_table.attach(self.background_color_button,2,3,6,7,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        


        headers_colors_vbox=gtk.VBox()
        headers_colors_label=gtk.Label("<b>"+_("Headers Colors")+"</b>")
        headers_colors_label.set_alignment(0,0.5)
        headers_colors_label.set_use_markup(True)
        self.headers2_bg_color_label=gtk.Label()
        headers_colors_vbox.pack_start(headers_colors_label)
        
        headers_colors_vbox.set_border_width(4)
        headers_colors_table=gtk.Table(5,3,False)
        headers_colors_table.set_border_width(4)

        self.headers_bg_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.headers_bg_color_button.set_size_request(100,25)
        self.headers_bg_color_button.set_title(_("Select Headers Background Color"))
        self.headers_bg_color_button.connect("color_set",self.update_back_color_entry)
        self.headers_fg_color_button=gtk.ColorButton(gtk.gdk.Color(0,0,0))
        self.headers_fg_color_button.set_size_request(100,25)
        self.headers_fg_color_button.set_title(_("Select Headers Foreground Color"))
        self.headers_fg_color_button.connect("color_set",self.update_text_color_entry)
        self.headers_color_entry=gtk.Entry()
        self.headers_color_entry.set_editable(False)
        headers_fg_color_label=gtk.Label(_("Color"))
        headers_fg_color_label.set_alignment(0,0.5)
        headers_fg_color_label.set_size_request(80,-1)
        headers_bg_color_label=gtk.Label(_("Background"))
        headers_bg_color_label.set_alignment(0,0.5)

        headers_colors_table.attach(headers_fg_color_label,0,1,0,1,gtk.FILL,gtk.FILL,16)
        headers_colors_table.attach(headers_bg_color_label,0,1,1,2,gtk.FILL,gtk.FILL,16)
        headers_colors_table.attach(self.headers_color_entry,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        headers_colors_table.attach(self.headers2_bg_color_label,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.SHRINK,2)
        headers_colors_table.attach(self.headers_fg_color_button,2,3,0,1,gtk.EXPAND|gtk.FILL,gtk.SHRINK)
        headers_colors_table.attach(self.headers_bg_color_button,2,3,1,2,gtk.EXPAND|gtk.FILL,gtk.SHRINK)


        colors_vbox.pack_start(colors_table,False,False)
        headers_colors_vbox.pack_start(headers_colors_table,False,False)

        label_display_profile_2=gtk.Label("<b>"+_("Layout")+"</b>")
        label_display_profile_2.set_use_markup(True)

        layout_label=gtk.Label("<b>"+_("Layout")+"</b>")
        layout_label.set_alignment(0,0.5)
        layout_label.set_use_markup(True)
        layout_main_vbox=gtk.VBox()
        layout_main_vbox.set_border_width(4)
        layout_main_vbox.pack_start(layout_label,False,False,4)
        layout_hbox=gtk.HBox()
        #layouts_vbox=gtk.VBox()
        layouts_table=gtk.Table(6,4,False)
        layout_vbox=gtk.VBox()
        self.layout_radiobuttons=[]
        for i in range(24):
            if i == 0: rbutton=gtk.RadioButton()
            else: rbutton=gtk.RadioButton(self.layout_radiobuttons[0])
            layout_image=gtk.Image()
            layout_image.set_from_file("pixmaps/layout_"+str(i+1)+".xpm")
            rbutton.add(layout_image)
            rbutton.connect("clicked",self.update_layout,None,i+1)
            self.layout_radiobuttons.append(rbutton)
            r,c=divmod(i,6)
            layouts_table.attach(rbutton,r,r+1,c,c+1,gtk.FILL,gtk.FILL,12,4)
        
        layout_hbox.pack_start(layouts_table,True,False,2)
        layout_label=gtk.Label(_("G:  Groups Pane\n\nH:  Headers Pane\n\nA:  Article Pane"))
        layout_hbox.pack_start(layout_label,True,False,4)
        layout_vbox.pack_start(layout_hbox,True,True,4)
        
        layout_main_vbox.pack_start(layout_vbox,False,False,16)
       
        art_pane_vbox=gtk.VBox()     
        art_pane_vbox.set_border_width(4)
        art_pane_label=gtk.Label("<b>"+_("Article Pane")+"</b>")
        art_pane_label.set_alignment(0,0.5)
        art_pane_label.set_use_markup(True)
        art_pane_table=gtk.Table(1,1,False)
        art_pane_table.set_border_width(4)
        art_pane_vbox.pack_start(art_pane_label,False,False,4)
 
        self.headers_checkbutton=gtk.CheckButton(_("Display Headers in the Article Pane"))

        self.headers_conf_button=gtk.Button(_("Headers List"))
        headers_conf_button_tooltip=gtk.Tooltips()
        headers_conf_button_tooltip.set_tip(self.headers_conf_button,_("XPN will show these headers on the top of the Article Pane"))
        headers_conf_label=gtk.Label(_("Headers Shown on the Article Pane"))
        self.headers_conf_button.connect("clicked",self.open_headers_list_win)
        art_pane_table.attach(self.headers_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        art_pane_table.attach(self.headers_conf_button,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        art_pane_table.attach(headers_conf_label,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL)
        art_pane_vbox.pack_start(art_pane_table,False,False)



        thread_pane_vbox=gtk.VBox()     
        thread_pane_vbox.set_border_width(4)
        thread_pane_label=gtk.Label("<b>"+_("Threads Pane")+"</b>")
        thread_pane_label.set_alignment(0,0.5)
        thread_pane_label.set_use_markup(True)
        thread_pane_table=gtk.Table(1,1,False)
        thread_pane_table.set_border_width(4)
        thread_pane_vbox.pack_start(thread_pane_label,False,False,4)
        
        thread_pane_label2=gtk.Label(_("Threads expander position"))
        self.thread_exp_radiobutton1=gtk.RadioButton(None,_("Subject Column"))
        self.thread_exp_radiobutton2=gtk.RadioButton(self.thread_exp_radiobutton1,_("From Column"))
        thread_pane_table.attach(self.thread_exp_radiobutton1,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        thread_pane_table.attach(self.thread_exp_radiobutton2,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        thread_pane_table.attach(thread_pane_label2,1,2,0,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        
        thread_pane_vbox.pack_start(thread_pane_table,False,False)

        display_profile_vbox.pack_start(font_vbox,False,True)
        display_profile_vbox.pack_start(colors_vbox,False,True)
        display_profile_vbox.pack_start(headers_colors_vbox,False,True)
        display_profile_vbox_2.pack_start(layout_main_vbox,False,False)
        display_profile_vbox_2.pack_start(art_pane_vbox,False,False)
        display_profile_vbox_2.pack_start(thread_pane_vbox,False,False)


        notebook.append_page(display_profile_vbox,label_display_profile)
        notebook.append_page(display_profile_vbox_2,label_display_profile_2)

        return notebook

    def build_groups_page(self):
        notebook=gtk.Notebook()
        label_groups_download=gtk.Label("<b>"+_("Download")+"</b>")
        label_groups_download.set_use_markup(True)
        label_groups_view=gtk.Label("<b>"+_("Visualization")+"</b>")
        label_groups_view.set_use_markup(True)
        label_groups_nav=gtk.Label("<b>"+_("Navigation")+"</b>")
        label_groups_nav.set_use_markup(True)
        
        groups_download_vbox=gtk.VBox()
        groups_view_vbox=gtk.VBox()
        groups_nav_vbox=gtk.VBox()


        purge_main_vbox=gtk.VBox()
        purge_main_vbox.set_border_width(4)
        purge_main_label=gtk.Label("<b>"+_("Purge Options")+"</b>")
        purge_main_label.set_alignment(0,0.5)
        purge_main_label.set_use_markup(True)
        purge_main_vbox.pack_start(purge_main_label,False,False,4)
        purge_table=gtk.Table(2,2,False)
        purge_table.set_border_width(4)
        self.purge_read_spinbutton=gtk.SpinButton(gtk.Adjustment(value=5,lower=0,upper=1000,step_incr=1,page_incr=10))
        purge_read_tooltip=gtk.Tooltips()
        purge_read_tooltip.set_tip(self.purge_read_spinbutton,_("Number of days. '0' means never purge read articles"))
        purge_read_label=gtk.Label(_("Purge read articles after (days)"))
        purge_read_label.set_alignment(0,0.5)
        self.purge_unread_spinbutton=gtk.SpinButton(gtk.Adjustment(value=10,lower=0,upper=1000,step_incr=1,page_incr=10))
        purge_unread_tooltip=gtk.Tooltips()
        purge_unread_tooltip.set_tip(self.purge_unread_spinbutton,_("Number of days. '0' means never purge unread articles"))
        purge_unread_label=gtk.Label(_("Purge unread articles after (days)"))
        purge_unread_label.set_alignment(0,0.5)



        purge_table.attach(self.purge_read_spinbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        purge_table.attach(purge_read_label,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,2)
        purge_table.attach(self.purge_unread_spinbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        purge_table.attach(purge_unread_label,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,2)
        
        purge_main_vbox.pack_start(purge_table,False,False,4)

        groups_download_vbox.pack_start(purge_main_vbox,False,True,2)

        articles_vbox=gtk.VBox()
        articles_vbox.set_border_width(4)
        articles_label=gtk.Label("<b>"+_("Articles")+"</b>")
        articles_label.set_alignment(0,0.5)
        articles_label.set_use_markup(True)
        articles_vbox.pack_start(articles_label,False,False,4)
        articles_table=gtk.Table(1,1,False)
        self.download_bodies_checkbutton=gtk.CheckButton(_("Retrieve Bodies for all new articles"))
        self.limit_articles_checkbutton=gtk.CheckButton(_("Limit the number of articles to download"))
        self.limit_articles_spinbutton=gtk.SpinButton(gtk.Adjustment(value=500,lower=1,upper=100000,step_incr=1,page_incr=10))
        limit_articles_label=gtk.Label(_("Max number of articles to download"))
        
        self.limit_articles_checkbutton.connect("clicked",self.change_limit_status)
        articles_table.attach(self.download_bodies_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        articles_table.attach(self.limit_articles_checkbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        articles_table.attach(self.limit_articles_spinbutton,0,1,2,3,gtk.FILL,gtk.FILL,16,2)
        articles_table.attach(limit_articles_label,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL)
        
        articles_vbox.pack_start(articles_table,False,False)
        groups_download_vbox.pack_start(articles_vbox,False,True,4)

        auto_download_vbox=gtk.VBox()
        auto_download_vbox.set_border_width(4)
        auto_download_label=gtk.Label("<b>"+_("Automatic Header Download")+"</b>")
        auto_download_label.set_alignment(0,0.5)
        auto_download_label.set_use_markup(True)
        auto_download_vbox.pack_start(auto_download_label,False,False,4)
        auto_download_table=gtk.Table(1,1,False)
        self.auto_download_checkbutton=gtk.CheckButton(_("Download Headers automatically"))
        self.auto_download_spinbutton=gtk.SpinButton(gtk.Adjustment(value=30,lower=5,upper=100000,step_incr=1,page_incr=10))
        timeout_label=gtk.Label(_("Minutes Between Downloads"))
        self.auto_download_checkbutton.connect("clicked",self.change_auto_download_status)
        
        auto_download_table.attach(self.auto_download_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        auto_download_table.attach(self.auto_download_spinbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        auto_download_table.attach(timeout_label,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL)

        auto_download_vbox.pack_start(auto_download_table,False,False)
        groups_download_vbox.pack_start(auto_download_vbox,False,False,4)





        sort_main_vbox=gtk.VBox()
        sort_main_vbox.set_border_width(4)
        sort_main_label=gtk.Label("<b>"+_("Sorting Options")+"</b>")
        sort_main_label.set_alignment(0,0.5)
        sort_main_label.set_use_markup(True)
        sort_main_vbox.pack_start(sort_main_label,False,False,4)
        sort_table=gtk.Table(2,2,False)
        sort_table.set_border_width(4)
        self.sort_order_checkbutton=gtk.CheckButton(_("Ascending Order"))
        sort_label=gtk.Label(_("Sorting Column"))
        sort_label.set_alignment(0,0.5)
        self.sort_combo=gtk.combo_box_entry_new_text()
        self.sort_combo.child.set_editable(False)
        self.sort_combo.set_size_request(130,-1)
        sort_columns=[_("Subject"),_("From"),_("Date"),_("Score")]
        for column in sort_columns:
            self.sort_combo.append_text(column)

        sort_table.attach(self.sort_order_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        sort_table.attach(self.sort_combo,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        sort_table.attach(sort_label,1,2,1,2,gtk.EXPAND|gtk.FILL,2)
        sort_main_vbox.pack_start(sort_table,False,False)
        
        groups_view_vbox.pack_start(sort_main_vbox,False,True)





        charset_vbox=gtk.VBox()
        charset_vbox.set_border_width(4)
        charset_label=gtk.Label("<b>"+_("Charsets")+"</b>")
        charset_label.set_alignment(0,0.5)
        charset_label.set_use_markup(True)
        charset_vbox.pack_start(charset_label,False,False,4)
        charset_table=gtk.Table(2,2,False)
        charset_table.set_border_width(4)
        fallback_charset_label=gtk.Label(_("Fallback Charset (Reading)"))
        fallback_charset_label.set_alignment(0,0.5)

        self.fallback_charset_combo=gtk.combo_box_entry_new_text()
        self.fallback_charset_combo.set_size_request(130,-1)
        for encoding in encodings_list:
            self.fallback_charset_combo.append_text(encoding)
        fallback_charset_tooltip=gtk.Tooltips()
        fallback_charset_tooltip.set_tip(self.fallback_charset_combo.child,encodings_tip)

        self.fallback_charset_combo.child.set_editable(False)

        self.charset_list_button=gtk.Button(_("Charsets List"))
        self.charset_list_button.connect("clicked",self.open_charset_list_win)
        self.charset_list_button.set_size_request(130,-1)
        charset_list_tooltip=gtk.Tooltips()
        charset_list_tooltip.set_tip(self.charset_list_button,_("XPN will try to use the charsets in this order"))
        charset_list_label=gtk.Label(_("Ordered List (Writing)"))
        charset_list_label.set_alignment(0,0.5)

        charset_table.attach(self.fallback_charset_combo,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        charset_table.attach(fallback_charset_label,1,2,0,1,gtk.EXPAND|gtk.FILL,2)
        charset_table.attach(self.charset_list_button,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        charset_table.attach(charset_list_label,1,2,1,2,gtk.EXPAND|gtk.FILL,2) 
        
        charset_vbox.pack_start(charset_table,True,False,4)
        groups_view_vbox.pack_start(charset_vbox,False,True,2)
        
        threading_vbox=gtk.VBox()
        threading_vbox.set_border_width(4)
        threading_label=gtk.Label("<b>"+_("Threading Method")+"</b>")
        threading_label.set_alignment(0,0.5)
        threading_label.set_use_markup(True)
        threading_vbox.pack_start(threading_label,False,False,4)
        threading_table=gtk.Table(1,1,False)
        threading_table.set_border_width(4)
        self.threading_method_radiobutton1=gtk.RadioButton(None,_("Fast (but imprecise) old Algorithm"))
        self.threading_method_radiobutton2=gtk.RadioButton(self.threading_method_radiobutton1,_("Slow (but precise) new Algorithm"))
        threading_table.attach(self.threading_method_radiobutton1,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        threading_table.attach(self.threading_method_radiobutton2,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        threading_vbox.pack_start(threading_table,True,False,4)
        
        groups_view_vbox.pack_start(threading_vbox,False,True,2)

        main_nav_vbox=gtk.VBox()
        main_nav_vbox.set_border_width(4)
        misc_main_label=gtk.Label("<b>"+_("Miscellaneous")+"</b>")
        misc_main_label.set_alignment(0,0.5)
        misc_main_label.set_use_markup(True)
        main_nav_vbox.pack_start(misc_main_label,False,False,4)
        misc_table=gtk.Table(5,2,False)
        misc_table.set_border_width(4)
        self.advance_on_mark_checkbutton=gtk.CheckButton(_("Advance to the Next Article on Mark"))
        self.oneclick_checkbutton=gtk.CheckButton(_("One Click Enter Group"))
        self.oneclick_article_checkbutton=gtk.CheckButton(_("One Click Enter Article"))
        self.expand_groups_checkbutton=gtk.CheckButton(_("Expand Group on Entering"))
        one_key_label=gtk.Label(_("Scroll Text (% of page)"))
        one_key_label.set_size_request(200,-1)
        one_key_label.set_alignment(0,0.5)
        self.one_key_spin=gtk.SpinButton(gtk.Adjustment(value=50,lower=1,upper=100,step_incr=1,page_incr=10))
        
        misc_table.attach(self.advance_on_mark_checkbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        misc_table.attach(self.oneclick_checkbutton,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        misc_table.attach(self.oneclick_article_checkbutton,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        misc_table.attach(self.expand_groups_checkbutton,0,1,4,5,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        misc_table.attach(self.one_key_spin,0,1,5,6,gtk.FILL,gtk.FILL,16,2)
        misc_table.attach(one_key_label,1,2,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL,2)

        main_nav_vbox.pack_start(misc_table,False,False)

        groups_nav_vbox.pack_start(main_nav_vbox,False,True,2)

        
        notebook.append_page(groups_download_vbox,label_groups_download)
        notebook.append_page(groups_view_vbox,label_groups_view)
        notebook.append_page(groups_nav_vbox,label_groups_nav)

        return notebook


    def build_misc_page(self):
        notebook=gtk.Notebook()
        label_misc=gtk.Label("<b>"+_("External Apps")+"</b>")
        label_misc.set_use_markup(True)

        label_misc_2=gtk.Label("<b>"+_("Miscellaneous")+"</b>")
        label_misc_2.set_use_markup(True)

        miscellaneous_vbox=gtk.VBox()
        miscellaneous_vbox_2=gtk.VBox()

        browser_table=gtk.Table()
        browser_table.set_border_width(4)
        browser_main_vbox=gtk.VBox()
        browser_main_vbox.set_border_width(4)
        browser_main_label=gtk.Label("<b>"+_("Web Browser")+"</b>")
        browser_main_label.set_alignment(0,0.5)
        browser_main_label.set_use_markup(True)
        browser_main_vbox.pack_start(browser_main_label,False,False,4)

        self.browser_checkbutton=gtk.CheckButton(_("Use Custom Web Browser Launcher"))
        self.browser_checkbutton.connect("clicked",self.change_browser_status)
        self.browser_entry=gtk.Entry()
        browser_tooltip=gtk.Tooltips()
        browser_tooltip.set_tip(self.browser_entry,_("Type your custom command, %s represents the url.\nExamples:\n\nmozilla %s &\nxterm -e links %s"))

        self.browser_label=gtk.Label(_("Web Browser Launcher"))
        self.browser_label.set_alignment(0,0.5)

        browser_table.attach(self.browser_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        browser_table.attach(self.browser_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        browser_table.attach(self.browser_label,1,2,1,2,gtk.EXPAND|gtk.FILL,2)


        browser_main_vbox.pack_start(browser_table,False,False)


        editor_table=gtk.Table()
        editor_table.set_border_width(4)
        editor_main_vbox=gtk.VBox()
        editor_main_vbox.set_border_width(4)
        editor_main_label=gtk.Label("<b>"+_("External Editor")+"</b>")
        editor_main_label.set_alignment(0,0.5)
        editor_main_label.set_use_markup(True)
        editor_main_vbox.pack_start(editor_main_label,False,False,4)
        self.editor_checkbutton=gtk.CheckButton(_("Always Use External Editor"))
        self.editor_entry=gtk.Entry()
        editor_tooltip=gtk.Tooltips()
        editor_tooltip.set_tip(self.editor_entry,_("""Type the editor launcher, %s represents the filename.\nExamples:\n\nxterm -e vim %s\ngvim -f %s\nnotepad.exe %s\n"C:\Program Files\Notepad++\Notepad++.exe" %s -nosession\n\nNOTE: This feature works only with *Nix and Windows systems"""))

        editor_label=gtk.Label(_("External Editor Command"))
        editor_label.set_alignment(0,0.5)

        editor_table.attach(self.editor_checkbutton,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        editor_table.attach(self.editor_entry,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        editor_table.attach(editor_label,1,2,1,2,gtk.EXPAND|gtk.FILL,2)



        editor_main_vbox.pack_start(editor_table,False,False)


        lang_vbox=gtk.VBox()
        lang_vbox.set_border_width(4)
        lang_vbox_label=gtk.Label("<b>"+_("Language")+"</b>")
        lang_vbox_label.set_alignment(0,0.5)
        lang_vbox_label.set_use_markup(True)
        lang_vbox.pack_start(lang_vbox_label,False,False,4)
        lang_hbox=gtk.HBox()
        langs_vbox=gtk.VBox()
        self.lang_en_radiobutton=gtk.RadioButton()
        lang_en_hbox=gtk.HBox()
        lang_en_label=gtk.Label(_("English"))
        lang_en_image=gtk.Image()
        lang_en_image.set_from_file("pixmaps/en.xpm")
        lang_en_hbox.pack_start(lang_en_image,True,True,2)
        lang_en_hbox.pack_start(lang_en_label,True,True,4)
        self.lang_en_radiobutton.add(lang_en_hbox)
       
        self.lang_it_radiobutton=gtk.RadioButton(self.lang_en_radiobutton)
        lang_it_hbox=gtk.HBox()
        lang_it_label=gtk.Label(_("Italian"))
        lang_it_image=gtk.Image()
        lang_it_image.set_from_file("pixmaps/it.xpm")
        lang_it_hbox.pack_start(lang_it_image,True,True,2)
        lang_it_hbox.pack_start(lang_it_label,True,True,4)
        self.lang_it_radiobutton.add(lang_it_hbox)

        self.lang_fr_radiobutton=gtk.RadioButton(self.lang_en_radiobutton)
        lang_fr_hbox=gtk.HBox()
        lang_fr_label=gtk.Label(_("French"))
        lang_fr_image=gtk.Image()
        lang_fr_image.set_from_file("pixmaps/fr.xpm")
        lang_fr_hbox.pack_start(lang_fr_image,True,True,2)
        lang_fr_hbox.pack_start(lang_fr_label,True,True,4)
        self.lang_fr_radiobutton.add(lang_fr_hbox)

        self.lang_de_radiobutton=gtk.RadioButton(self.lang_en_radiobutton)
        lang_de_hbox=gtk.HBox()
        lang_de_label=gtk.Label(_("German"))
        lang_de_image=gtk.Image()
        lang_de_image.set_from_file("pixmaps/de.xpm")
        lang_de_hbox.pack_start(lang_de_image,True,True,2)
        lang_de_hbox.pack_start(lang_de_label,True,True,4)
        self.lang_de_radiobutton.add(lang_de_hbox)
        
        langs_vbox.pack_start(self.lang_en_radiobutton,True,True,2)
        langs_vbox.pack_start(self.lang_it_radiobutton,True,True,2)
        langs_vbox.pack_start(self.lang_fr_radiobutton,True,True,2)
        langs_vbox.pack_start(self.lang_de_radiobutton,True,True,2)
        lang_hbox.pack_start(langs_vbox,True,False,2)
        lang_label=gtk.Label(_("You must restart XPN in order\n to get the translation active"))
        lang_hbox.pack_start(lang_label,True,False,4)
        lang_vbox.pack_start(lang_hbox,False,False)


        miscellaneous_vbox.pack_start(browser_main_vbox,False,True,2)
        miscellaneous_vbox.pack_start(editor_main_vbox,False,True,2)
        miscellaneous_vbox_2.pack_start(lang_vbox,False,True,2)
        
        notebook.append_page(miscellaneous_vbox,label_misc)
        notebook.append_page(miscellaneous_vbox_2,label_misc_2)

        return notebook

        
    def __init__(self,conf,main_win):
        self.configs=conf.get_configs()
        self.main_win=main_win
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("XPN Preferences"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/conf.xpm"))
        self.win.set_default_size(470,400)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.tips=gtk.Tooltips()

        #main_vbox
        self.main_vbox=gtk.VBox()
        self.win.add(self.main_vbox)
        
        #main_hbox
        self.main_hbox=gtk.HBox()
        self.evbox=gtk.EventBox()
        self.left_buttons=gtk.VButtonBox()
        self.left_buttons.set_layout(gtk.BUTTONBOX_EDGE)
        self.evbox.add(self.left_buttons)
        style = self.evbox.get_style()
        bgcolor = gtk.gdk.Color( 65535, 65535, 65535 )
        self.evbox.modify_bg( gtk.STATE_NORMAL, bgcolor )

        self.buttons={}
        self.insert_rb(_("Server"),"config-servers.png","server",_("Configure Server Profiles"))
        self.insert_rb(_("User"),"config-users.png","user",_("Configure User Profile"),self.buttons["server"])
        self.insert_rb(_("Display"),"config-display.png","display",_("Configure Display Profile"),self.buttons["server"])
        #self.insert_rb(_("Posting"),"config-posting.png","posting",_("Configure Posting Profile"),self.buttons["server"])
        self.insert_rb(_("Groups"),"config-groups.png","groups",_("Configure Group Properties"),self.buttons["server"])
        self.insert_rb(_("Misc"),"config-misc.png","misc",_("Configure Miscellaneous Properties"),self.buttons["server"])


        self.main_hbox.pack_start(self.evbox,False,False,4)
        self.main_vbox.pack_start(self.main_hbox,True,True,4)

        self.server_page=self.build_server_page()
        self.user_page=self.build_user_page()
        self.display_page=self.build_display_page()
#        self.posting_page=self.build_posting_page()
        self.groups_page=self.build_groups_page()
        self.misc_page=self.build_misc_page()


        self.main_hbox.pack_start(self.server_page,False,False)
        #self.show_config_pages(None,"Server")

        #buttons hbox
        self.buttons_hbox=gtk.HBox()
        self.main_vbox.pack_start(self.buttons_hbox,False,False,0)

        #cancel_button
        self.cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        self.cancel_button_tooltip=gtk.Tooltips()
        self.cancel_button_tooltip.set_tip(self.cancel_button,_("Close window. Discard changes"))
        self.cancel_button.connect("clicked",self.destroy)
        self.buttons_hbox.pack_start(self.cancel_button,True,True,0)
        #ok_button
        self.ok_button=gtk.Button(None,gtk.STOCK_OK)
        self.ok_button.connect("clicked",self.save_configs,conf)
        self.ok_button_tooltip=gtk.Tooltips()
        self.ok_button_tooltip.set_tip(self.ok_button,_("Close window and save settings"))
        self.buttons_hbox.pack_start(self.ok_button,True,True,0)
        self.ok_button.set_border_width(5)
        self.cancel_button.set_border_width(5)

        self.update_all(self.configs)
