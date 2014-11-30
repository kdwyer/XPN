#!/usr/bin/env python
import os,shutil
#os.environ['PATH'] += ';'+os.path.join('gtk/lib')+';'+os.path.join('gtk/bin') #OLD
#os.environ['PATH'] = os.path.join('gtk/lib')+';'+os.path.join('gtk/bin')+';'+os.path.join('gtk\\lib')+';'+os.path.join('gtk\\bin')+';'+os.environ['PATH']  #NEW

#py2exe 0.6.8 problem
import email
import email.mime.text
import email.iterators
import email.generator
import email.utils
#py2exe 0.6.8 problem

import sys
import gtk
import gobject
import pango
import cPickle
import time
import re
import platform
import glob
import gettext
import locale
import webbrowser
import ConfigParser
from urllib import quote as url_quote
from optparse import OptionParser
from email.Utils import parsedate_tz, mktime_tz
from xpn_src.Groups_Pane import Groups_Pane
from xpn_src.Threads_Pane import Threads_Pane
from xpn_src.Article_Pane import Article_Pane
from xpn_src.Groups_Win import Groups_Win
from xpn_src.Config_File import Config_File
from xpn_src.Config_Win import Config_Win
from xpn_src.Edit_Win import Edit_Win
from xpn_src.Edit_Mail_Win import Edit_Mail_Win
from xpn_src.Dialogs import About_Dialog, Dialog_YES_NO, Error_Dialog, MidDialog, Dialog_OK, Dialog_Import_Newsrc
from xpn_src.Article import Article, Article_To_Send
from xpn_src.Show_Logs import Logs_Window
from xpn_src.Newsrc import ImportNewsrc, ExportNewsrc
from xpn_src.Find_Win import Find_Win, Search_Win, GlobalSearch
from xpn_src.Score import Score_Rules, Score_Win
from xpn_src.Charset_List import load_ordered_list
from xpn_src.Connections_Handler import Connection, SMTPConnection, SSLConnection
from xpn_src.UserDir import UserDir, get_wdir
from xpn_src.Outbox_Manager import Outbox_Manager
from xpn_src.KeyBindings import KeyBindings, load_shortcuts
from xpn_src.Server_Win import NNTPServer_Win
from xpn_src.Groups_Vs_ID import Groups_Vs_ID
from xpn_src.Articles_DB import Articles_DB, Groups_DB
from xpn_src.Custom_Search_Entry import Custom_Search_Entry
try:
    set()
except:
    from sets import Set as set

try:
    user_system=" ; "+platform.system()
except:
    user_system=""

NUMBER="1.2.6"
VERSION="XPN/%s (Street Spirit%s)" % (NUMBER,user_system)

gettext.NullTranslations()
gettext.install("xpn")

ui_string="""<ui>
    <menubar name='MainMenuBar'>
        <menu action='File'>
            <menuitem action='groups' />
            <separator/>
            <menuitem action='rules' />
            <separator/>
            <menuitem action='logs' />
            <separator/>
            <menuitem action='exp_newsrc' />
            <menuitem action='imp_newsrc' />
            <separator />
            <menuitem action='accelerator' />
            <separator />
            <menuitem action='conf' />
            <separator />
            <menuitem action='exit' />
        </menu>
        <menu action='Search'>
            <menuitem action='find' />
            <menuitem action='global' />
            <menuitem action='filter' />
            <separator />
            <menuitem action='search' />
        </menu>
        <menu action ='View'>
            <menu action='view_articles_opts'>
                <menuitem action='raw' />
                <menuitem action='spoiler' />
                <menuitem action='show_quote' />
                <menuitem action='show_sign' />
                <menuitem action='fixed' />
                <menuitem action='show_hide_headers' />
                <menuitem action='rot13' />
            </menu>
            <separator />
            <menu action='view_group_opts'>
                <menuitem action='show_threads' />
                <menuitem action='show_all_read_threads' />
                <menuitem action='show_threads_without_watched' />
                <menuitem action='show_read_articles' />
                <menuitem action='show_unread_articles' />
                <menuitem action='show_kept_articles' />
                <menuitem action='show_unkept_articles' />
                <menuitem action='show_watched_articles' />
                <menuitem action='show_ignored_articles' />
                <menuitem action='show_unwatchedignored_articles' />
                <menuitem action='show_score_neg_articles' />
                <menuitem action='show_score_zero_articles' />
                <menuitem action='show_score_pos_articles' />
            </menu>
        </menu>
        <menu action ='Navigate'>
            <menuitem action='group' />
            <separator />
            <menuitem action='previous' />
            <menuitem action='next' />
            <menuitem action='next_unread' />
            <menuitem action='parent' />
            <menuitem action='one_key' />
            <menuitem action='move_up' />
            <separator />
            <menuitem action='focus_groups' />
            <menuitem action='focus_threads' />
            <menuitem action='focus_article' />
            <separator />
            <menuitem action='zoom_groups' />
            <menuitem action='zoom_threads' />
            <menuitem action='zoom_article' />
        </menu>
        <menu action='Subscribed'>
            <menuitem action='gethdrs' />
            <menuitem action='gethdrssel' />
            <menuitem action='getbodies' />            
            <menuitem action='getbodiessel' />
            <separator />   
            <menuitem action='expand_row' />
            <menuitem action='collapse_row' />
            <menuitem action='expand' />
            <menuitem action='collapse' />
            <separator />
            <menu action='mark_group'>
                <menuitem action='mark' />
                <menuitem action='mark_unread_group' />
                <menuitem action='mark_download_group' />
                <menuitem action='keepall' />
                <separator />
                <menuitem action='markall' />
                <menuitem action='markall_unread' />
            </menu>
            <separator />
            <menuitem action='apply_score' />
            <separator />
            <menuitem action='groups_vs_id' />
            
        </menu>
        <menu action='Articles'>
            <menuitem action='post' />
            <menuitem action='followup' />
            <menuitem action='reply' />
            <menuitem action='outbox_manager' />
            <separator />
            <menuitem action='cancel' />
            <menuitem action='supersede' />
            <separator />
            <menu action='flags'>
                <menuitem action='mark_read' />
                <menuitem action='mark_unread' />
                <menuitem action='mark_download' />
                <menuitem action='keep' />
                <menuitem action='delete' />
                <separator />
                <menuitem action='mark_read_sub' />
                <menuitem action='mark_unread_sub' />
                <menuitem action='mark_download_sub' />
                <menuitem action='keep_sub' />
                <menuitem action='watch' />
                <menuitem action='ignore' />
                <separator />
                <menuitem action='raise_score' />
                <menuitem action='lower_score' />
                <menuitem action='set_score' />
            </menu>
        </menu>       
        <menu action='Help'>
            <menuitem action='about' />
        </menu>
    </menubar>
            
    <popup action='mark_group'>
        <menuitem action='mark' />
        <menuitem action='mark_unread_group' />
        <menuitem action='mark_download_group' />
        <menuitem action='keepall' />
        <separator />
        <menuitem action='markall' />
        <menuitem action='markall_unread' />
    </popup>
    
    <popup action='flags'>
        <menuitem action='mark_read' />
        <menuitem action='mark_unread' />
        <menuitem action='mark_download' />
        <menuitem action='keep' />
        <menuitem action='delete' />
        <separator />
        <menuitem action='mark_read_sub' />
        <menuitem action='mark_unread_sub' />
        <menuitem action='mark_download_sub' />
        <menuitem action='keep_sub' />
        <menuitem action='watch' />
        <menuitem action='ignore' />
        <separator />
        <menuitem action='raise_score' />
        <menuitem action='lower_score' />
        <menuitem action='set_score' />
    </popup>


    <toolbar name='MainToolBar'>
        <toolitem action='groups' />
        <toolitem action='gethdrs' />
        <toolitem action='getbodies' />
        <toolitem action='mark' />
        <toolitem action='markall' />
        <separator />
        <toolitem action='post' />
        <toolitem action='followup' />
        <toolitem action='reply' />
        <toolitem action='outbox_manager' />
        <separator />
        <toolitem action='previous' />
        <toolitem action='next' />
        <toolitem action='next_unread' />
        <toolitem action='rot13' />
        <separator />
        <toolitem action='expand_row' />
        <toolitem action='collapse_row' />
        <toolitem action='expand' />
        <toolitem action='collapse' />
        <separator />
        <toolitem action='rules' />
        <toolitem action='conf' />
    </toolbar>
</ui>"""

def escape(data):
    """Escape &, <, and > in a string of data.
    """

    # must do ampersand first
    data = data.replace("&", "&amp;")
    data = data.replace(">", "&gt;")
    data = data.replace("<", "&lt;")
    return data

class MainWin:
    def open_logs_win(self,object):
        self.logs_win=Logs_Window(self.window)

    def open_groups_win(self,object):
        self.win2=Groups_Win(self)
        self.win2.show()

    def open_configure_win(self,object):
        self.save_sizes()
        self.win3=Config_Win(self.conf,self)
        self.win3.show()

    def open_rules_win(self,object):
        self.score_win=Score_Win(self.score_rules,self)
        self.score_win.show()

    def open_groups_vs_id(self,object):
        self.groups_vs_id=Groups_Vs_ID(self.subscribed_groups,self)
        self.groups_vs_id.show()

    def supersede_cancel_message(self,object,mode):
        group_selected=""
        id_name=""
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        if iter_selected!=None:
            group_selected=model.get_value(iter_selected,0)
            id_name=self.get_id_for_group(group_selected)
        model,iter_selected=self.threads_pane.threads_tree.get_selection().get_selected()
        subj=""
        cp_id=ConfigParser.ConfigParser()
        cp_id.read(os.path.join(get_wdir(),"dats","id.txt"))

        if iter_selected!=None:
            #subj=model.get_value(iter_selected,1).decode("utf-8")
            article=self.threads_pane.get_article(model,iter_selected)
            subj=article.subj
            try:
                article.ngroups
            except AttributeError:
                self.statusbar.push(1,_("First you have to read the article"))
            else:
                nick=cp_id.get(id_name,"nick")
                email=cp_id.get(id_name,"email")
                user=nick+" <"+email+">"
                if article.user_agent.startswith("XPN") and user==article.from_name:
                    if mode=="Supersede":
                        self.win4=Edit_Win(self.configs,article.ngroups,article,None,self.subscribed_groups,"Supersede",server_name=self.current_server,id_name=id_name)
                        #self.win4.show()
                    else:
                        message=Dialog_YES_NO(_("Do you want to CANCEL this article?\n\nSubject: %s ""\nMessage-ID: %s") % (article.subj.encode("utf-8"),escape(article.msgid.encode("utf-8"))))

                        if message.resp:
                            canc_mess=Article_To_Send(article.ngroups,user,"cmsg cancel "+article.msgid,"",VERSION,"us-ascii",load_ordered_list(),["Cancel Message for "+article.msgid],["Control"],["cancel "+article.msgid],cp_id.get(id_name,"gen_mid"),cp_id.get(id_name,"fqdn"))
                            cancel_message=canc_mess.get_article()
                            message,articlePosted=self.connectionsPool[self.current_server].sendArticle(cancel_message)
                            if articlePosted:
                                self.statusbar.push(1,_("Cancel Article Sent: ")+message)
                            else:
                                self.statusbar.push(1,message)
                else:
                    self.statusbar.push(1,_("You can Cancel/Supersede only your articles"))

    def open_outbox_manager(self,obj):
        self.win_outbox=Outbox_Manager(self,VERSION)
        self.win_outbox.show()

            
    def open_edit_win(self,object,is_followup=False):
        group=""
        id_name=""
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        if iter_selected!=None:
            group=model.get_value(iter_selected,0)
            id_name=self.get_id_for_group(group)
        if is_followup:
            #this is a followup
            model,iter_selected=self.threads_pane.threads_tree.get_selection().get_selected()
            subj=""
            if iter_selected!=None:
                #subj=model.get_value(iter_selected,1).decode("utf-8")
                article=self.threads_pane.get_article(model,iter_selected)
                subj=article.subj
                group=article.original_group
                try:
                    article.ngroups
                except AttributeError:
                    self.statusbar.push(1,_("First you have to read the article"))
                else:
                    self.threads_pane.update_article_icon("fup")

                    bounds=self.article_pane.buffer.get_selection_bounds()
                    selected_text=None
                    if bounds:
                        start=bounds[0]
                        stop=bounds[1]
                        selected_text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8").split("\n")

                    newsgroups=group
                    if group!=article.ngroups:
                        #this is a crosspost
                        crosspost=True
                        newsgroups=article.ngroups
                    else:
                        crosspost=False
                    if article.fup_to!="":
                        newsgroups=article.fup_to
                        followup_to=True
                    else:
                        followup_to=False

                    if crosspost and not followup_to:
                        message=Dialog_YES_NO(_("This is a crosspost! \n Do you want to send the article only on the original newsgroup (%s) ?") % (group,))
                        if message.resp:
                            newsgroups=group
                    if followup_to:
                        if article.fup_to!="poster":
                            message=Dialog_YES_NO(_("Original Poster set \"Followup_to\" on %s,\n\nDo you want to send your article on the original newsgroup (%s) ?") % (article.fup_to,group))
                            if message.resp:
                                newsgroups=group
                        else:
                            message=Dialog_YES_NO(_("Original Poster set \"Followup_to: poster\",\n\nDo you want to reply by mail ?"))
                            if message.resp:
                                self.open_edit_mail_win(None)
                                return None
                            else:
                                newsgroups=group
                    self.win4=Edit_Win(self.configs,newsgroups,article,selected_text,self.subscribed_groups,server_name=self.current_server,id_name=id_name)
                    #self.win4.show()
        else:
            #this is a new post
            self.win4=Edit_Win(self.configs,group,None,None,self.subscribed_groups,server_name=self.current_server,id_name=id_name)
            #self.win4.show()


    def open_edit_mail_win(self,object):
        to_name=""
        id_name=""
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        if iter_selected!=None:
            group=model.get_value(iter_selected,0)
            id_name=self.get_id_for_group(group)

        model,iter_selected=self.threads_pane.threads_tree.get_selection().get_selected()
        subj=""
        if iter_selected!=None:
            #subj=model.get_value(iter_selected,1).decode("utf-8")
            article=self.threads_pane.get_article(model,iter_selected)
            subj=article.subj
            try:
                article.reply_to
            except AttributeError:
                self.statusbar.push(1,_("First you have to read the article"))
            else:
                self.threads_pane.update_article_icon("fup")
                if article.reply_to!="":
                    to_name=article.reply_to
                else:
                    to_name=article.from_name
                bounds=self.article_pane.buffer.get_selection_bounds()
                selected_text=None
                if bounds:
                    start=bounds[0]
                    stop=bounds[1]
                    selected_text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8").split("\n")

                self.win4=Edit_Mail_Win(self.configs,to_name,article,selected_text,id_name=id_name)
                self.win4.show()

    def open_about_dialog(self,object):
        self.about_dialog=About_Dialog(NUMBER)
        self.about_dialog.show()

    def delete_event(self,widget,event,data=None):
        self.mainwin_width,self.mainwin_height=self.window.get_size()
        self.mainwin_pos_x,self.mainwin_pos_y=self.window.get_position()
        return False

    def save_sizes(self):
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"rb")
        except IOError:
            sizes={}        
        else:
            sizes=cPickle.load(f)
        sizes["vpaned_pos"]=self.vpaned.get_position()
        sizes["hpaned_pos"]=self.hpaned.get_position()
        sizes["threads_col_status"]=self.threads_pane.column1.get_width()
        sizes["threads_col_subject"]=self.threads_pane.column2.get_width()
        sizes["threads_col_from"]=self.threads_pane.column3.get_width()
        sizes["threads_col_date"]=self.threads_pane.column4.get_width()
        sizes["threads_col_score"]=self.threads_pane.column5.get_width()
        sizes["groups_col1"]=self.groups_pane.column1.get_width()
        if not self.mainwin_width:
            sizes["mainwin_width"],sizes["mainwin_height"]=self.window.get_size()
        else:
            sizes["mainwin_width"]=self.mainwin_width
            sizes["mainwin_height"]=self.mainwin_height
        if not self.mainwin_pos_x:
            sizes["mainwin_pos_x"],sizes["mainwin_pos_y"]=self.window.get_position()
        else:
            sizes["mainwin_pos_x"]=self.mainwin_pos_x
            sizes["mainwin_pos_x"]=self.mainwin_pos_x
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"wb")
        except IOError:
            pass
        else:
            cPickle.dump(sizes,f,1)
            f.close()

    def save_checkmenu_options(self):
        self.configs["raw"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/raw").get_active()))
        self.configs["fixed"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/fixed").get_active()))
        self.configs["show_quote"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_quote").get_active()))
        self.configs["show_sign"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_sign").get_active()))
        self.configs["show_spoiler"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/spoiler").get_active()))
        self.configs["show_threads"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active()))
        self.configs["show_all_read_threads"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_all_read_threads").get_active()))
        self.configs["show_threads_without_watched"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads_without_watched").get_active()))
        self.configs["show_read_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_read_articles").get_active()))
        self.configs["show_unread_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unread_articles").get_active()))
        self.configs["show_kept_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_kept_articles").get_active()))
        self.configs["show_unkept_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unkept_articles").get_active()))
        self.configs["show_watched_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_watched_articles").get_active()))
        self.configs["show_ignored_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_ignored_articles").get_active()))
        self.configs["show_unwatchedignored_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unwatchedignored_articles").get_active()))
        self.configs["show_score_neg_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_neg_articles").get_active()))
        self.configs["show_score_zero_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_zero_articles").get_active()))
        self.configs["show_score_pos_articles"]=str(bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_pos_articles").get_active()))
        self.conf.write_configs()

    def update_checkmenu_options(self):
        if self.configs["raw"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/raw").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/raw").set_active(False)
        if self.configs["fixed"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/fixed").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/fixed").set_active(False)
        if self.configs["show_quote"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_quote").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_quote").set_active(False)
        if self.configs["show_sign"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_sign").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_sign").set_active(False)
        if self.configs["show_spoiler"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/spoiler").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_articles_opts/spoiler").set_active(False)
        if self.configs["show_threads"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").set_active(False)
        if self.configs["show_all_read_threads"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_all_read_threads").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_all_read_threads").set_active(False)
        if self.configs["show_threads_without_watched"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads_without_watched").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads_without_watched").set_active(False)
        if self.configs["show_read_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_read_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_read_articles").set_active(False)
        if self.configs["show_unread_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unread_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unread_articles").set_active(False)
        if self.configs["show_kept_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_kept_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_kept_articles").set_active(False)
        if self.configs["show_unkept_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unkept_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unkept_articles").set_active(False)
        if self.configs["show_watched_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_watched_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_watched_articles").set_active(False)
        if self.configs["show_ignored_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_ignored_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_ignored_articles").set_active(False)
        if self.configs["show_unwatchedignored_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unwatchedignored_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unwatchedignored_articles").set_active(False)
        if self.configs["show_score_neg_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_neg_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_neg_articles").set_active(False)
        if self.configs["show_score_zero_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_zero_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_zero_articles").set_active(False)
        if self.configs["show_score_pos_articles"]=="True":
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_pos_articles").set_active(True)
        else:
            self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_pos_articles").set_active(False)
      
    def destroy(self,widget):
        for connection in self.connectionsPool.itervalues():
            connection.closeConnection()
        self.save_sorting_type()
        self.save_sizes()
        self.save_checkmenu_options()
        self.purge_groups()
        try: os.remove(os.path.join(self.wdir,"xpn.lock"))
        except: pass
        gtk.main_quit()

    def save_sorting_type(self,obj=None):
        for n in range(1,5):
            col=self.threads_pane.threads_tree.get_column(n)
            if col.get_sort_indicator():
                order=col.get_sort_order()
                col_name=["Subject","From","Date","Score"][n-1]
                if order==gtk.SORT_ASCENDING:
                    ascend_order="True"
                else:
                    ascend_order="False"
                self.configs["ascend_order"]=ascend_order
                self.configs["sort_col"]=col_name
                self.conf.write_configs()
         
                
    
    def show_subscribed(self):
        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        
        list=self.art_db.getSubscribed()
        new_list=[]
        self.subscribed_groups=[]
        groups_to_open=[group[0] for group in list]
        self.art_db.addGroups(groups_to_open)
        for group in list:
            total,unread_number=self.art_db.getArticlesNumbers(group[0])
            new_list.append((group[0],str(unread_number)+" ("+str(total)+")"))
            self.subscribed_groups.append([group[0],group[2],group[3]]) #group_name,server_name,id_name
        self.groups_pane.show_list(new_list,True)
        self.threads_pane.clear()
        self.article_pane.clear()
        if path_list:
            self.groups_pane.select_row_by_path(path_list[0])

    def show_threads(self,group,search_type=None,text=None):
        art_fup=gtk.gdk.pixbuf_new_from_file("pixmaps/art_fup.xpm")
        art_body=gtk.gdk.pixbuf_new_from_file("pixmaps/art_body.xpm")
        art_unread=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unread.xpm")
        art_read=gtk.gdk.pixbuf_new_from_file("pixmaps/art_read.xpm")
        art_mark=gtk.gdk.pixbuf_new_from_file("pixmaps/art_mark.xpm")
        art_keep=gtk.gdk.pixbuf_new_from_file("pixmaps/art_keep.xpm")
        art_unkeep=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unkeep.xpm")
        art_watch=gtk.gdk.pixbuf_new_from_file("pixmaps/art_watch.xpm")
        art_unwatchignore=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unwatchignore.xpm")
        art_ignore=gtk.gdk.pixbuf_new_from_file("pixmaps/art_ignore.xpm")
        
        icons=(art_fup,art_body,art_unread,art_read,art_mark,art_keep,art_unkeep,art_watch,art_unwatchignore,art_ignore)

        show_read_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_read_articles").get_active())
        show_unread_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unread_articles").get_active())
        show_kept_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_kept_articles").get_active())
        show_unkept_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unkept_articles").get_active())
        show_watched_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_watched_articles").get_active())
        show_ignored_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_ignored_articles").get_active())
        show_unwatchedignored_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_unwatchedignored_articles").get_active())
        show_score_neg_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_neg_articles").get_active())
        show_score_zero_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_zero_articles").get_active())
        show_score_pos_articles=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_score_pos_articles").get_active())
        show_threads=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active())
        show_all_read_threads=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_all_read_threads").get_active())
        
        show_threads_without_watched=bool(self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads_without_watched").get_active())
        
        show_bools=(show_read_articles,show_unread_articles,show_kept_articles,show_unkept_articles,show_watched_articles,show_ignored_articles,show_unwatchedignored_articles,show_score_neg_articles,show_score_zero_articles,show_score_pos_articles,show_threads,show_all_read_threads)

        if group:
            self.window.set_title( "%s - XPN %s" % ( group, NUMBER ) )
        else:
            self.window.set_title( "XPN %s" % (NUMBER,) )

        if not group: return
        groups=[line[0] for line in self.groups_pane.model]
        if not group in groups: return 
            
        self.threads_pane.clear()
        model=self.threads_pane.new_model()

        article_tree = {}
        self.statusbar.push(1,_("Please Wait. Building Threads"))        
       
        def thread_alg_1(search_type=None,text=None):
            sort=True
            
            sorted=[]
            for xpn_article in self.art_db.getArticles(group,show_bools,False,search_type,text):
                sorted.append((xpn_article.secs,xpn_article))
                
            if sort:
                sorted.sort()
            articles=sorted
                
            for secs, xpn_article in articles:
                article_info = xpn_article.get_article_info(icons)
                nick,from_name,ref,subj,date,date_parsed=xpn_article.get_headers()
                msgid=xpn_article.msgid
                if show_threads:
                    try:
                        idx=ref.rindex("<")
                    except ValueError:
                        #Root node
                        article_tree[msgid] = (True, [], article_info)
                    else:
                        #Child node
                        last_ref=ref[idx:]
                        if last_ref in article_tree:
                            #I found the father
                            article_tree[last_ref][1].append(msgid)
                            article_tree[msgid] = (False, [], article_info)
                        else:
                            #Trying threading by subject
                            for old_article_msgid, (old_article_is_root, old_branchs, old_article_info) in article_tree.iteritems():
                                old_article_subj = old_article_info[1]
                                diff_len = len(subj) - len(old_article_subj)
                                if (old_article_subj in subj) and old_article_is_root and diff_len<=6:
                                    #Found a root article with similar subject
                                    article_tree[old_article_msgid][1].append(msgid)
                                    article_tree[msgid] = (False, [], article_info)
                                    break
                            else:
                                #In the list there aren't articles with similar subject
                                article_tree[msgid] = (True, [], article_info)
                else:
                    # we're populating "article_tree", but always with true because
                    # they're all "root nodes" (show_threads is false)
                    article_tree[msgid] = (True, [], article_info)

        def thread_alg_2(search_type=None,text=None):
            #t1=time.time()
            for xpn_article in self.art_db.getArticles(group,show_bools,False,search_type,text):
                article_info = xpn_article.get_article_info(icons)
                msgid=xpn_article.msgid
                #first create all the nodes
                article_tree[msgid] = (True, [], article_info)
            #t2=time.time()
            if show_threads:            
                for is_root,children,article_info in article_tree.itervalues():
                    xpn_article=article_info[4]
                    msgid=xpn_article.msgid
                    nick,from_name,ref,subj,date,date_parsed=xpn_article.get_headers()
                    try:
                        idx=ref.rindex("<")
                    except ValueError:
                        #Root node
                        pass
                    else:
                        #Child node
                        last_ref=ref[idx:]
                        if last_ref in article_tree:
                            #I found the father
                            article_tree[last_ref][1].append(msgid)
                            article_tree[msgid] = (False, article_tree[msgid][1], article_tree[msgid][2])

                #t3=time.time()
                #threading by subject
                orphaned=[(art_info[4].secs,art_info[4]) for mid,(is_root,children,art_info) in article_tree.iteritems() if (is_root and art_info[4].ref)]
                orphaned.sort()
                orp=orphaned[:]
                #t4=time.time()
                for secs,xpn_article in orphaned:
                    subj=xpn_article.subj
                    for is_root,children,art_info in article_tree.itervalues():
                        if is_root and not ((art_info[4].secs,art_info[4]) in orp):
                            old_xpn_article=art_info[4]
                            old_subj=old_xpn_article.subj
                            diff_len = len(subj) - len(old_subj)
                            if (old_subj in subj) and diff_len <=6:
                                article_tree[old_xpn_article.msgid][1].append(xpn_article.msgid)
                                article_tree[xpn_article.msgid] = (False, article_tree[xpn_article.msgid][1], article_tree[xpn_article.msgid][2])
                                break
                        else: continue
                    #found nothing but we can use this article as parent
                    else: #else of the for is not executed when break is called
                        orp.remove((xpn_article.secs,xpn_article))
                #t5=time.time()
                #print "Lettura degli articoli e prima passata:",t2-t1
                #print "Seconda passata, vegono riconosciuti i legami padre figlio:",t3-t2
                #print "Estrazione degli articoli orfani:", t4-t3
                #print "Terza passata, threading by subject:",t5-t4


        # here we apply all the "tree wide" filters
        def anyUnread(node):
            '''Recursive function to check if all the branch is read.'''
            (root, branchs, info) = article_tree[node]

            # if the node is unread, the whole branch has any unread
            if info[5]:  
                return True

            # if any of the sons is unread, just pass the flag to the previous call
            for branch in branchs:
                if anyUnread(branch):
                    return True

            # all my sons are read
            return False
        
        def anyWatched(node):
            (root, branchs, info) = article_tree[node]

            
            if info[11]==art_watch:  
                return True

            
            for branch in branchs:
                if anyWatched(branch):
                    return True
            
            return False

        
        
        if search_type:
            search_type=search_type.lower()
            text=text.lower()
            if search_type=="from": search_type="from_name"
            if search_type=="body": search_type="bodies.raw_body"
        
        
        try: self.configs["threading_method"]
        except KeyError: self.configs["threading_method"]="2"
        if self.configs["threading_method"]=="2": thread_alg_2(search_type,text)
        else:                                     thread_alg_1(search_type,text)


        if not show_all_read_threads:
            roots = [k for k,v in article_tree.iteritems() if v[0]]
            for article_root in roots:
                if not anyUnread(article_root):
                    del article_tree[article_root]
        

        if not show_threads_without_watched:
            roots = [k for k,v in article_tree.iteritems() if v[0]]
            for article_root in roots:
                if not anyWatched(article_root):
                    del article_tree[article_root]
        
        def walkTree(node, iter_mom):
            '''Recursive function to build the articles tree in the GTK Widget.'''
            # took the info about the article in the node
            (root, branchs, info) = article_tree[node]
            if info[5]:
                unread_in_thread = 1
            else:
                unread_in_thread = 0
            
            if info[11]==art_watch:
                watched_in_thread = 1
            else:
                watched_in_thread = 0
            
            watched_unread_in_thread = unread_in_thread and watched_in_thread

            # tell TreeStore to build a branch
            iter_new = self.threads_pane.insert(model, iter_mom, None, info)

            # build all its sons
            for branch in branchs:
                (node_iter, more_unread, more_watched, more_watched_unread) = walkTree(branch, iter_new)
                unread_in_thread += more_unread
                watched_in_thread += more_watched
                watched_unread_in_thread += more_watched_unread

            return (iter_new, unread_in_thread, watched_in_thread, watched_unread_in_thread)

        # with the help of walkTree, we'll build... well... the tree
        roots = [k for k,v in article_tree.iteritems() if v[0]]
        for article_root in roots:
            # start a branch from its root
            (root_iter, unread_in_thread, watched_in_thread, watched_unread_in_thread) = walkTree(article_root, None)

            # show how many unread items the branch has
            self.threads_pane.set_unread_in_thread(model, root_iter, unread_in_thread)
            self.threads_pane.set_unread_in_thread_visible(model, root_iter, unread_in_thread!=0)
            
            self.threads_pane.set_watched_in_thread(model, root_iter, watched_in_thread)
            self.threads_pane.set_watched_unread_in_thread(model, root_iter, watched_unread_in_thread)

        message=_("%s selected") % (group,)
        self.statusbar.push(1,message)
        self.threads_pane.set_model(model)
        #adjust sorting
        model=self.threads_pane.threads_tree.get_model()
        sort_col=self.configs["sort_col"].lower()
        sortings={"subject":1,"from":2,"date":6,"score":7}
        sort_col=sortings.get(sort_col,6)
        if self.configs["ascend_order"]=="True":
            sort_order=gtk.SORT_ASCENDING
        else:
            sort_order=gtk.SORT_DESCENDING
        model.set_sort_column_id(sort_col,sort_order)

    def get_server_for_group(self,group_name):
        server_name=""
        for group,server,id in self.subscribed_groups:
            if group==group_name: server_name=server
        return server_name

    def get_id_for_group(self,group_name):
        id_name=""
        for group,server,id in self.subscribed_groups:
            if group==group_name: id_name=id
        return id_name

    def view_group(self,*params):
        clicktype=params[-1]
        if self.configs["oneclick"]=="True" and clicktype=="doubleclick": return
        if self.configs["oneclick"]=="False" and clicktype=="oneclick": return
        if self.groups_lock==False:
            self.groups_lock=True
            model,path_list,iter_list=self.groups_pane.get_selected_rows()
            if iter_list:
                self.group_to_thread=model.get_value(iter_list[0],0)
                self.current_server=self.get_server_for_group(self.group_to_thread)
                self.article_pane.clear()
                self.show_threads(self.group_to_thread)
                self.msgids[self.group_to_thread]=None
            self.groups_lock=False
            if self.configs["expand_group"]=="True": self.expand_all_threads(None,True)

    def mark_for_download(self,article):
        '''mark article for download'''
        article.marked_for_download=not article.marked_for_download
        self.art_db.updateArticle(self.group_to_thread,article)


    def mark_subthread_for_download(self,model,root_iter,force_value=None):
        '''mark subthread for download'''
        xpn_article=self.threads_pane.get_article(model,root_iter)
        #let's mark the root article
        if force_value==True:
            if xpn_article.body==None:
                xpn_article.marked_for_download=force_value
        elif force_value==False:
            xpn_article.marked_for_download=force_value
        else:
            status=not xpn_article.marked_for_download
            if status==True:
                if xpn_article.body==None:
                    xpn_article.marked_for_download=status
            else:
                xpn_article.marked_for_download=status
        if xpn_article.marked_for_download:
            self.threads_pane.update_article_icon("download",root_iter)
        else:
            if xpn_article.is_read:
                self.threads_pane.update_article_icon("read",root_iter)
            elif xpn_article.body!=None:
                self.threads_pane.update_article_icon("body",root_iter)
            else:
                self.threads_pane.update_article_icon("unread",root_iter)
        self.art_db.updateArticle(self.group_to_thread,xpn_article)
        self.threads_pane.set_article(model,root_iter,xpn_article)
        
        iter_list=self.threads_pane.get_subthread(root_iter,model,[])
        
        for iter_child in iter_list:
            xpn_sub_article=self.threads_pane.get_article(model,iter_child)
            #watching others articles in the subthread
            if force_value==True:
                if xpn_sub_article.body==None:
                    xpn_sub_article.marked_for_download=force_value
            elif force_value==False:
                xpn_sub_article.marked_for_download=force_value
            else:
                status=xpn_article.marked_for_download
                if status==True:
                    if xpn_sub_article.body==None:
                        xpn_sub_article.marked_for_download=status
                else:
                    xpn_sub_article.marked_for_download=status
            
            if xpn_sub_article.marked_for_download:
                self.threads_pane.update_article_icon("download",iter_child)
            else:
                if xpn_sub_article.is_read:
                    self.threads_pane.update_article_icon("read",iter_child)
                elif xpn_sub_article.body!=None:
                    self.threads_pane.update_article_icon("body",iter_child)
                else:
                    self.threads_pane.update_article_icon("unread",iter_child)
            
            self.art_db.updateArticle(self.group_to_thread,xpn_sub_article)
            self.threads_pane.set_article(model,iter_child,xpn_sub_article)

        

    def mark_group_for_download(self,group):
        '''mark the whole group for download'''
        if group:
            self.art_db.markGroupForDownload(group)
            self.view_group(None,None)
    
    def keep_subthread(self, model, root_iter):
        xpn_root_article=self.threads_pane.get_article(model,root_iter)
        status= xpn_root_article.keep
        xpn_root_article.keep=not status
        if status:
            self.threads_pane.update_article_icon("unkeep",root_iter)
        else:
            self.threads_pane.update_article_icon("keep",root_iter)
        self.art_db.updateArticle(self.group_to_thread,xpn_root_article)
        self.threads_pane.set_article(model,root_iter,xpn_root_article)

        iter_list=self.threads_pane.get_subthread(root_iter,model,[])
        for iter_child in iter_list:
            xpn_sub_article=self.threads_pane.get_article(model,iter_child)
            xpn_sub_article.keep=not status
            if status:
                self.threads_pane.update_article_icon("unkeep",iter_child)
            else:
                self.threads_pane.update_article_icon("keep",iter_child)
            self.art_db.updateArticle(self.group_to_thread,xpn_sub_article)
            self.threads_pane.set_article(model,iter_child,xpn_sub_article)
    
                    

        
    def mark_subthread_read(self,model,root_iter,read):
        xpn_root_article=self.threads_pane.get_article(model,root_iter)
        if read:
            self.remove_from_unreads(xpn_root_article)
            self.threads_pane.update_article_icon("read",root_iter)
            self.threads_pane.set_is_unread(model,root_iter,False)
        else:
            self.insert_in_unreads(xpn_root_article)
            if xpn_root_article.body==None: self.threads_pane.update_article_icon("unread",root_iter)
            else: self.threads_pane.update_article_icon("body",root_iter)
            self.threads_pane.set_is_unread(model,root_iter,True)
        self.threads_pane.set_article(model,root_iter,xpn_root_article)

        iter_list=self.threads_pane.get_subthread(root_iter,model,[])
        for iter_child in iter_list:
            xpn_sub_article=self.threads_pane.get_article(model,iter_child)
            if read:
                self.remove_from_unreads(xpn_sub_article)
                self.threads_pane.update_article_icon("read",iter_child)
                self.threads_pane.set_is_unread(model,iter_child,False)
            else:
                self.insert_in_unreads(xpn_sub_article)
                if xpn_sub_article.body==None: self.threads_pane.update_article_icon("unread",iter_child)
                else: self.threads_pane.update_article_icon("body",iter_child)
                self.threads_pane.set_is_unread(model,iter_child,True)
            self.threads_pane.set_article(model,iter_child,xpn_sub_article)
                    
            
    
    def set_keep(self,article,group):
        '''set keep flag'''
        article.keep=not article.keep
        self.art_db.updateArticle(group,article)


    def set_watch(self,model,root_iter):
        #set watch flag and mark on subthread
        xpn_article=self.threads_pane.get_article(model,root_iter)
        xpn_article.watch=not xpn_article.watch
        
        show_threads=self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active()
        
        if xpn_article.watch:
            xpn_article.ignore=False
            self.threads_pane.update_article_icon("watch",root_iter)
            self.threads_pane.update_watched_in_thread(xpn_article.watch,show_threads,True)
            self.threads_pane.update_watched_unread_in_thread(xpn_article.is_read,xpn_article.watch,show_threads,False,True,False)
        else:
            self.threads_pane.update_article_icon("unwatchignore",root_iter)
            self.threads_pane.update_watched_in_thread(xpn_article.watch,show_threads,False)
            self.threads_pane.update_watched_unread_in_thread(xpn_article.is_read,xpn_article.watch,show_threads,False,False,False)
        self.threads_pane.set_article(model,root_iter,xpn_article)
        self.art_db.updateArticle(self.group_to_thread,xpn_article)
        
        iter_list=self.threads_pane.get_subthread(root_iter,model,[])
        
        for iter_child in iter_list:
            #watching others articles in the subthread
            xpn_sub_article=self.threads_pane.get_article(model,iter_child)

            xpn_sub_article.watch=xpn_article.watch
            if xpn_sub_article.watch:
                self.threads_pane.update_article_icon("watch",iter_child)
                self.threads_pane.update_watched_in_thread(xpn_article.watch,show_threads,True)
                self.threads_pane.update_watched_unread_in_thread(xpn_article.is_read,xpn_article.watch,show_threads,False,True,False)
            else:
                self.threads_pane.update_article_icon("unwatchignore",iter_child)
                self.threads_pane.update_watched_in_thread(xpn_article.watch,show_threads,False)
                self.threads_pane.update_watched_unread_in_thread(xpn_article.is_read,xpn_article.watch,show_threads,False,False,False)
            xpn_sub_article.ignore=False
            self.art_db.updateArticle(self.group_to_thread,xpn_sub_article)
            self.threads_pane.set_article(model,iter_child,xpn_sub_article)

        self.mark_subthread_for_download(model,root_iter,xpn_article.watch)
    
    def set_ignore(self,model,root_iter):
        #set ignore flag and unmark on subthread
        xpn_article=self.threads_pane.get_article(model,root_iter)
        xpn_article.ignore=not xpn_article.ignore
        show_threads=self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active()
        
        if xpn_article.watch:
            self.threads_pane.update_watched_in_thread(False,show_threads,False)
            self.threads_pane.update_watched_unread_in_thread(xpn_article.is_read,False,show_threads,False,False,False)
        
        if xpn_article.ignore:
            xpn_article.watch=False
            self.remove_from_unreads(xpn_article)
            self.threads_pane.update_article_icon("ignore",root_iter)
        else:
            self.insert_in_unreads(xpn_article)
            self.threads_pane.update_article_icon("unwatchignore",root_iter)
        self.threads_pane.set_article(model,root_iter,xpn_article)
        self.threads_pane.set_is_unread(model,root_iter,not xpn_article.is_read)
        
        iter_list=self.threads_pane.get_subthread(root_iter,model,[])
        
        for iter_child in iter_list:
            #watching others articles in the subthread
            xpn_sub_article=self.threads_pane.get_article(model,iter_child)
            xpn_sub_article.ignore=xpn_article.ignore
            if xpn_sub_article.ignore:
                xpn_sub_article.watch=False
                self.remove_from_unreads(xpn_sub_article)
                self.threads_pane.update_article_icon("ignore",iter_child)
            else:
                xpn_sub_article.watch=False
                self.insert_in_unreads(xpn_sub_article)
                self.threads_pane.update_article_icon("unwatchignore",iter_child)
            self.threads_pane.set_article(model,iter_child,xpn_sub_article)
            self.threads_pane.set_is_unread(model,iter_child,not xpn_sub_article.is_read)
        self.mark_subthread_for_download(model,root_iter,xpn_article.watch)

    def insert_in_unreads(self,article):
        #reinsert article in unreads
        self.groups_pane.update_read_vs_unread(article.is_read,True)
        show_threads=self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active()
        self.threads_pane.update_unread_in_thread(article.is_read,show_threads,True)
        self.threads_pane.update_watched_unread_in_thread(article.is_read,article.watch,show_threads,True,False,True)
        
        article.is_read=False
        self.art_db.updateArticle(self.group_to_thread,article)



    def remove_from_unreads(self,article):
        #remove article from unreads
        self.groups_pane.update_read_vs_unread(article.is_read,False)
        show_threads=self.ui.get_widget("/MainMenuBar/View/view_group_opts/show_threads").get_active()
        self.threads_pane.update_unread_in_thread(article.is_read,show_threads,False)
        self.threads_pane.update_watched_unread_in_thread(article.is_read,article.watch,show_threads,False,False,True)
        article.is_read=True
        self.art_db.updateArticle(self.group_to_thread,article)

    def show_article(self,article):
        self.article_pane.delete_all()
        vadj=self.article_pane.text_scrolledwin.get_vadjustment()
        vadj.set_value(0)
        is_sign=False
        is_quote=False
        line_number=0
        mute_quote=not bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_quote").get_active())
        mute_quote_text_inserted=False
        mute_sign=not bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/show_sign").get_active())
        mute_sign_text_inserted=False

        RE_bold=r"(?:^|.)(\*.+?\*)(?=.|$)"
        RE_underline=r"(?:^|[.,:;\s(])(_.+?_)(?=[.,:;\s)]|$)"
        RE_italic=r"(?:^|[.,:;\s(])(/.+?/)(?=[.,:;\s)]|$)"
        RE_url=r"(https?://[-a-zA-Z0-9_$.+!*(),;:@%&=?~#'/]*[-a-zA-Z0-9_$+!*(@%&=?~#/])"
        RE_mid=r"(?:^|.)(?:<)([-a-zA-Z0-9_$.+!*(),;:%&=?~#'/]+@[-a-zA-Z0-9_$.+!*(),;:%&=?~#'/]+)(?:>)(?=.|$)"
        compiled_bold=re.compile(RE_bold,re.UNICODE|re.DOTALL)
        compiled_underline=re.compile(RE_underline,re.UNICODE)
        compiled_italic=re.compile(RE_italic,re.UNICODE|re.DOTALL)
        compiled_url=re.compile(RE_url)
        compiled_mid=re.compile(RE_mid)

        def quote_depth(line):
            count=0
            for char in line:
                if char==">":
                    count=count+1
                else:
                    break
            if count>3:
                count=3
            if count==0: #this prevent a warning during the mute_quote mode
                count=1
            return str(count)
        
        for line in article:
            line=line.replace("\r","") #this is needed for some strange articles
            insert_newline=True
            if len(line)>0:
                if line[0]==">":
                    is_quote=True
                elif (len(line)==2 and line[0:2]=="--") or (len(line)==3 and line[0:3]=="-- "):
                    is_sign=True
                    is_quote=False
                else:
                    is_quote=False
                tag_prefix=""
                
                if is_quote and not is_sign:
                    if mute_quote:
                        if mute_quote_text_inserted:
                            line=""
                            insert_newline=False
                        else:
                            line=_("> [...Muted Quote...]")
                            mute_quote_text_inserted=True
                    quote_level=quote_depth(line)
                    
                    self.article_pane.insert_with_tags(line,"quote"+quote_level)
                    tag_prefix="quote"+quote_level

                elif is_sign:
                    if mute_sign:
                        if mute_sign_text_inserted:
                            line=""
                            insert_newline=False
                        else:
                            line=_("[...Muted Sign...]")
                            mute_sign_text_inserted=True
                    self.article_pane.insert_with_tags(line,"sign")
                    tag_prefix="sign"
                    mute_quote_text_inserted=False

                else:
                    self.article_pane.insert_with_tags(line,"text")
                    tag_prefix="text"
                    mute_quote_text_inserted=False

                matches_bold=compiled_bold.finditer(line)
                matches_underline=compiled_underline.finditer(line)
                matches_italic=compiled_italic.finditer(line)
                matches_url=compiled_url.finditer(line)
                matches_mid=compiled_mid.finditer(line)
                
                self.apply_styles(matches_bold,tag_prefix,"_bold",line_number,1)
                self.apply_styles(matches_underline,tag_prefix,"_underline",line_number,1)
                self.apply_styles(matches_italic,tag_prefix,"_italic",line_number,1)
                self.apply_styles(matches_url,"","url",line_number,0)
                self.apply_styles(matches_mid,"","mid",line_number,1)
                
            if insert_newline:
                self.article_pane.insert("\n")
                line_number=line_number+1
        if self.ui.get_widget("/MainMenuBar/View/view_articles_opts/spoiler").get_active()==False:
            self.apply_spoiler()
        if self.ui.get_widget("/MainMenuBar/View/view_articles_opts/raw").get_active()==True:
            self.highlight_headers()

    def apply_styles(self,style_matched,tagPrefix,tagSuffix,line_number,group_number):
        for match in style_matched:
            iter_start=self.article_pane.buffer.get_start_iter()
            iter_start.set_line(line_number)
            iter_stop=iter_start.copy()
            iter_start.set_line_offset(match.start(group_number))
            iter_stop.set_line_offset(match.end(group_number))
            self.article_pane.buffer.delete(iter_start,iter_stop)
            self.article_pane.insert_with_tags_at_iter(iter_start,match.group(group_number),tagPrefix+tagSuffix)

    def highlight_headers(self):
        bounds=self.article_pane.buffer.get_bounds()
        RE_header="^.+?:"
        if bounds:
            start,stop=bounds
            text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8")
            text_splitted=text.splitlines()
            if "" in text_splitted:
                index=text_splitted.index("")
            else:
                index=0
            i=0
            headers_block=[]
            for i in range(index):
                headers_block.append(text_splitted[i])
            text='\n'.join(headers_block)
            match_header=re.compile(RE_header,re.UNICODE|re.MULTILINE).finditer(text)
            for match in match_header:
                match_start,match_stop,match_text= match.start(), match.end(), match.group()
                iter_start=self.article_pane.buffer.get_iter_at_offset(match_start)
                iter_stop=self.article_pane.buffer.get_iter_at_offset(match_stop)
                self.article_pane.buffer.delete(iter_start,iter_stop)
                self.article_pane.insert_with_tags_at_iter(iter_start,match_text,"quote1_bold")

    def apply_spoiler(self):
        bounds=self.article_pane.buffer.get_bounds()
        RE_spoiler=chr(12)+".+?"+chr(12)
        if bounds:
            start,stop=bounds
            text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8")
            matchs_spoiler=re.compile(RE_spoiler,re.UNICODE|re.DOTALL).finditer(text)
            for match in matchs_spoiler:
                match_start,match_stop,match_text= match.start(), match.end(), match.group()

                iter_start=self.article_pane.buffer.get_iter_at_offset(match_start)
                iter_stop=self.article_pane.buffer.get_iter_at_offset(match_stop)
                self.article_pane.buffer.delete(iter_start,iter_stop)
                self.article_pane.insert_with_tags_at_iter(iter_start,match_text,"spoiler")

            if divmod(text.count(chr(12)),2)[1]!=0:
                #the number of spoiler chars is an odd number
                pos=text.rindex(chr(12))
                iter_start=self.article_pane.buffer.get_iter_at_offset(pos)
                iter_stop=self.article_pane.buffer.get_end_iter()
                match_text=self.article_pane.buffer.get_text(iter_start,iter_stop)
                self.article_pane.buffer.delete(iter_start,iter_stop)
                self.article_pane.insert_with_tags_at_iter(iter_start,match_text,"spoiler")

 

    def retrieve_body(self,article_to_read,group,server_name=None,single_retrieve=True):
        if not server_name: 
            if self.current_server:
                server_name=self.current_server
            else:
                server_name=self.get_server_for_group(group)
        self.article_pane.textview.grab_focus()
        message=""
        bodyRetrieved=True
        body,bodyRetrieved,message=self.art_db.retrieveBody(article_to_read,group,server_name,self.connectionsPool,single_retrieve)
        if single_retrieve: self.statusbar.push(1,message)
        return body,bodyRetrieved

    def view_article(self,*params):
        #params=obj,path,column,clicktype
        def return_part_number(obj):
            self.part_to_show=0
            i=0
            for button in self.article_pane.multiparts_buttons:
                if obj==button:
                    self.part_to_show=i
                i=i+1
            self.view_article("oneclick")

        def get_and_show_body(article_to_read,body):
            try: article_to_read.body_parts
            except: pass
            else:
                self.article_pane.add_parts_buttons(article_to_read.body_parts)
                for button in self.article_pane.multiparts_buttons: button.connect("released",return_part_number)
                try: 
                    body=article_to_read.body_parts[self.part_to_show][1].splitlines()
                    self.article_pane.multiparts_buttons[self.part_to_show].set_active(True)
                except: body=article_to_read.body_parts[0][1].splitlines()
            if show_raw and bodyRetrieved:
                body=article_to_read.get_raw()
            self.show_article(body)

        
        clicktype=params[-1]
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        show_raw=bool(self.ui.get_widget("/MainMenuBar/View/view_articles_opts/raw").get_active())
        if iter_selected!=None:
            article_to_read=self.threads_pane.get_article(model,iter_selected)
            self.msgids[self.group_to_thread]=article_to_read.msgid
            if self.configs["oneclick_article"]=="True" and clicktype=="doubleclick": return
            if self.configs["oneclick_article"]=="False" and clicktype=="oneclick":
                self.article_pane.clear()
                self.article_pane.update_headers_labels(article_to_read)
                #body=article_to_read.get_body()
                if (article_to_read.is_read) and (article_to_read.has_body):
                    body=self.art_db.getBodyFromDB(article_to_read.original_group,article_to_read)
                    bodyRetrieved=True
                    get_and_show_body(article_to_read,body)
                    self.article_pane.update_headers_labels(article_to_read)

                self.article_pane.set_face_x_face(article_to_read.face,article_to_read.x_face)
                return
            
            #self.article_pane.textview.grab_focus()
            body,bodyRetrieved=self.retrieve_body(article_to_read,article_to_read.original_group)

########AGGIUSTARE QUA###################
######QUANDO IL CORPO E' VUOTO BODY E' FALSO E IL PROGRAMMA NON VA AVANTI###########
#####PER IL MOMENTO METTO !=NONE MA E' DA VERIFICARE NEI CASI DI ERRORI###########
            if body!=None:
                self.article_pane.clear()
                if bodyRetrieved:
                    self.threads_pane.set_is_unread(model,iter_selected,False)
                    self.threads_pane.update_article_icon("read")
                    self.remove_from_unreads(article_to_read)
                    self.article_pane.update_headers_labels(article_to_read)

                get_and_show_body(article_to_read,body)
                self.article_pane.set_face_x_face(article_to_read.face,article_to_read.x_face)

            self.threads_pane.threads_tree.grab_focus()


    def view_next_article(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        column=self.threads_pane.threads_tree.get_column(0)

        if iter_selected==None:
            iter_new=model.get_iter_first()
        else:
            path=model.get_path(iter_selected)        
            iter_new=self.threads_pane.find_next_row(model,iter_selected)
        if iter_new!=None:
            path=model.get_path(iter_new)
            self.threads_pane.threads_tree.expand_row(path,False)
            #need these 3 lines to update the view and correctly point the cursor
            self.threads_pane.threads_tree.queue_draw()
            while gtk.events_pending():
                gtk.main_iteration(False)
            self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
            self.threads_pane.threads_tree.set_cursor(path,None,False)
            self.threads_pane.threads_tree.row_activated(path,column)

    def view_next_unread_article(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        column=self.threads_pane.threads_tree.get_column(0)
        if iter_selected==None:
            iter_selected=model.get_iter_first()
        if iter_selected!=None:
            read_status=self.threads_pane.get_is_unread(model,iter_selected)
        else:
            read_status=False
        while (not read_status) and (iter_selected!=None):
            iter_selected=self.threads_pane.find_next_row(model,iter_selected)
            if iter_selected!=None:
                read_status=self.threads_pane.get_is_unread(model,iter_selected)
            else:
                read_status=False
        if read_status:
            path=model.get_path(iter_selected)
            root_path=[]
            root_path.append(path[0])
            root_path=tuple(root_path)
            self.threads_pane.threads_tree.expand_row(root_path,True)
            #need these 3 lines to update the view and correctly point the cursor
            self.threads_pane.threads_tree.queue_draw()
            while gtk.events_pending():
                gtk.main_iteration(False)
            self.threads_pane.threads_tree.grab_focus()
            self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
            self.threads_pane.threads_tree.set_cursor(path,None,False)
            self.threads_pane.threads_tree.row_activated(path,column)




    def view_previous_article(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        column=self.threads_pane.threads_tree.get_column(0)
        if iter_selected==None:
            iter_new=model.get_iter_first()
        else:
            iter_new=self.threads_pane.find_previous_row(model,iter_selected)
        if iter_new!=None:
            path=model.get_path(iter_new)
            self.threads_pane.threads_tree.set_cursor(path,None,False)
            self.threads_pane.threads_tree.row_activated(path,column)

    def view_parent_article(self,obj):
        model,iter_son=self.threads_pane.threads_tree.get_selection().get_selected()
        if iter_son!=None:
            article_son=self.threads_pane.get_article(model,iter_son)
            references=article_son.ref
            if references=="":
                self.statusbar.push(1,_("This is root article"))
            else:
                idx=references.rindex("<")
                last_ref=references[idx:]

                #First search the parent in the threaded articles
                iter_current=model.get_iter_first()
                success=False
                while iter_current!=None and not success:
                    article_mom=self.threads_pane.get_article(model,iter_current)
                    if article_mom.msgid==last_ref:
                        #It is in the threads, let's show the article selecting its row
                        path=model.get_path(iter_current)
                        self.threads_pane.threads_tree.set_cursor(path,None,False)
                        self.threads_pane.threads_tree.row_activated(path,self.threads_pane.column1)
                        self.statusbar.push(1,_("Article Found"))
                        success=True
                    else:
                        iter_current=self.threads_pane.find_next_row(model,iter_current)

                if not success:
                    #Let' search the article on the server
                    message,number=self.connectionsPool[self.current_server].getArticleNumber(article_son.original_group,last_ref)
                    self.statusbar.push(1,message)
                    if number!=-1:
                        message,headers,last=self.connectionsPool[self.current_server].getHeaders(article_son.original_group,number,number)
                        self.statusbar.push(1,message)
                        if headers:
                            number,subj,from_name,date,msgid,ref,bytes,lines,xref=headers[0]
                            #If it is not in the threaded articles, let's insert a node for this article
                            article=Article(number,msgid,from_name,ref,subj,date,self.configs["fallback_charset"],article_son.original_group,xref,bytes,lines)
                            #applying score rules
                            score=self.score_rules.apply_score_rules(article,article.original_group)
                            article.set_score(score)
                            nick,from_name,ref,subj,date,date_parsed=article.get_headers()
                            art_unread=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unread.xpm")
                            art_unkeep=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unkeep.xpm")

                            if score<0:
                                score_foreground="red"
                            else:
                                score_foreground="darkgreen"
                            if score==0:
                                show_score=False
                            else:
                                show_score=True     
                            
                            iter_new=self.threads_pane.insert(model,None,iter_son,[art_unread,subj,nick,date_parsed,article,True,article.secs,article.score,score_foreground,show_score,art_unkeep,])
                            path=model.get_path(iter_new)
                            self.threads_pane.threads_tree.set_cursor(path,None,False)
                            self.threads_pane.threads_tree.row_activated(path,self.threads_pane.column1)
                            self.statusbar.push(1,_("Article loaded"))
                        else:
                            self.statusbar.push(1,_("This article is not available on the server"))
                    else:
                        self.statusbar.push(1,_("This article is not available on the server"))

    def show_activity_list(self,activity_list):
        msg=_("There are new articles in watched threads: ")
        report=""
        if activity_list:
            for group,number in activity_list.iteritems():
                report+=group+": "+str(number)+"\n"
            d=Dialog_OK(msg+"\n\n"+report)

    def get_new_headers(self,obj):
        "Download new headers for the subscribed"
        subscribed=self.art_db.getSubscribed()
        activity_list=dict()
        for group in subscribed:
            s1=len(self.art_db.getWatched(group[0]))
            group[1]=self.download_headers(group[0],group[1],group[2])
            s2=len(self.art_db.getWatched(group[0]))
            if s2>s1: activity_list[group[0]]=s2-s1
        self.art_db.updateSubscribed(subscribed)
        self.statusbar.push(1,_("Download Completed"))
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        msgid_selected=self.msgids.get(self.group_to_thread,None)
        self.show_subscribed()
        if iter_selected:
            self.groups_pane.groups_list.set_cursor(path,None,False)
            self.groups_pane.groups_list.row_activated(path,self.groups_pane.groups_list.get_column(0))
        self.show_activity_list(activity_list)
        self.select_article_again(msgid_selected)
        return True #for timeout_add
        
    def select_article_again(self,msgid_selected):
        #let's select again the selected article
        if msgid_selected:
            treesel=self.threads_pane.threads_tree.get_selection()
            model,iter_selected=treesel.get_selected()
            iter_new=model.get_iter_first()
            while iter_new:
                article=self.threads_pane.get_article(model,iter_new)
                path=model.get_path(iter_new)
                if article.msgid == msgid_selected:
                    if len(path)>1: self.threads_pane.threads_tree.expand_row((path[0],),True)
                    self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
                    self.threads_pane.threads_tree.set_cursor(path,None,False)
                iter_new=self.threads_pane.find_next_row(model,iter_new)

    
    def get_new_headers_selected(self,obj):
        "Dowload new headers for selected group"
        subscribed=self.art_db.getSubscribed()
        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        activity_list=dict()
        msgid_selected=self.msgids.get(self.group_to_thread,None)
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_name=model.get_value(iter_selected,0)
            for group in subscribed:
                if group[0]==group_name:
                    s1=len(self.art_db.getWatched(group[0]))
                    group[1]=self.download_headers(group[0],group[1],group[2])
                    s2=len(self.art_db.getWatched(group[0]))
                    if s2>s1: activity_list[group_name]=s2-s1
        self.art_db.updateSubscribed(subscribed)
        if path_list:
            self.show_subscribed()
            self.groups_pane.groups_list.set_cursor(path_list[0],None,False)
            self.groups_pane.groups_list.row_activated(path_list[0],self.groups_pane.groups_list.get_column(0))
            self.show_activity_list(activity_list)
        self.select_article_again(msgid_selected)

    def download_headers(self,group,last_number,server_name):
        first=int(last_number)+1
        #Downloading headers
        self.progressbar.set_text(_("Fetching Headers"))
        self.progressbar.set_fraction(1/float(2))
        while gtk.events_pending():
            gtk.main_iteration(False)
        if self.configs["limit_articles"]=="True":
            articles_number=int(self.configs["limit_articles_number"])
            message,total_headers,last=self.connectionsPool[server_name].getHeaders(group,first,count=articles_number)
        else:            
            message,total_headers,last=self.connectionsPool[server_name].getHeaders(group,first)
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

        self.art_db.addHeaders(group,total_headers,server_name,self.connectionsPool)

        self.progressbar.set_fraction(0)
        self.progressbar.set_text("")
        return last_number

    def reapply_score_actions_rules(self,obj):
        subscribed=self.art_db.getSubscribed()

        j=0
        for group in subscribed:
            j=j+1
            self.progressbar.set_fraction(j/float(len(subscribed)))
            self.progressbar.set_text("%s / %s" % (j,len(subscribed)))
            self.statusbar.push(1,_("Refreshing Group %s") % group[0])
            while gtk.events_pending():
                gtk.main_iteration(False)

            for xpn_article in self.art_db.getArticles(group[0]):
                xpn_article.reset_article_score_actions()
                self.art_db.updateArticle(group[0],xpn_article)
            
            self.art_db.reapply_rules(group[0],group[2],self.connectionsPool)
                
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        if iter_selected:
            self.show_subscribed()
            self.groups_pane.groups_list.set_cursor(path,None,False)
            self.groups_pane.groups_list.row_activated(path,self.groups_pane.groups_list.get_column(0))
        self.progressbar.set_fraction(0)
        self.progressbar.set_text("")
        self.statusbar.push(1,"")

    def get_bodies(self,obj):
        "Download bodies for marked articles"
                
        subscribed=self.art_db.getSubscribed()
        
        
        i=0
        length=float(len(subscribed))
        for group in subscribed:
            i=i+1
            self.progressbar.set_fraction(i/length)
            self.download_bodies(group[0],group[2])
        self.threads_pane.clear()
        self.article_pane.clear()
        self.progressbar.set_fraction(0)
        self.progressbar.set_text("")
        self.statusbar.push(1,_("Download Completed"))
        model,path,iter_selected=self.groups_pane.get_first_selected_row()
        msgid_selected=self.msgids.get(self.group_to_thread,None)
        if iter_selected:
            self.show_subscribed()
            self.groups_pane.groups_list.set_cursor(path,None,False)
            self.groups_pane.groups_list.row_activated(path,self.groups_pane.groups_list.get_column(0))
        self.select_article_again(msgid_selected)

    def get_bodies_selected(self,obj):
        "Download bodies for marked articles in selected group"
        
        subscribed=self.art_db.getSubscribed()

        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_name=model.get_value(iter_selected,0)
            for group in subscribed:
                if group[0]==group_name:
                    self.download_bodies(group[0],group[2])
        msgid_selected=self.msgids.get(self.group_to_thread,None)
        if path_list:
            self.threads_pane.clear()
            self.article_pane.clear()
            self.progressbar.set_fraction(0)
            self.progressbar.set_text("")
            self.statusbar.push(1,_("Download Completed"))
            self.groups_pane.groups_list.set_cursor(path_list[0],None,False)
            self.groups_pane.groups_list.row_activated(path_list[0],self.groups_pane.groups_list.get_column(0)) 
        self.select_article_again(msgid_selected)
        
    def download_bodies(self,group,server_name):
        self.statusbar.push(1,_("Downloading Bodies for %s") % (group,))
        marked_articles=[]
        for article in self.art_db.getArticles(group):
            if article.marked_for_download:
                marked_articles.append(article)
        #j=0
        #length=len(marked_articles)
        for article in marked_articles:
            #j=j+1
            body,bodyRetrieved=self.retrieve_body(article,group,server_name,False)
            #self.progressbar.set_fraction(j/float(length))
            #self.progressbar.set_text(_("Downloading %s of %s") % (j,length))
            while gtk.events_pending():
                gtk.main_iteration(False)
        self.art_db._commitGroups([group,])

    
    def one_key_reading(self,obj):
        #increment=80
        vadj=self.article_pane.text_scrolledwin.get_vadjustment()
        increment= vadj.page_increment * int(self.configs["scroll_fraction"]) / 100
        value= vadj.get_value()
        if value+increment+vadj.page_size<vadj.upper:
            vadj.set_value(value+increment)
        else:
            if vadj.upper-vadj.page_size==vadj.get_value():
                self.view_next_unread_article(None)
            else:
                vadj.set_value(vadj.upper-vadj.page_size)

    def one_key_move_up(self,obj):
        vadj=self.article_pane.text_scrolledwin.get_vadjustment()
        decrement= vadj.page_increment * int(self.configs["scroll_fraction"]) / 100
        value= vadj.get_value()
        if value-decrement>vadj.lower:
            vadj.set_value(value-decrement)
        else:
            vadj.set_value(vadj.lower)
        
    def expand_all_threads(self,obj,expand):
        if expand: self.threads_pane.threads_tree.expand_all()
        else: self.threads_pane.threads_tree.collapse_all()
        self.threads_pane.threads_tree.queue_draw()

    
    def expand_selected_row(self,obj,expand):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected:
            path=model.get_path(iter_selected)
            if expand: self.threads_pane.threads_tree.expand_row(path,True)
            else: self.threads_pane.threads_tree.collapse_row(path)
            self.threads_pane.threads_tree.queue_draw()



    def mark_group(self,obj,mark_read):
        "Mark selected groups read or unread"
        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_to_mark=model.get_value(iter_selected,0)
            self.art_db.markGroupRead(group_to_mark,mark_read)
        if path_list:
            self.show_subscribed()

    def mark_all_groups(self,obj,mark_read):
        "Mark all groups read or unread"
        subscribed=self.art_db.getSubscribed()
        for group in subscribed:
            group_to_mark=group[0]
            self.art_db.markGroupRead(group_to_mark,mark_read)
        self.show_subscribed()

    def keep_group(self,obj):
        "Set keep flag on the whole selected groups"
        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_to_mark=model.get_value(iter_selected,0)
            self.art_db.keepGroup(group_to_mark)
        self.show_subscribed()
 
    def rot13(self,text):
        "Rot13 the string passed"
        string_coded = ""
        dic={'a':'n','b':'o','c':'p','d':'q','e':'r','f':'s','g':'t',
             'h':'u','i':'v','j':'w','k':'x','l':'y','m':'z',
             'n':'a','o':'b','p':'c','q':'d','r':'e','s':'f','t':'g',
             'u':'h','v':'i','w':'j','x':'k','y':'l','z':'m',
             'A':'N','B':'O','C':'P','D':'Q','E':'R','F':'S','G':'T',
             'H':'U','I':'V','J':'W','K':'X','L':'Y','M':'Z',
             'N':'A','O':'B','P':'C','Q':'D','R':'E','S':'F','T':'G',
             'U':'H','V':'I','W':'J','X':'K','Y':'L','Z':'M'}
        for c in text:
            char=dic.get(c,c)
            string_coded=string_coded+char
        return string_coded

    def apply_rot13(self,obj):
        bounds=self.article_pane.buffer.get_selection_bounds()
        if bounds:
            #rot selected text
            start=bounds[0]
            stop=bounds[1]
            self.article_pane.buffer.create_mark("start_rot13",start,True)

            text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8")
            text_rotted=self.rot13(text)
            self.article_pane.buffer.delete_selection(False,False)
            self.article_pane.insert(text_rotted)

            start=self.article_pane.buffer.get_iter_at_mark(self.article_pane.buffer.get_mark("start_rot13"))
            self.article_pane.buffer.move_mark_by_name("insert",start)
        else:
            #rot the article
            bounds=self.article_pane.buffer.get_bounds()
            if bounds:
                start,stop=bounds
                text=self.article_pane.buffer.get_text(start,stop,True).decode("utf-8")
                text_rotted=self.rot13(text)
                self.show_article(text_rotted.split("\n"))


    def set_fixed_pitch(self,obj):
        monospace=pango.FontDescription("Monospace 9")
        user=pango.FontDescription(self.configs["font_name"])
        style=self.article_pane.textview.get_style().copy()
        if style.font_desc.get_family()!=monospace.get_family():
            self.article_pane.textview.modify_font(monospace)
        else:
            self.article_pane.textview.modify_font(user)


    def show_hide_headers(self,obj):
        self.article_pane.expander.set_expanded(not self.article_pane.expander.get_expanded())

    def export_newsrc(self,obj):
        def dispatch_response(dialog,id):
            if id==gtk.RESPONSE_OK:
                self.save_newsrc(None)
            if id==gtk.RESPONSE_CANCEL:
                self.file_dialog.destroy()
        self.file_dialog=gtk.FileChooserDialog(_("Select Newsrc Export Path"),None,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        self.file_dialog.set_local_only(True)
        #self.file_dialog.set_current_name("newsrc")
        self.file_dialog.connect("response",dispatch_response)
        path=self.file_dialog.get_current_folder()
        self.file_dialog.set_current_folder(path)
        self.file_dialog.show()

    def import_newsrc(self,obj):
        def dispatch_response(dialog,id):
            if id==gtk.RESPONSE_OK:
                self.load_newsrc(None)
            if id==gtk.RESPONSE_CANCEL:
                self.file_dialog.destroy()

        def show_hide_hidden(obj):
            self.file_dialog.set_property("show_hidden",obj.get_active())

        self.file_dialog=gtk.FileChooserDialog(_("Select Newsrc File"),None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        hidden_checkbutton=gtk.CheckButton(_("Show Hidden Files"))
        self.file_dialog.set_extra_widget(hidden_checkbutton)
        hidden_checkbutton.connect("clicked",show_hide_hidden)
        self.file_dialog.set_local_only(True)
        self.file_dialog.connect("response",dispatch_response)
        path=self.file_dialog.get_current_folder()
        self.file_dialog.set_current_folder(path)
        self.file_dialog.show()

    def save_newsrc(self,obj):
        path=self.file_dialog.get_filename()
        newsrc_file=ExportNewsrc(self.art_db)
        newsrc_file.save_newsrc(path)
        self.file_dialog.destroy()
        self.statusbar.push(1,newsrc_file.message)

    def load_newsrc(self,obj):
        path=self.file_dialog.get_filename()
        self.file_dialog.destroy()
        file_name=os.path.split(path)[1] 
        try:
            server_name=file_name[0:file_name.index(".newsrc")]        
        except:
            server_name=""
        
        d=Dialog_Import_Newsrc(_("""To correctly import a newsrc file you have to use the same server you used when you saved the file.\n
By default XPN uses a name like 'server_name.newsrc' so it is possible to know wich server was used\n
When you try to import a newsrc file XPN searches for the server name in the file name.\n\n
<b>Server To Use:</b>"""),server_name)
        if d.resp==gtk.RESPONSE_OK:
            server_name=d.server_name
            try:
                f=open(path,"rb")
            except IOError:
                self.statusbar.push(1,_("File does not exist"))
            else:
                newsrc_file=f.readlines()
                imp_newsrc=ImportNewsrc(newsrc_file,self,self.configs,server_name)
                self.show_subscribed()
                self.progressbar.set_fraction(0.0)
                self.progressbar.set_text("")
                self.statusbar.push(1,_("Newsrc successful imported"))

    def modify_keybord_shortcuts(self,obj):
        self.shortcuts_win=KeyBindings(self)

    def context_mark_read(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)
            self.remove_from_unreads(article)
            self.threads_pane.update_article_icon("read")
            self.threads_pane.set_is_unread(model,iter_selected,False)
            
            next_iter=self.threads_pane.find_next_row(model,iter_selected)
            if next_iter!=None and self.configs.get("advance_on_mark","False")=="True":
                old_path=model.get_path(iter_selected)
                if not self.threads_pane.threads_tree.row_expanded(old_path):
                    self.threads_pane.threads_tree.set_cursor(old_path,None,False)
                    self.threads_pane.threads_tree.expand_row(old_path,False)
                path=model.get_path(next_iter)
                self.threads_pane.threads_tree.expand_row(path,False)
                self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
                self.threads_pane.threads_tree.set_cursor(path,None,False)

    def context_mark_unread(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)            
            self.insert_in_unreads(article)
            self.threads_pane.set_is_unread(model,iter_selected,True)
            if article.body==None:
                self.threads_pane.update_article_icon("unread")
            else:
                self.threads_pane.update_article_icon("body")
            next_iter=self.threads_pane.find_next_row(model,iter_selected)
            if next_iter!=None and self.configs.get("advance_on_mark","False")=="True":
                old_path=model.get_path(iter_selected)
                if not self.threads_pane.threads_tree.row_expanded(old_path):
                    self.threads_pane.threads_tree.set_cursor(old_path,None,False)
                    self.threads_pane.threads_tree.expand_row(old_path,False)
                path=model.get_path(next_iter)
                self.threads_pane.threads_tree.expand_row(path,False)
                self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
                self.threads_pane.threads_tree.set_cursor(path,None,False)

    def context_keep(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)
            self.set_keep(article,self.group_to_thread)
            if article.keep:
                self.threads_pane.update_article_icon("keep")
            else:
                self.threads_pane.update_article_icon("unkeep")
            next_iter=self.threads_pane.find_next_row(model,iter_selected)
            if next_iter!=None and self.configs.get("advance_on_mark","False")=="True":
                old_path=model.get_path(iter_selected)
                if not self.threads_pane.threads_tree.row_expanded(old_path):
                    self.threads_pane.threads_tree.set_cursor(old_path,None,False)
                    self.threads_pane.threads_tree.expand_row(old_path,False)
                path=model.get_path(next_iter)
                self.threads_pane.threads_tree.expand_row(path,False)
                self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
                self.threads_pane.threads_tree.set_cursor(path,None,False)

    def context_delete(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)
            self.art_db.deleteArticle(self.group_to_thread,article)
            if model.iter_has_child(iter_selected):
                self.threads_pane.delete_row(model,iter_selected)
                self.show_threads(self.group_to_thread)
            else:
                self.threads_pane.delete_row(model,iter_selected)
            self.groups_pane.removed_article(article.is_read)

    def context_keep_sub(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            self.keep_subthread(model,iter_selected)

    def context_watch(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            self.set_watch(model,iter_selected)

    def context_ignore(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            self.set_ignore(model,iter_selected)

    def context_modify_score(self,obj,action):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)
            newsgroup=self.group_to_thread
            from_name=article.from_name
            self.score_win=Score_Win(self.score_rules,self)
            self.score_win.header_opt_menu.set_active(0)
            self.score_win.scope_combo.child.set_text("["+newsgroup+"]")
            self.score_win.match_type_opt_menu.set_active(0)
            self.score_win.match_value_entry.set_text(from_name.encode("utf-8"))
            self.score_win.case_checkbutton.set_active(True)
            self.score_win.score_mod_spinbutton.set_value(100)
            self.score_win.score_mod_opt_menu.set_active(action)
            self.score_win.show()
            self.score_win.notebook.set_current_page(1)

    def context_mark_download(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            article=self.threads_pane.get_article(model,iter_selected)
            if article.body==None:
                self.mark_for_download(article)
                if article.marked_for_download:
                    self.threads_pane.update_article_icon("download")
                elif article.body!=None:
                    self.threads_pane.update_article_icon("body")
                else:
                    self.threads_pane.update_article_icon("unread")
                next_iter=self.threads_pane.find_next_row(model,iter_selected)
                if next_iter!=None and self.configs.get("advance_on_mark","False")=="True":
                    old_path=model.get_path(iter_selected)
                    if not self.threads_pane.threads_tree.row_expanded(old_path):
                        self.threads_pane.threads_tree.set_cursor(old_path,None,False)
                        self.threads_pane.threads_tree.expand_row(old_path,False)
                    path=model.get_path(next_iter)
                    self.threads_pane.threads_tree.expand_row(path,False)
                    self.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
                    self.threads_pane.threads_tree.set_cursor(path,None,False)

    def context_mark_download_sub(self,obj):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            self.mark_subthread_for_download(model,iter_selected)
    
    def context_mark_read_sub(self,obj,read):
        treesel=self.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        if iter_selected!=None:
            self.mark_subthread_read(model,iter_selected,read)

    
    
    def context_mark_download_group(self,obj):
        model,path_list,iter_list=self.groups_pane.get_selected_rows()
        for path in path_list:
            iter_selected=model.get_iter(path)
            group_to_mark=model.get_value(iter_selected,0)
            self.mark_group_for_download(group_to_mark)

    def threads_context_menu(self,obj,event):
        if event.button==3:
            menu=self.ui.get_widget("/flags")
            menu.popup(None,None,None,event.button,event.time)
    
    def groups_context_menu(self,obj,event):
        if event.button==3:
            menu=self.ui.get_widget("/mark_group")
            menu.popup(None,None,None,event.button,event.time)

    def find_article(self,obj):
        self.find_win=Find_Win(self)
        self.find_win.show()

    def global_search(self,obj):
        self.GlobalSearch=GlobalSearch(self)
        self.GlobalSearch.show()

    def search_in_the_article(self,obj):
        self.search_win=Search_Win(self)
        self.search_win.show()

    def connect_signals(self):
        #menuitems signals

        #groups_pane signals
        self.groups_pane.groups_list.connect("button_release_event",self.groups_context_menu)
        self.groups_pane.groups_list.connect("row_activated",self.view_group,"doubleclick")
        self.groups_pane.groups_list.get_selection().connect("changed",self.view_group,"oneclick")

        #threads_pane signals
        self.threads_pane.threads_tree.connect("button_release_event",self.threads_context_menu)
        self.threads_pane.threads_tree.connect("row_activated",self.view_article,"doubleclick")
        self.threads_pane.threads_tree.get_selection().connect("changed",self.view_article, "oneclick")
        
        self.threads_pane.column2.connect("clicked",self.save_sorting_type)
        self.threads_pane.column3.connect("clicked",self.save_sorting_type)
        self.threads_pane.column4.connect("clicked",self.save_sorting_type)
        self.threads_pane.column5.connect("clicked",self.save_sorting_type)

        
        #article_pane_signals
        self.article_pane.vbox.connect("mid_clicked",self.mid_clicked)

    def mid_clicked(self,obj,mid):
        dia=MidDialog(mid)
        if dia.resp==gtk.RESPONSE_OK:
            mid=dia.entry.get_text()
            if dia.sel[0]:
                self.find_article(None)
                self.find_win.entry_msgid.set_text(mid)
                self.find_win.checkbutton_start.set_active(True)
            elif dia.sel[1]:
                self.global_search(None)
                self.GlobalSearch.entry_msgid.set_text(mid)
            else:
                if self.article_pane.use_custom_browser:
                    launcher=webbrowser.get("xpn_launcher")
                    launcher.open("http://groups.google.com/groups?selm="+url_quote(mid))
                else:
                    webbrowser.open("http://groups.google.com/groups?selm="+url_quote(mid))
                    
    def build_panes(self):
        self.groups_pane=Groups_Pane(_("Newsgroups"),_("UnRead"),True,self.configs)
        self.threads_pane=Threads_Pane(self.configs)
        if self.configs["show_headers"]=="True":
            show_headers=True
        else:
            show_headers=False
        self.article_pane=Article_Pane(show_headers,self.configs)

    def set_sizes(self):
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"rb")
        except IOError:
            vpaned_pos=120
            hpaned_pos=200
            groups_col1_width=145
            threads_col_subject_width=415
            threads_col_from_width=201
            threads_col_date_width=95
            self.window.maximize()
        else:
            sizes=cPickle.load(f)
            f.close()
            vpaned_pos=sizes.get("vpaned_pos",120)
            hpaned_pos=sizes.get("hpaned_pos",200)
            mainwin_width=sizes.get("mainwin_width",640)
            mainwin_height=sizes.get("mainwin_height",480)
            mainwin_pos_x=sizes.get("mainwin_pos_x",0)
            mainwin_pos_y=sizes.get("mainwin_pos_y",0)
            groups_col1_width=int(sizes.get("groups_col1",145))
            threads_col_subject_width=int(sizes.get("threads_col_subject",415))
            threads_col_from_width=int(sizes.get("threads_col_from",201))
            threads_col_date_width=int(sizes.get("threads_col_date",95))
            self.window.resize(int(mainwin_width),int(mainwin_height))
            self.window.move(int(mainwin_pos_x),int(mainwin_pos_y))
        self.hpaned.set_position(int(hpaned_pos))
        self.vpaned.set_position(int(vpaned_pos))
        self.groups_pane.column1.set_fixed_width(groups_col1_width)
        self.threads_pane.column2.set_fixed_width(threads_col_subject_width)
        self.threads_pane.column3.set_fixed_width(threads_col_from_width)
        self.threads_pane.column4.set_fixed_width(threads_col_date_width)

        

    def build_layout_type_1(self,layout_number,swap=False):
        if layout_number==1:
            self.pane_1=self.groups_pane
            self.pane_2=self.threads_pane
            self.pane_3=self.article_pane
        elif layout_number==2:
            self.pane_1=self.threads_pane
            self.pane_2=self.groups_pane
            self.pane_3=self.article_pane
        elif layout_number==3:
            self.pane_1=self.article_pane
            self.pane_2=self.groups_pane
            self.pane_3=self.threads_pane
        elif layout_number==4:
            self.pane_1=self.groups_pane
            self.pane_2=self.article_pane
            self.pane_3=self.threads_pane
        elif layout_number==5:
            self.pane_1=self.threads_pane
            self.pane_2=self.article_pane
            self.pane_3=self.groups_pane
        elif layout_number==6:
            self.pane_1=self.article_pane
            self.pane_2=self.threads_pane
            self.pane_3=self.groups_pane
            
        #Vpaned
        self.vpaned=gtk.VPaned()
        self.vbox1.pack_start(self.vpaned,True,True,0)
        self.vpaned.show()

        #HPaned
        self.hpaned=gtk.HPaned()
        self.hpaned.show()

        pane_1_parent,pane_2_parent,pane_3_parent=self.unlink_panes()
        
        #Groups Pane
        self.hpaned.add(self.pane_1.get_widget())
        self.pane_1.show()

        #Threads Pane
        self.hpaned.add(self.pane_2.get_widget())
        self.pane_2.show()

        #Article Pane
        
        if not swap:
            self.vpaned.add(self.hpaned)
            self.vpaned.add(self.pane_3.get_widget())
        else:
            self.vpaned.add(self.pane_3.get_widget())
            self.vpaned.add(self.hpaned)
            
        self.pane_3.show()

        if pane_3_parent!=None and pane_2_parent!=None and pane_1_parent!=None:
            pane_3_parent.get_parent().remove(pane_3_parent)
            if pane_1_parent!=pane_3_parent:
                pane_1_parent.get_parent().remove(pane_1_parent)
            if pane_2_parent!=pane_3_parent and pane_2_parent!=pane_1_parent:
                pane_2_parent.get_parent().remove(pane_2_parent)


    def build_layout_type_2(self,layout_number,swap=False):
        if layout_number==1:
            self.pane_1=self.groups_pane
            self.pane_2=self.threads_pane
            self.pane_3=self.article_pane
        elif layout_number==2:
            self.pane_1=self.groups_pane
            self.pane_2=self.article_pane
            self.pane_3=self.threads_pane
        elif layout_number==3:
            self.pane_1=self.article_pane
            self.pane_2=self.groups_pane
            self.pane_3=self.threads_pane
        elif layout_number==4:
            self.pane_1=self.article_pane
            self.pane_2=self.threads_pane
            self.pane_3=self.groups_pane
        elif layout_number==5:
            self.pane_1=self.threads_pane
            self.pane_2=self.article_pane
            self.pane_3=self.groups_pane
        elif layout_number==6:
            self.pane_1=self.threads_pane
            self.pane_2=self.groups_pane
            self.pane_3=self.article_pane

        #HPaned
        self.hpaned=gtk.HPaned()
        self.vbox1.pack_start(self.hpaned,True,True,0)
        self.hpaned.show()

        #Vpaned
        self.vpaned=gtk.VPaned()
        self.vpaned.show()

        pane_1_parent,pane_2_parent,pane_3_parent=self.unlink_panes()
        
        #Groups Pane
        self.vpaned.add(self.pane_1.get_widget())
        self.pane_1.show()


        #Threads Pane
        self.vpaned.add(self.pane_2.get_widget())
        self.pane_2.show()

        #Article Pane
        
        if not swap:
            self.hpaned.add(self.vpaned)
            self.hpaned.add(self.pane_3.get_widget())
        else:
            self.hpaned.add(self.pane_3.get_widget())
            self.hpaned.add(self.vpaned)
            
        self.pane_3.show()

        if pane_3_parent!=None and pane_2_parent!=None and pane_1_parent!=None:
            pane_3_parent.get_parent().remove(pane_3_parent)
            if pane_1_parent!=pane_3_parent:
                pane_1_parent.get_parent().remove(pane_1_parent)
            if pane_2_parent!=pane_3_parent and pane_2_parent!=pane_1_parent:
                pane_2_parent.get_parent().remove(pane_2_parent)
    
    def build_layout_type_3(self,layout_number):
        self.build_layout_type_2(layout_number,True)
    
    def build_layout_type_4(self,layout_number):
        self.build_layout_type_1(layout_number,True)


    def purge_groups(self):
        for group in self.art_db.purgeGroups():
            self.statusbar.push(1,_("Purging Group: %s") % (group,))
            while gtk.events_pending():
                gtk.main_iteration(False)
        self.art_db.closeGroups()
        self.art_db.closeSubscribed()


    def rebuild_layout(self):
        layout_methods = {"1":self.build_layout_type_1,
                          "2":self.build_layout_type_2,
                          "3":self.build_layout_type_3,
                          "4":self.build_layout_type_4
                         }
        r,c=divmod(int(self.configs["layout"])-1,6)
        layout_builder = layout_methods.get(str(r+1), None)
        if layout_builder: layout_builder(c+1)
        else: self.build_layout_type_1(1)
        self.set_sizes()

    def unlink_panes(self):
        pane_1_parent=self.pane_1.get_widget().get_parent()
        if pane_1_parent!=None:
            pane_1_parent.remove(self.pane_1.get_widget())
        pane_2_parent=self.pane_2.get_widget().get_parent()
        if pane_2_parent!=None:
            pane_2_parent.remove(self.pane_2.get_widget())
        pane_3_parent=self.pane_3.get_widget().get_parent()
        if pane_3_parent!=None:
            pane_3_parent.remove(self.pane_3.get_widget())
        return pane_1_parent,pane_2_parent,pane_3_parent
        
    def focus_pane(self,obj,pane):
        pane.grab_focus()
        
    def zoom_pane(self,pane,button):
        buttons=[self.zoom_groups_button,self.zoom_threads_button,self.zoom_article_button]
        status=button.get_active() #mantaining status
        buttons.remove(button)
        for other_button in buttons:
            other_button.set_active(False)
        button.set_active(status)

        if button.get_active()==True:
            parent1=pane.get_widget().get_parent()
            parent2=parent1.get_parent()
            parent3=parent2.get_parent()

        pane_1_parent,pane_2_parent,pane_3_parent=self.unlink_panes()
        if self.hpaned.get_parent()==self.vbox1:
            try:self.vbox1.remove(self.hpaned)
            except:pass
        if self.vpaned.get_parent()==self.vbox1:
            try:self.vbox1.remove(self.vpaned)
            except:pass

        
        if button.get_active()==True:
            self.vbox1.pack_start(pane.get_widget(),True,True,0)
            # if type(parent1)==type(gtk.VBox()):
                # self.vbox1.pack_start(pane.get_widget(),True,True,0)
            # if type(parent2)==type(gtk.VBox()):
                # parent2.remove(parent1)
                # self.vbox1.pack_start(pane.get_widget(),True,True,0)
            # if type(parent3)==type(gtk.VBox()):
                # parent3.remove(parent2)
                # self.vbox1.pack_start(pane.get_widget(),True,True,0)
        else:
            self.rebuild_layout()
    
    def zoom_article(self,obj):
        self.zoom_pane(self.article_pane,obj)

    def zoom_groups(self,obj):
        self.zoom_pane(self.groups_pane,obj)

    def zoom_threads(self,obj):
        self.zoom_pane(self.threads_pane,obj)
    
    def toggle_zoom_button(self,obj,button):
        button.set_active(not button.get_active())

    
    def load_languages(self):
        #loading translation
        if self.configs["lang"]=="it":
            it=gettext.translation("xpn","lang",["it"])
            it.install()
            try:
                #trying to force GTK translation
                locale.setlocale(locale.LC_MESSAGES,"it_IT")
            except: pass
        elif self.configs["lang"]=="fr":
            fr=gettext.translation("xpn","lang",["fr"])
            fr.install()
            try:
                #trying to force GTK translation
                locale.setlocale(locale.LC_MESSAGES,"fr_FR")
            except: pass
        elif self.configs["lang"]=="de":
            de=gettext.translation("xpn","lang",["de"])
            de.install()
            try:
                #trying to force GTK translation
                locale.setlocale(locale.LC_MESSAGES,"de_DE")
            except: pass
        else:
            try:
                #trying to force GTK translation
                locale.setlocale(locale.LC_MESSAGES,"en_US")
            except: pass
    
    def create_ui(self):

        #loading icons
        def _iconset (filename):
            return gtk.IconSet (gtk.gdk.pixbuf_new_from_file (os.path.join ("pixmaps", filename)))
        self.icons=gtk.IconFactory()
        for icon_name in os.listdir("pixmaps"):
            if "." in icon_name and not icon_name.endswith(".svg"):
                self.icons.add("xpn_"+icon_name.split(".")[0], _iconset (icon_name))
        self.icons.add_default()

        
        #try:
        #    self.ui.remove_action_group(self.actiongroup) 
        #    self.ui.remove_ui(self.merge_id)
        #    self.window.remove_accel_group(self.accel_group)
        #except:
        #    pass


        self.ui = gtk.UIManager()
        self.accelgroup = self.ui.get_accel_group()
        self.actiongroup= gtk.ActionGroup("MainWindowActions")

        self.window.add_accel_group(self.accelgroup)
        mscuts=load_shortcuts("main")
        self.actions=[("File",None,_("_File")),
                ("groups","xpn_groups",_("Groups List..."),mscuts["groups"],_("Manage Groups"),self.open_groups_win),
                ("rules","xpn_score",_("Scoring and Action Rules..."),mscuts["rules"],_("Edit Scoring and Action Rules"),self.open_rules_win),
                ("logs",None,_("Server Logs..."),mscuts["logs"],None,self.open_logs_win),                       
                ("exp_newsrc",None,_("Export Newsrc..."),mscuts["exp_newsrc"],None,self.export_newsrc),
                ("imp_newsrc",None,_("Import Newsrc..."),mscuts["imp_newsrc"],None,self.import_newsrc),
                ("accelerator",None,_("Modify Keyboard Shortcuts..."),mscuts["accelerator"],None,self.modify_keybord_shortcuts),
                ("conf","xpn_conf",_("Preferences..."),mscuts["conf"],_("Preferences"),self.open_configure_win),
                ("exit","xpn_exit",_("Exit"),mscuts["exit"],None,self.destroy),
                ("Search",None,_("_Search")),
                ("find","xpn_find",_("Find Article..."),mscuts["find"],None,self.find_article),
                ("global","xpn_global_search",_("Global Search ..."),mscuts["global"],None,self.global_search),
                ("filter",None,_("Filter Articles ..."),mscuts["filter"],None,self.filter_articles),
                ("search","xpn_search",_("Search in the Body..."),mscuts["search"],None,self.search_in_the_article),
                ("View",None,_("_View")),
                ("view_articles_opts",None,_("Articles View Options")),
                ("view_group_opts",None,_("Groups View Options")),
                ("Navigate",None,_("_Navigate")),
                ("group",None,_("View Next Group"),mscuts["group"],None,self.groups_pane.view_next_group),
                ("previous","xpn_previous",_("Read Previous Article"),mscuts["previous"],_("Read Previous Article"),self.view_previous_article),
                ("next","xpn_next",_("Read Next Article"),mscuts["next"],_("Read Next Article"),self.view_next_article),
                ("next_unread","xpn_next_unread",_("Read Next Unread Article"),mscuts["next_unread"],_("Read Next Unread Article"),self.view_next_unread_article),
                ("parent",None,_("Read Parent Article"),mscuts["parent"],None,self.view_parent_article),
                ("one_key",None,_("One-Key Reading"),mscuts["one_key"],None,self.one_key_reading),
                ("move_up",None,_("One-Key Scroll Up"),mscuts["move_up"],None,self.one_key_move_up),
                ("focus_article",None,_("Focus to Article Pane"),mscuts["focus_article"],None,self.focus_pane,self.article_pane.textview),
                ("focus_groups",None,_("Focus to Groups Pane"),mscuts["focus_groups"],None,self.focus_pane,self.groups_pane.groups_list),
                ("focus_threads",None,_("Focus to Threads Pane"),mscuts["focus_threads"],None,self.focus_pane,self.threads_pane.threads_tree),
                ("zoom_article",None,_("Zoom Article Pane"),mscuts["zoom_article"],None,self.toggle_zoom_button,self.zoom_article_button),
                ("zoom_groups",None,_("Zoom Groups Pane"),mscuts["zoom_groups"],None,self.toggle_zoom_button,self.zoom_groups_button),
                ("zoom_threads",None,_("Zoom Threads Pane"),mscuts["zoom_threads"],None,self.toggle_zoom_button,self.zoom_threads_button),
                ("Subscribed",None,_("Subscribed _Groups")),
                ("gethdrs","xpn_receive_headers",_("Get New Headers in Subscribed Groups"),mscuts["gethdrs"],_("Get New Headers in Subscribed Groups"),self.get_new_headers),
                ("gethdrssel","xpn_receive_headers_selected",_("Get New Headers in Selected Groups"),mscuts["gethdrssel"],None,self.get_new_headers_selected),
                ("getbodies","xpn_receive_bodies",_("Get Marked Article Bodies in Subscribed Groups"),mscuts["getbodies"],_("Get Marked Article Bodies in Subscribed Groups"),self.get_bodies),
                ("getbodiessel","xpn_receive_bodies_selected",_("Get Marked Article Bodies in Selected Groups"),mscuts["getbodiessel"],None,self.get_bodies_selected),
                ("expand","xpn_expand_all",_("Expand All Threads"),mscuts["expand"],_("Expand All"),self.expand_all_threads,True),
                ("collapse","xpn_collapse_all",_("Collapse All Threads"),mscuts["collapse"],_("Collapse All"),self.expand_all_threads,False),
                ("expand_row","xpn_expand",_("Expand Selected SubThread"),mscuts["expand_row"],_("Expand Selected SubThread"),self.expand_selected_row,True),
                ("collapse_row","xpn_collapse",_("Collapse Selected SubThread"),mscuts["collapse_row"],_("Collapse Selected SubThread"),self.expand_selected_row,False),
                ("mark_group",None,_("Mark Group ...")),
                ("mark","xpn_mark",_("Mark Selected Groups as Read"),mscuts["mark"],_("Mark Selected Groups as Read"),self.mark_group,True),
                ("mark_unread_group",None,_("Mark Selected Groups as Unread"),mscuts["mark_unread_group"],None,self.mark_group,False),
                ("mark_download_group","xpn_mark_multiple",_("Mark Group for Retrieving"),mscuts["mark_download_group"],None,self.context_mark_download_group),
                ("keepall","xpn_art_keep",_("Keep Articles in Selected Groups"),mscuts["keepall"],None,self.keep_group),
                ("markall","xpn_mark_all",_("Mark All Groups as Read"),mscuts["markall"],_("Mark All Groups as Read"),self.mark_all_groups,True),
                ("markall_unread",None,_("Mark All Groups as Unread"),mscuts["markall_unread"],None,self.mark_all_groups,False),
                ("apply_score",None,_("Apply Scoring and Action Rules"),mscuts["apply_score"],None,self.reapply_score_actions_rules),
                ("groups_vs_id",None,_("Assign Identities to Groups"),mscuts["groups_vs_id"],None,self.open_groups_vs_id),
                ("Articles",None,_("_Articles")),
                ("show_hide_headers",None,_("Show/Hide Headers"),mscuts["show_hide_headers"],None,self.show_hide_headers),
                ("rot13","xpn_rot13",_("ROT13 Selected Text"),mscuts["rot13"],_("ROT13 Selected Text"),self.apply_rot13),
                ("flags",None,_("Flags & Score")),
                ("mark_read","xpn_art_read",_("Mark Article as Read"),mscuts["mark_read"],None,self.context_mark_read),
                ("mark_unread","xpn_art_unread",_("Mark Article as UnRead"),mscuts["mark_unread"],None,self.context_mark_unread),
                ("mark_download","xpn_art_mark",_("Mark Article for Retrieving"),mscuts["mark_download"],None,self.context_mark_download),
                ("keep","xpn_art_keep",_("Keep Article"),mscuts["keep"],None,self.context_keep),
                ("delete","xpn_art_delete",_("Delete Article"),mscuts["delete"],None,self.context_delete),
                ("mark_unread_sub",None,_("Mark SubThread as UnRead"),mscuts["mark_unread_sub"],None,self.context_mark_read_sub,False),
                ("mark_read_sub","xpn_art_read",_("Mark SubThread as Read"),mscuts["mark_read_sub"],None,self.context_mark_read_sub,True),
                ("mark_download_sub","xpn_mark_multiple",_("Mark SubThread for Retrieving"),mscuts["mark_download_sub"],None,self.context_mark_download_sub),
                ("keep_sub","xpn_art_keep",_("Keep SubThread"),mscuts["keep_sub"],None,self.context_keep_sub),
                ("watch","xpn_art_watch",_("Watch SubThread"),mscuts["watch"],None,self.context_watch),
                ("ignore","xpn_art_ignore",_("Ignore SubThread"),mscuts["ignore"],None,self.context_ignore),
                ("raise_score","xpn_raise_score",_("Raise Author Score"),mscuts["raise_score"],None,self.context_modify_score,0),
                ("lower_score","xpn_lower_score",_("Lower Author Score"),mscuts["lower_score"],None,self.context_modify_score,1),
                ("set_score","xpn_set_score",_("Set Author Score"),mscuts["set_score"],None,self.context_modify_score,2),
                ("post","xpn_post",_("Post New Article..."),mscuts["post"],_("Post New Article"),self.open_edit_win),
                ("outbox_manager","xpn_outbox",_("Open Outbox Manager"),mscuts["outbox_manager"],_("Open Outbox Manager"),self.open_outbox_manager),
                ("followup","xpn_followup",_("Follow-Up To Newsgroup..."),mscuts["followup"],_("Follow-Up To Newsgroup"),self.open_edit_win,True),
                ("reply","xpn_reply",_("Reply By Mail..."),mscuts["reply"],_("Reply by Mail"),self.open_edit_mail_win),
                ("supersede","xpn_supersede",_("Supersede Article..."),mscuts["supersede"],None,self.supersede_cancel_message,"Supersede"),
                ("cancel","xpn_cancel",_("Cancel Article..."),mscuts["cancel"],None,self.supersede_cancel_message,"Cancel"),
                ("Help",None,_("Help")),
                ("about","xpn_about",_("About..."),mscuts["about"],None,self.open_about_dialog)]
                
        for action in self.actions:
            if len(action)<7:
                self.actiongroup.add_actions([action])
            else:
                self.actiongroup.add_actions([action[0:6]],action[-1])

        self.toggle_actions=[
                ("show_threads",None,_("Show Threads"),mscuts["show_threads"],None,self.view_group,False,None,None),
                ("show_all_read_threads",None,_("Show All Read Threads"),mscuts["show_all_read_threads"],None,self.view_group,False,None,None),
                ("show_threads_without_watched",None,_("Show Threads Without Watched Articles"),mscuts["show_threads_without_watched"],None,self.view_group,False,None,None),
                ("show_read_articles",None,_("Show Read Articles"),mscuts["show_read_articles"],None,self.view_group,False,None,None),
                ("show_unread_articles",None,_("Show UnRead Articles"),mscuts["show_unread_articles"],None,self.view_group,False,None,None),
                ("show_kept_articles",None,_("Show Kept Articles"),mscuts["show_kept_articles"],None,self.view_group,False,None,None),
                ("show_unkept_articles",None,_("Show UnKept Articles"),mscuts["show_unkept_articles"],None,self.view_group,False,None,None),
                ("show_watched_articles",None,_("Show Watched Articles"),mscuts["show_watched_articles"],None,self.view_group,False,None,None),
                ("show_ignored_articles",None,_("Show Ignored Articles"),mscuts["show_ignored_articles"],None,self.view_group,False,None,None),
                ("show_unwatchedignored_articles",None,_("Show UnWatched/UnIgnored Articles"),mscuts["show_unwatchedignored_articles"],None,self.view_group,False,None,None),
                ("show_score_neg_articles",None,_("Show Articles with Score<0"),mscuts["show_score_neg_articles"],None,self.view_group,False,None,None),
                ("show_score_zero_articles",None,_("Show Articles with Score=0"),mscuts["show_score_zero_articles"],None,self.view_group,False,None,None),
                ("show_score_pos_articles",None,_("Show Articles with Score>0"),mscuts["show_score_pos_articles"],None,self.view_group,False,None,None),
                ("raw",None,_("View Raw Article"),mscuts["raw"],None,self.view_article,False),
                ("spoiler",None,_("Show Spoilered Text"),mscuts["spoiler"],None,self.view_article,False),
                ("show_quote",None,_("Show Quoted Text"),mscuts["show_quote"],None,self.view_article,False),
                ("show_sign",None,_("Show Signatures"),mscuts["show_sign"],None,self.view_article,False),
                ("fixed",None,_("Fixed Pitch Font"),mscuts["fixed"],None,self.set_fixed_pitch,False)]


        for action in self.toggle_actions: 
            if len(action)<8:
                self.actiongroup.add_toggle_actions([action])
            else:
                self.actiongroup.add_toggle_actions([action[0:7]],action[7:])

        self.ui.insert_action_group(self.actiongroup,0)
        self.merge_id = self.ui.add_ui_from_string(ui_string)
        self.ui.ensure_update()  
                
    def toolbar_search(self,obj,search_type,text):
        self.show_threads(self.group_to_thread,search_type,text)
        

    def search_focus_changed(self,obj,event,focusIn):
        if focusIn:
            #we have to disable accelerator
            self.window.remove_accel_group(self.accelgroup)
        else:
            self.window.add_accel_group(self.accelgroup)
    
    def close_filter_toolbar(self,obj):
        self.filter_toolbar.hide()
    
    def filter_articles(self,obj):
        self.filter_toolbar.show_all()
        self.cs_entry.grab_focus()
    
    def recoverPreviousInstall(self):
        '''Recover files from 1.0 installation'''

        #Looking for groups.dat files
        file_list=os.listdir(os.path.join(self.wdir,"groups_info"))
        groups_list_db=Groups_DB()
        for file_name in file_list:
            if file_name.endswith("groups.dat"):
                print "Recovering", file_name
                f=open(os.path.join(self.wdir,"groups_info",file_name))
                try: list_to_recover=cPickle.load(f)
                except: list_to_recover=[]
                f.close()
                groups_list_db.createList(list_to_recover,"",file_name.replace(".dat",".sqlitedb"))
                os.remove(os.path.join(self.wdir,"groups_info",file_name))

        #Looking for subscribed.dat files
        if "subscribed.dat" in file_list:
            print "Recovering subscribed.dat"
            f=open(os.path.join(self.wdir,"groups_info","subscribed.dat"))
            try:subscribed=cPickle.load(f)
            except:subscribed=[]
            f.close()
            
            for group in subscribed:
                self.art_db.addSubscribed(group[0],group[1],group[2],group[3])
            os.remove(os.path.join(self.wdir,"groups_info","subscribed.dat"))

            for group in subscribed:
                print "Recovering Group:", group
                import shelve
                try:art=shelve.open(os.path.join(self.wdir,"groups_info",group[0],group[0]))
                except:art=[]
                articles=dict(art)
                try:art.close()
                except:pass
                shutil.rmtree(os.path.join(self.wdir,"groups_info",group[0]))
                self.art_db.createGroup(group[0])
                for article in articles.itervalues():
                    if article.body: #This is needed for the recoverPreviousInstall function
                        article.raw_body=article.get_raw()
                        article.has_body=True
                        self.art_db._insertBody(group[0],article,False)
                    else:
                        article.raw_body=""
                        article.has_body=False
                    self.art_db.insertArticle(group[0],article)



    def __init__(self,use_home,custom_dir):
        Edit_Win.VERSION=VERSION
        Edit_Mail_Win.VERSION=VERSION
        if use_home:           
            userdir=UserDir(userHome=True)
        elif custom_dir:
            userdir=UserDir(customPath=custom_dir)
        else:
            userdir=UserDir(cwd=True)
        ret=userdir.Create()
        if ret>0 :sys.exit(ret)
        self.wdir=userdir.dir
        
        self.conf=Config_File()
        self.configs=self.conf.get_configs()


        
        self.load_languages()
        
        try: open(os.path.join(self.wdir,"xpn.lock"),"r")
        except IOError:open(os.path.join(self.wdir,"xpn.lock"),"w")
        else: 
            #raise StandardError, "An istance of XPN is already running, if you think this is an error remove manually the file 'xpn.lock' in your XPN working directory."
            md=Dialog_YES_NO(_("An instance of XPN is already running.\n\nDo you want to open XPN anyway?"))
            if not md.resp:
                sys.exit()
        
        try: os.remove(os.path.join(self.wdir,"server_logs.dat"))
        except: pass

        try: os.remove(os.path.join(self.wdir,"error_logs.dat"))
        except: pass

        try: map(shutil.rmtree,glob.glob(os.path.join(self.wdir,"groups_info/global.search.results.*")))
        except: pass

        try: os.makedirs(os.path.join(self.wdir,"groups_info"))
        except: pass
        
        try: os.makedirs(os.path.join(self.wdir,"dats"))
        except: pass

        try: os.makedirs(os.path.join(self.wdir,"outbox/news"))
        except: pass
        try: os.makedirs(os.path.join(self.wdir,"outbox/mail"))
        except: pass

        try: os.makedirs(os.path.join(self.wdir,"draft/news"))
        except: pass
        try: os.makedirs(os.path.join(self.wdir,"draft/mail"))
        except: pass
        
        try: os.makedirs(os.path.join(self.wdir,"sent/news"))
        except: pass
        try: os.makedirs(os.path.join(self.wdir,"sent/mail"))
        except: pass
        
        self.s=None

        
        self.groups_lock=False
        self.group_to_thread=""
        self.current_server=""
        self.subscribed_groups=[]
        
        self.art_db=Articles_DB()

        self.recoverPreviousInstall()

        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.connectionsPool=dict()
        for server in cp.sections():
            if cp.get(server,"nntp_use_ssl")=="True":
                self.connectionsPool[server]=SSLConnection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
            else:
                self.connectionsPool[server]=Connection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))


        #loading score rules
        self.score_rules=Score_Rules()

        #MainMenuBar
        self.window=gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title("XPN "+NUMBER)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/xpn-icon.png"))
        self.window.set_size_request(300,200)

        self.build_panes()        

        self.zoom_article_button=gtk.ToggleButton("A")
        self.zoom_threads_button=gtk.ToggleButton("H")
        self.zoom_groups_button=gtk.ToggleButton("G")
        
        #UIManager
        self.create_ui()


        #Filter Toolbar
        se_toolitem=gtk.ToolItem()
        self.cs_entry=Custom_Search_Entry()
        self.cs_entry.connect("do_search",self.toolbar_search)
        self.cs_entry.connect("search_focus_in",self.search_focus_changed,True)
        self.cs_entry.connect("search_focus_out",self.search_focus_changed,False)
        se_toolitem.add(self.cs_entry)
        se_toolitem.show_all()
        label_toolitem=gtk.ToolItem()
        label=gtk.Label(_("Filter Articles by: "))
        label_toolitem.add(label)
        label_toolitem.show_all()
        close_tool_button=gtk.ToolButton(gtk.STOCK_CLOSE)
        try: close_tool_button.set_tooltip_text(_("Close Filter Toolbar"))
        except: pass #doesn't work with some old GTK 
        close_tool_button.connect("clicked",self.close_filter_toolbar)
        close_tool_button.show_all()
        
        self.filter_toolbar=gtk.Toolbar()
        self.filter_toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.filter_toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.filter_toolbar.set_style(gtk.SHADOW_NONE)
        self.filter_toolbar.insert(label_toolitem,-1)
        self.filter_toolbar.insert(se_toolitem,-1)
        self.filter_toolbar.insert(close_tool_button,-1)
        
        


        menubar=self.ui.get_widget("/MainMenuBar")
        toolbar=self.ui.get_widget("/MainToolBar")
        #toolbar.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_style(gtk.SHADOW_NONE)

        #main vbox
        self.vbox1 = gtk.VBox(False,0)
        self.window.add(self.vbox1)
        self.vbox1.show()

        self.vbox1.pack_start(menubar,False,True,0)
        menubar.show()        

        #Handlebox
        self.vbox1.pack_start(toolbar,False,False,0)
        toolbar.show()
        
        self.vbox1.pack_start(self.filter_toolbar,False,False,0)
        

        layout_methods = {"1":self.build_layout_type_1,
                          "2":self.build_layout_type_2,
                          "3":self.build_layout_type_3,
                          "4":self.build_layout_type_4
                         }
        r,c=divmod(int(self.configs["layout"])-1,6)
        layout_builder = layout_methods.get(str(r+1), None)
        if layout_builder: layout_builder(c+1)
        else: self.build_layout_type_1(1)   # If there is no layout associated to
                                            # self.configs["layout"] then build 1


        #hbox_bottom
        hbox_bottom=gtk.HBox()
        self.vbox1.pack_end(hbox_bottom,False,False,0)
        hbox_bottom.show()

        #progressbar
        self.progressbar=gtk.ProgressBar()
        hbox_bottom.pack_start(self.progressbar,False,False,0)
        self.progressbar.show()

        #Zoom Buttons
        self.zoom_article_button.set_relief(gtk.RELIEF_NONE)
        self.zoom_threads_button.set_relief(gtk.RELIEF_NONE)
        self.zoom_groups_button.set_relief(gtk.RELIEF_NONE)
        self.zoom_article_button.connect("clicked",self.zoom_article)
        self.zoom_threads_button.connect("clicked",self.zoom_threads)
        self.zoom_groups_button.connect("clicked",self.zoom_groups)
        zoom_article_tip=gtk.Tooltips()
        zoom_threads_tip=gtk.Tooltips()
        zoom_groups_tip=gtk.Tooltips()
        zoom_article_tip.set_tip(self.zoom_article_button,_("Zoom Article Pane"))
        zoom_threads_tip.set_tip(self.zoom_threads_button,_("Zoom Headers Pane"))
        zoom_groups_tip.set_tip(self.zoom_groups_button,_("Zoom Groups Pane"))
        hbox_bottom.pack_start(self.zoom_article_button,False,False,0)
        hbox_bottom.pack_start(self.zoom_threads_button,False,False,0)
        hbox_bottom.pack_start(self.zoom_groups_button,False,False,0)
        self.zoom_article_button.show()
        self.zoom_threads_button.show()
        self.zoom_groups_button.show()

        separator=gtk.VSeparator()
        separator.show()
        hbox_bottom.pack_start(separator,False,False,0)


        #statusbar
        self.statusbar=gtk.Statusbar()
        hbox_bottom.pack_start(self.statusbar,True,True,0)
        self.statusbar.show()


        

        self.connect_signals()

        self.show_subscribed()

        self.update_checkmenu_options()

        monospace=pango.FontDescription("Monospace 9")
        if self.configs["use_system_fonts"]=="True":
            user=pango.FontDescription("")
        else:
            user=pango.FontDescription(self.configs["font_name"])
        if self.configs["fixed"]=="True":
            self.article_pane.textview.modify_font(monospace)
        else:
            self.article_pane.textview.modify_font(user)
        self.article_pane.textview.set_indent(5)
        self.set_sizes()
        self.mainwin_width=None  #I must use these because if I close the window with the [x]
        self.mainwin_height=None #I loose window sizes
        self.mainwin_pos_x=None
        self.mainwin_pos_y=None
        
        self.window.show()
        
        if not self.conf.found_config_file:
            dia=Dialog_YES_NO(_("Missing Config File.\n\nDo you want to Configure XPN now?"))
            if dia.resp:
                self.open_configure_win(None)        
        self.msgids=dict()
        timeout=int(self.configs.get("download_timeout",'30'))
        do_auto_download=eval(self.configs.get("automatic_download","False"))
        if do_auto_download: gobject.timeout_add(timeout*1000*60,self.get_new_headers,None)

def hook(et,ev,eb):
    import traceback
    ex_list=traceback.format_exception(et,ev,eb)
    list="".join(ex_list)
    if not ("sys.exit()" in list or "systemexit" in list.lower()):
        message="\n"+"".join(ex_list)
        log=message
        try:
            f=open(os.path.join(wdir,"error_logs.dat"),"a")
        except IOError:
            pass
        else:
            f.write(":::: "+time.ctime(time.time())+" :::: \n"+message+"\n\n")
            f.close()
        try:
            f=open(os.path.join(wdir,"error_logs.dat"),"rb")
        except IOError:
            pass
        else:
            log=f.read()
        try:
            error_dialog=Error_Dialog(unicode(message,"us-ascii","replace").encode("utf-8"),unicode(log,"us-ascii","replace").encode("utf-8"))
            error_dialog.run()
        except:
            sys.stderr.write(_('Unexpected error in the excepthook.'))
            sys.stderr.write('\n\n')
            message = message="\n"+"".join(traceback.format_exception(*sys.exc_info()))
            sys.stderr.write(message)
        else:
            error_dialog.destroy() 


parser=OptionParser(usage=_("python %prog [-d] [-cCUSTOM_DIR]\n\nWith command line options you can decide where XPN will save config files and articles.\nIf you don't use any option, the current working directory will be used.\nIf you use the '--home_dir' option, XPN will create a .xpn directory inside your home directory, and will store informations inside that directory.\nIf you use the '--custom_dir' option, XPN will create a .xpn directory inside that custom_directory.\n\nNOTE: If you set the '--home_dir' option, XPN will ignore the '--custom_dir' option (if you used it).\n\nExamples:\npython xpn.py\npython xpn.py -d\npython xpn.py --custom_dir /home/user/custom"))
parser.add_option("-d","--home_dir",action="store_true",dest="use_home",default=False,
                  help=_("use home directory to store config files and articles"))
parser.add_option("-c","--custom_dir",dest="custom_dir",
                  help=_("specify an existing directory where store config files and articles"))
options,args=parser.parse_args()

try: dir=os.path.dirname(sys.argv[0])
except: dir=""
if dir:
    try:os.chdir(dir)
    except: pass

try:
    main=MainWin(options.use_home,options.custom_dir)
    wdir=main.wdir
except:
    def eHook():
        hook(*sys.exc_info())
        gtk.main_quit()
    wdir=''
    gobject.timeout_add(100,eHook)
    gtk.main()

else:
    #reload(sys)
    #sys.setdefaultencoding("ascii")
    sys.excepthook=hook
    gtk.main()
