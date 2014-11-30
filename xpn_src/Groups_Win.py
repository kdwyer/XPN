import sys
import gtk
import gobject
import socket
import time
import re
import threading, Queue
import os,shutil
import ConfigParser
from nntplib import *
from string import find
from email.Utils import parsedate_tz,mktime_tz
from xpn_src.Groups_Pane import Groups_Pane,Groups_List
from xpn_src.ListThread import ListThread
from xpn_src.Article import Article
from xpn_src.Config_File import Config_File
from xpn_src.Connections_Handler import Connection, SSLConnection
from xpn_src.UserDir import get_wdir
from xpn_src.Dialogs import Dialog_OK
from xpn_src.Articles_DB import Articles_DB,Groups_DB


try:
    set()
except:
    from sets import Set as set


class Groups_Win:
    def show(self):
        self.win.show_all()

    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,obj):
        for connection in self.connectionsPool.itervalues():
            connection.closeConnection()
        self.win.destroy()

    def handle_error(self, error_strings):
        self.statusbar.push(1, error_strings[1])
        self.add_log(error_strings[1],False)
        for connection in self.connectionsPool.itervalues():
            connection.closeConnection()
        return 1

    def connected(self, response):
        self.statusbar.push(1, response[1])
        self.add_log(response[1],False)

    def ended_listing(self, data):
        lock = threading.Lock()
        lock.acquire()
        groups_list = self.listThread.queue.get()
        lock.release()
        groups_list.sort()
        server_name=self.server_combo.get_active_text()        
        self.groups_list_db.createList(groups_list,server_name)
        self.update_total_list()
        return 1

    def update_total_list(self):
        file_list=os.listdir(os.path.join(self.wdir,"groups_info"))
        total_list=[]
        for file_name in file_list:
            if file_name.endswith(".groups.sqlitedb"):
                groups_list=self.groups_list_db.getList(file_name)
                total_list += groups_list
        self.total_list=total_list
        self.groups_list_db.createList(total_list,"","groups.sqlitedb")
        self.server_list.show_list(self.total_list)
        

    def get_list(self,obj):
        lock = threading.Lock()
        server=self.server_combo.get_active_text()
        
        message,connection_is_up=self.connectionsPool[server]._tryConnection()
        self.statusbar.push(1,message)
        if connection_is_up:
            self.listThread = ListThread(self.connectionsPool[server].serverConnection,server)
            self.listThread.start()
            self.statusbar.push(1,_("Please wait, I'm downloading the list"))
            finished = 0
            timer=10
            while 1:
                while gtk.events_pending():
                    gtk.main_iteration(False)
                time.sleep(0.001)
                lock.acquire()
                try:
                    evt = self.listThread.queue.get_nowait()
                except Queue.Empty:
                    evt = [None, None]
                lock.release()
                _dispatch = {"Connected":self.connected,
                             "Server error":self.handle_error,
                             "Finished Listing":self.ended_listing
                             }
                if evt[0]!=None:
                    handler = _dispatch.get(evt[0],None)
                else:
                    handler = None
                if handler: finished = handler(evt)
                else:
                    timer=timer-1
                    if timer<0:
                        self.progressbar.pulse()
                        timer=10
                if finished:
                    self.progressbar.set_fraction(0)
                    break




    def show_subscribed(self):
        list=self.art_db.getSubscribed()
        new_list=[]
        for group in list:
            total,unread_number=self.art_db.getArticlesNumbers(group[0])
            new_list.append((group[0],total))
        self.subscribed_list.show_list(new_list)


    def search_group(self,obj):
        group_to_search=self.group_entry.get_text()
        use_regex=self.regex_checkbutton.get_active()

        def match_regex(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE).findall(field)
            except:
                match_rule=False
            return match_rule

        if use_regex:
            match_rule=lambda field,regex: match_regex(field,regex)
        else:
            match_rule=lambda field,word: field.find(word)+1

        list=self.total_list
        i=0
        found=[]
        self.statusbar.push(1,_("Searching..."))
        while (i<len(list)):
            if  match_rule(list[i][0],group_to_search):
                found.append(list[i])
            i=i+1
        self.server_list.show_list(found)
        self.statusbar.push(1,"")

    def show_full_list(self,obj):
        self.server_list.show_list(self.total_list)


        
    def download_headers(self,group,articles_number,server_name):
        last_number=str(0)
        #Downloading headers
        self.progressbar.set_text(_("Fetching Headers"))
        self.progressbar.set_fraction(1/float(2))
        while gtk.events_pending():
            gtk.main_iteration(False)
        message,total_headers,last=self.connectionsPool[server_name].getHeaders(group,0,count=articles_number)
        if last!=-1:
            last_number=str(last)
        self.statusbar.push(1,message)
        if total_headers:
            self.progressbar.set_text(_("Building Articles"))
        else:
            self.progressbar.set_text(_("No New Headers"))
        self.progressbar.set_fraction(2/float(2))
        while gtk.events_pending():
            gtk.main_iteration(False)
        
        self.art_db.createGroup(group)
        self.art_db.addHeaders(group,total_headers,server_name,self.connectionsPool)
            
        
        self.statusbar.push(1,_("Group subscribed"))
        self.progressbar.set_fraction(0)
        self.progressbar.set_text("")
        return last_number,message
   
    def subscribe_manually(self,obj):
        group_to_subscribe=self.subscribe_manually_entry.get_text()
        if group_to_subscribe:
            server_name=self.server_combo.get_active_text()        
            self.subscribe_group(group_to_subscribe,server_name)
            self.show_subscribed()
            self.main_win.show_subscribed() 

    def subscribe_selected_groups(self,obj):
        model,path_list,iter_list=self.server_list.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_to_subscribe=model.get_value(iter_selected,0)
            server_name=model.get_value(iter_selected,2)
            self.subscribe_group(group_to_subscribe,server_name)
        self.show_subscribed()
        self.main_win.show_subscribed() 

    def subscribe_group(self,group_to_subscribe,server_name):
        articles_number=self.articles_spinbutton.get_value_as_int()


        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","id.txt"))
        try:
            id_name=cp.sections()[0]
        except IndexError:
            self.statusbar.push(1,_("First you have to create at least one Identity"))
            Dialog_OK(_("First you have to create at least one Identity"))
        else:    
            last,message=self.download_headers(group_to_subscribe,articles_number,server_name)

            self.art_db.removeSubscribed(group_to_subscribe)
            self.art_db.addSubscribed(group_to_subscribe,last,server_name,id_name)

            if message.lower().startswith("server error"):
                self.unsubscribe_group(group_to_subscribe)
                self.statusbar.push(1,_("The Group Name seems to be wrong"))
            if message.lower().startswith("no connection with"):
                self.unsubscribe_group(group_to_subscribe)
                self.statusbar.push(1,message)
                


    def unsubscribe_selected_groups(self,obj):
        model,path_list,iter_list=self.subscribed_list.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_to_unsubscribe=model.get_value(iter_selected,0)
            self.unsubscribe_group(group_to_unsubscribe)
        self.main_win.show_subscribed()
        self.show_subscribed()


    def unsubscribe_group(self,group_to_unsubscribe):
        removed=self.art_db.removeSubscribed(group_to_unsubscribe)
        if removed:
            self.art_db.closeGroups((group_to_unsubscribe,))
            shutil.rmtree(os.path.join(self.wdir,"groups_info/",group_to_unsubscribe))
            self.statusbar.push(1,_("Group removed"))




    def change_live_search_status(self,obj):
        live_search=self.live_search_checkbutton.get_active()
        if live_search:
            self.search_button.set_sensitive(False)
            self.live_search_handler=self.group_entry.connect("changed",self.search_group)
        else:
            self.search_button.set_sensitive(True)
            self.group_entry.disconnect(self.live_search_handler)
    
    def add_log(self,message,is_command):
        ''' Adds an entry in server_logs.dat.

        Arguments:
        message    : is the entry to add
        is_command : if it is True we are adding a message sent to the server, else
                     we are adding a message received from the server
        '''
        try:
            f=open(os.path.join(self.wdir,"server_logs.dat"),"a")
        except IOError:
            pass
        else:
            if is_command:
                f.write(time.ctime(time.time())+" :: >> "+message+"\n")
            else:
                f.write(time.ctime(time.time())+" :: << "+message+"\n")
            f.close()
        
    def __init__(self,main_win):
        self.wdir=get_wdir()
        self.conf=Config_File()
        self.configs=self.conf.get_configs()
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.connectionsPool=dict()
        
        for server in cp.sections():
            if cp.get(server,"nntp_use_ssl")=="True":
                self.connectionsPool[server]=SSLConnection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
            else:
                self.connectionsPool[server]=Connection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
        self.art_db=main_win.art_db
        self.groups_list_db=Groups_DB()
        self.main_win=main_win
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_modal(True)
        self.win.set_transient_for(main_win.window)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("NewsGroups"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/groups.xpm"))
        self.win.set_default_size(700,480)
        self.win.set_position(gtk.WIN_POS_CENTER)

        #main vbox
        self.vbox1 = gtk.VBox(False,0)
        self.vbox1.set_border_width(2)
        self.win.add(self.vbox1)

        #hpaned
        self.hpaned =gtk.HPaned()
        self.hpaned.set_position(310)
        self.vbox1.pack_start(self.hpaned,True,True,0)

        #FrameList
        self.frame_list=gtk.Frame(_("List"))
        self.hpaned.add(self.frame_list)


        #VBoxList
        self.vbox_list=gtk.VBox()
        self.vbox_list.set_border_width(2)
        self.frame_list.add(self.vbox_list)

        #HBoxList
        self.hbox_list=gtk.HBox()
        self.vbox_list.pack_start(self.hbox_list,False,True,2)

        #group_entry
        self.group_entry=gtk.Entry()
        self.hbox_list.pack_start(self.group_entry,True,True,2)

        #search_button
        self.search_button=gtk.Button(_("Search Group"))
        self.search_button.connect("clicked",self.search_group)
        self.hbox_list.pack_start(self.search_button,False,True,2)
        self.search_button_tooltip=gtk.Tooltips()
        self.search_button_tooltip.set_tip(self.search_button,_("Start searching"))

        #live search check_button
        self.live_search_checkbutton=gtk.CheckButton(_("Perform Live Search"))
        self.vbox_list.pack_start(self.live_search_checkbutton,False,True,2)
        self.live_search_checkbutton.connect("clicked",self.change_live_search_status)

        #regex check_button
        self.regex_checkbutton=gtk.CheckButton(_("Use Regular Expression"))
        self.vbox_list.pack_start(self.regex_checkbutton,False,True,2)
        
        #full list button
        self.full_button=gtk.Button(_("Show Full List"))
        self.full_button.connect("clicked",self.show_full_list)
        self.vbox_list.pack_start(self.full_button,False,True,2)

        #GroupsList
        self.server_list=Groups_List(_("NewsGroups"),_("Mode"),_("Server"))
        self.server_list.groups_list.set_rules_hint(1)
        self.server_list.groups_list.connect("row-activated", lambda *w: self.subscribe_selected_groups(None))
        self.vbox_list.pack_start(self.server_list.get_widget(),True,True,2)

        #right_vbox
        self.right_vbox =gtk.VBox()
        self.hpaned.add(self.right_vbox)

        #right_hbox
        self.right_hbox=gtk.HBox()
        self.right_vbox.pack_start(self.right_hbox,False,True,0)


        #Server Frame
        self.server_frame =gtk.Frame(_("Server"))
        self.right_hbox.pack_start(self.server_frame,True,True,0)

        #Server HBox
        self.server_hbox=gtk.HBox()
        self.server_frame.add(self.server_hbox)
        self.server_hbox.set_border_width(5)


        #Server Button
        self.server_button=gtk.Button(_("Get Newsgroups List"))
        self.server_button.connect("clicked",self.get_list)
        self.server_hbox.pack_start(self.server_button,False,True,5)
        self.server_button_tooltip=gtk.Tooltips()
        self.server_button_tooltip.set_tip(self.server_button,_("This could take several minutes"))

        #Server Label
        self.server_combo= gtk.combo_box_new_text()
        for server in cp.sections(): self.server_combo.append_text(cp.get(server,"server"))
        self.server_combo.set_active(0)
        if len(cp.sections())==0:
            self.server_button.set_sensitive(False)
        self.server_hbox.pack_start(self.server_combo,False,True,5)



        #Article Frame
        self.articles_frame =gtk.Frame(_("Articles Number"))
        self.right_hbox.pack_start(self.articles_frame,False,True,0)

        #Articles SpinButton
        self.articles_spinbutton =gtk.SpinButton(gtk.Adjustment(value=500,lower=0,upper=10000,step_incr=1,page_incr=50))
        self.articles_spinbutton_tooltip=gtk.Tooltips()
        self.articles_spinbutton_tooltip.set_tip(self.articles_spinbutton,_("Download this number of articles (headers only)"))
        self.articles_frame.add(self.articles_spinbutton)

        #Subscribed Frame
        self.subscribed_frame= gtk.Frame(_("Subscribed Groups"))
        self.right_vbox.pack_start(self.subscribed_frame,True,True,2)

        #Subscribed_hbox
        self.subscribed_hbox = gtk.HBox()
        self.subscribed_frame.add(self.subscribed_hbox)
        
        
        #button_box
        self.vbutton_box=gtk.VButtonBox()
        self.subscribed_hbox.pack_start(self.vbutton_box,False,False,0)
        self.vbutton_box.set_layout(gtk.BUTTONBOX_SPREAD)

        #button_subscribe
        self.button_subscribe=gtk.Button()
        self.button_subscribe.connect("clicked",self.subscribe_selected_groups)
        button_subscribe_image=gtk.Image()
        button_subscribe_image.set_from_stock(gtk.STOCK_GO_FORWARD,gtk.ICON_SIZE_MENU)
        self.button_subscribe.add(button_subscribe_image)
        self.vbutton_box.pack_start(self.button_subscribe,False,False,0)
        self.subscribe_button_tooltip=gtk.Tooltips()
        self.subscribe_button_tooltip.set_tip(self.button_subscribe,_("Subscribe selected groups"))

        #button_unsubscribe
        self.button_unsubscribe=gtk.Button()
        self.button_unsubscribe.connect("clicked",self.unsubscribe_selected_groups)
        button_unsubscribe_image=gtk.Image()
        button_unsubscribe_image.set_from_stock(gtk.STOCK_GO_BACK,gtk.ICON_SIZE_MENU)
        self.button_unsubscribe.add(button_unsubscribe_image)
        self.vbutton_box.pack_start(self.button_unsubscribe,False,False,0)
        self.unsubscribe_button_tooltip=gtk.Tooltips()
        self.unsubscribe_button_tooltip.set_tip(self.button_unsubscribe,_("UnSubscribe selected groups"))

        #subscribed_groups
        self.subscribed_list=Groups_Pane(_("NewsGroups"),_("Articles"),False,self.configs)
        self.subscribed_list.groups_list.connect("row-activated", lambda *w: self.unsubscribe_selected_groups(None))

        #Subscribed_vbox
        self.subscribed_vbox= gtk.VBox()

        self.subscribed_vbox.pack_start(self.subscribed_list.get_widget(),True,True,5)
       
        #subscribe manually
        self.subscribe_manually_entry=gtk.Entry()
        self.subscribe_manually_button=gtk.Button(_("Subscribe Manually"))
        subscribe_manually_hbox=gtk.HBox()
        subscribe_manually_hbox.add(self.subscribe_manually_entry)
        subscribe_manually_hbox.add(self.subscribe_manually_button)
        self.subscribe_manually_button.connect("clicked",self.subscribe_manually)
        
        self.subscribed_vbox.pack_start(subscribe_manually_hbox,False,False)

        self.subscribed_hbox.pack_start(self.subscribed_vbox,True,True)

        #button_close
        self.button_close= gtk.Button(None,gtk.STOCK_OK)
        self.vbox1.pack_start(self.button_close,False,True,4)
        self.button_close.connect("clicked",self.destroy)
        self.button_close_tooltip=gtk.Tooltips()
        self.button_close_tooltip.set_tip(self.button_close,_("Close this window"))

        #hbox_bottom
        self.hbox_bottom=gtk.HBox()
        self.vbox1.pack_start(self.hbox_bottom,False,False,0)

        #progressbar
        self.progressbar=gtk.ProgressBar()
        self.hbox_bottom.pack_start(self.progressbar,False,False,0)

        #statusbar
        self.statusbar=gtk.Statusbar()
        self.hbox_bottom.pack_start(self.statusbar,True,True,0)

        #some inits
        self.show_subscribed()
        self.show()
        self.statusbar.push(1,_("Building Newsgroups list"))
        self.total_list=[]
        while gtk.events_pending():
            gtk.main_iteration(False)
        try:
            f=open(os.path.join(self.wdir,"groups_info/groups.sqlitedb"),"rb")
        except IOError:
            self.statusbar.push(1,_("You have to download newsgroups list"))
        else:
            groups_list=self.groups_list_db.getList("groups.sqlitedb")
            self.total_list=groups_list
            self.server_list.show_list(groups_list)
            self.statusbar.push(1,_("Newsgroups list loaded"))
            
