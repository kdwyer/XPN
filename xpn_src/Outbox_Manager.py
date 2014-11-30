import gtk
import gobject
import os
import cPickle
import ConfigParser
from email.Utils import parsedate,parsedate_tz,mktime_tz
from time import ctime
from xpn_src.UserDir import get_wdir
from xpn_src.Edit_Win import Edit_Win
from xpn_src.Edit_Mail_Win import Edit_Mail_Win
from xpn_src.Charset_List import load_ordered_list
from xpn_src.Article import Article_To_Send,Mail_To_Send
from xpn_src.Connections_Handler import Connection,SMTPConnection, SSLConnection
from xpn_src.KeyBindings import load_shortcuts

ui_string="""<ui>
    <menubar name='OutboxMenuBar'>
        <menu action="Outbox">
            <menuitem action='send_article' />
            <menuitem action='send_mail' />
            <separator />
            <menuitem action='edit' />
            <menuitem action='delete' />
            <separator />            
            <menuitem action='exit' />
        </menu>
    </menubar>


    <toolbar name='OutboxToolBar'>
            <toolitem action='send_article' />
            <toolitem action='send_mail' />
            <separator />
            <toolitem action='edit' />
            <toolitem action='delete' />
            <separator />            
            <toolitem action='exit' />
    </toolbar>
</ui>"""

class Outbox_Manager:

    def show(self):
        self.win.show_all()
        
    def delete_event(self,widget,event,data=None):
        self.outboxwin_width,self.outboxwin_height=self.win.get_size()
        self.save_sizes()
        return False

    def destroy(self,obj):
        self.save_sizes()
        self.win.destroy()
    
    def populateFolderTree(self):
        """Builds the Folder Tree content"""
        folder_icon=gtk.gdk.pixbuf_new_from_file("pixmaps/folder.xpm")
        folder_open_icon=gtk.gdk.pixbuf_new_from_file("pixmaps/folder_open.xpm")
        model,iter_selected=self.folderTree.get_selection().get_selected()
        if iter_selected: path=model.get_path(iter_selected)
        else: path=None
        model=self.folderTree.get_model()
        model.clear()
        iterOutbox=model.insert_before(None,None)
        model.set_value(iterOutbox,0,_("OutBox"))
        model.set_value(iterOutbox,2,folder_open_icon)
        iterOutboxArticle=model.insert_before(iterOutbox,None)
        model.set_value(iterOutboxArticle,0,_("OutGoing Articles"))
        model.set_value(iterOutboxArticle,2,folder_icon)
        iterOutboxMail=model.insert_before(iterOutbox,None)
        model.set_value(iterOutboxMail,0,_("OutGoing Mails"))
        model.set_value(iterOutboxMail,2,folder_icon)
        
        iterDraft=model.insert_before(None,None)
        model.set_value(iterDraft,0,_("Drafts"))
        model.set_value(iterDraft,2,folder_open_icon)
        iterDraftArticle=model.insert_before(iterDraft,None)
        model.set_value(iterDraftArticle,0,_("Draft Articles"))
        model.set_value(iterDraftArticle,2,folder_icon)
        iterDraftMail=model.insert_before(iterDraft,None)
        model.set_value(iterDraftMail,0,_("Draft Mails"))
        model.set_value(iterDraftMail,2,folder_icon)

        iterSent=model.insert_before(None,None)
        model.set_value(iterSent,0,_("Sent"))
        model.set_value(iterSent,2,folder_open_icon)
        iterSentArticle=model.insert_before(iterSent,None)
        model.set_value(iterSentArticle,0,_("Sent Articles"))
        model.set_value(iterSentArticle,2,folder_icon)
        iterSentMail=model.insert_before(iterSent,None)
        model.set_value(iterSentMail,0,_("Sent Mails"))
        model.set_value(iterSentMail,2,folder_icon)

        self.folderTree.expand_all()

        try:
            articles=os.listdir(os.path.join(self.wdir,"outbox/news"))
        except:
            self.statusbar.push(1,_("Problems while opening News OutBox"))
        else:
            total=len(articles)
            model.set_value(iterOutboxArticle,1,total)
       
        try:
            articles=os.listdir(os.path.join(self.wdir,"outbox/mail"))
        except:
            self.statusbar.push(1,_("Problems while opening Mail OutBox"))
        else:
            total=len(articles)
            model.set_value(iterOutboxMail,1,total)

        try:
            articles=os.listdir(os.path.join(self.wdir,"draft/news"))
        except:
            self.statusbar.push(1,_("Problems while opening News Drafts"))
        else:
            total=len(articles)
            model.set_value(iterDraftArticle,1,total)
       
        try:
            articles=os.listdir(os.path.join(self.wdir,"draft/mail"))
        except:
            self.statusbar.push(1,_("Problems while opening Mail Drafts"))
        else:
            total=len(articles)
            model.set_value(iterDraftMail,1,total) 

        try:
            articles=os.listdir(os.path.join(self.wdir,"sent/news"))
        except:
            self.statusbar.push(1,_("Problems while opening Sent Articles"))
        else:
            total=len(articles)
            model.set_value(iterSentArticle,1,total)
       
        try:
            articles=os.listdir(os.path.join(self.wdir,"sent/mail"))
        except:
            self.statusbar.push(1,_("Problems while opening Sent Mails"))
        else:
            total=len(articles)
            model.set_value(iterSentMail,1,total) 


        if path:
            column=self.folderTree.get_column(0)
            self.folderTree.set_cursor(path,None,False)
            self.folderTree.row_activated(path,column)

            

 
    def openFolder(self,*params):
        """Opens the selected folder and loads the articles/mails inside it"""
        model,iter_selected=self.folderTree.get_selection().get_selected()
        if iter_selected: path=model.get_path(iter_selected)
        else: path=[]
        if len(path)>1: 
            folderName=""
            isMail=False
            if path[0]==0: folderName="outbox/"
            elif path[0]==1: folderName="draft/"
            else : folderName="sent/"
            if path[1]==0: folderName+="news"
            else: folderName+="mail"
            isMail="mail" in folderName
            try:
                articles=os.listdir(os.path.join(self.wdir,folderName))
            except:
                self.statusbar.push(1,_("Problems while opening folder :")+folderName)
            else:
                model=self.previewTree.get_model()
                model.clear()

                for articleName in articles:
                    try:
                        pathToArticle=os.path.join(self.wdir,folderName,articleName)
                        f=open(pathToArticle,"rb")
                    except:
                        self.statusbar.push(1,_("Problems while opening article :")+articleName)
                    else:
                        article=cPickle.load(f)
                        f.close()
                        self.previewArticle(article,isMail,os.path.join(folderName,articleName))
        else:
            self.previewTree.get_model().clear()
    
    def parse_date(self,date):
        #data=parsedate(date)
        try: #trying to prevent the rfc822.parsedate bug with Tue,26 instead of Tue, 26
            secs=mktime_tz(parsedate_tz(date))
        except:
            secs=time()
        data=parsedate(ctime(secs))
        if data[3]<10:
            ora="0"+repr(data[3])
        else:
            ora=repr(data[3])
        if data[4]<10:
            minuti="0"+repr(data[4])
        else:
            minuti=repr(data[4])
        return repr(data[2])+"/"+repr(data[1])+"/"+repr(data[0])+" "+ora+":"+minuti,secs
 
    def previewArticle(self,article,isMail,relativePathToArticle):
        """Shows a summary of the article/mail"""
        model=self.previewTree.get_model()
        iter_new=model.insert_before(None,None)
        subj=article.get("subject","")
        if isMail: to=article.get("to_name","")
        else: to=article.get("newsgroups","")
        date=article.get("date","")
        date_parsed,secs=self.parse_date(date)
        model.set_value(iter_new,0,subj.encode("utf-8"))
        model.set_value(iter_new,1,to.encode("utf-8"))
        model.set_value(iter_new,2,date_parsed)
        model.set_value(iter_new,3,article)
        model.set_value(iter_new,4,isMail)
        model.set_value(iter_new,5,relativePathToArticle)
        model.set_value(iter_new,6,secs)
        
    def openArticle(self,*params):
        """Opens the article/mail in the edit window"""
        model,iterSelected=self.previewTree.get_selection().get_selected()
        if iterSelected:
            article=model.get_value(iterSelected,3)
            isMail=model.get_value(iterSelected,4)
            rPath=model.get_value(iterSelected,5)
            isSent=rPath.startswith("sent")
            server_name=article.get("server_name","")            
            if isMail:
                editWin=Edit_Mail_Win(self.configs,article.get("to_name",""),None,None,"Draft",article,rPath,self,isSent,id_name=article.get("id_name",""))
            else:
                editWin=Edit_Win(self.configs,article.get("newsgroups",""),None,None,self.subscribedGroups,"Draft",article,rPath,self,isSent,server_name,id_name=article.get("id_name",""))

            editWin.show()
    
    def deleteArticle(self,*params):
        """Deletes the article/mail selected"""
        model,iterSelected=self.previewTree.get_selection().get_selected()
        if iterSelected:
            article=model.get_value(iterSelected,3)
            isMail=model.get_value(iterSelected,4)
            rPath=model.get_value(iterSelected,5)
            try: os.remove(os.path.join(self.wdir,rPath))
            except: self.statusbar.push(1,_("Problems while deleting the article: %s" % (os.path.join(self.wdir,rPath))))
            else: self.statusbar.push(1,_("Article Deleted"))
            self.populateFolderTree()


    def store_article(self,dirName,article_backup):
        try:
            out_files=os.listdir(dirName)
        except:
            self.statusbar.push(1,_("Problems while opening : ")+dirName)
        else:
            num=len(out_files)
            numbers=map(int,out_files)
            if not numbers:numbers=[-1]
            number=max((max(numbers),num))
            f=open(os.path.join(dirName,str(number+1)),"wb")
            cPickle.dump(article_backup,f,1)
            f.close()


    def sendQueuedArticles(self,obj):
        '''Send articles stored in outbox'''
        ordered_list=load_ordered_list()
        user_agent=self.VERSION
        try:
            articles=os.listdir(os.path.join(self.wdir,"outbox/news"))
        except:
            self.statusbar.push(1,_("Problems while opening News OutBox"))
        else:
            total=len(articles)
            news_sent=total
    
            cp=ConfigParser.ConfigParser()
            cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
            self.connectionsPool=dict()        
            for server in cp.sections():
                if cp.get(server,"nntp_use_ssl")=="True":
                    self.connectionsPool[server]=SSLConnection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
                else:
                    self.connectionsPool[server]=Connection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))

            i=0    
            for articleName in articles:
                i=i+1
                try:
                    f=open(os.path.join(self.wdir,"outbox/news/",articleName),"rb")
                except:
                    self.statusbar.push(1,_("Problems while opening article :")+articleName)
                else:
                    self.statusbar.push(1,_("Sending Article: ")+articleName)
                    while gtk.events_pending():
                        gtk.main_iteration(False)
                    draftArticle=cPickle.load(f)
                    f.close()
                    newsgroups=draftArticle.get("newsgroups","")
                    from_name=draftArticle.get("from_name","")
                    subject=draftArticle.get("subject","")
                    references=draftArticle.get("references","")
                    output_charset=draftArticle.get("output_charset","")
                    body=draftArticle.get("body","")
                    custom_names=draftArticle.get("custom_names",[])
                    custom_values=draftArticle.get("custom_values",[])
                    article_to_send=Article_To_Send(newsgroups,from_name,subject,references,user_agent,output_charset,ordered_list,body,custom_names,custom_values,self.configs["gen_mid"],self.configs["fqdn"])
                    article=article_to_send.get_article()
                    server_name=draftArticle.get("server_name","")

                    message,articlePosted=self.connectionsPool[server_name].sendArticle(article)
                    self.statusbar.push(1,message)
                    if articlePosted:
                        os.remove(os.path.join(self.wdir,"outbox/news/",articleName))
                        self.store_article(os.path.join(self.wdir,"sent/news"),draftArticle)
                    else:
                        news_sent=news_sent-1
                while gtk.events_pending():
                    gtk.main_iteration(False)
            self.statusbar.push(1,_("Sent %d Articles") % (news_sent,))
            for connection in self.connectionsPool.itervalues():
                connection.closeConnection()

            self.populateFolderTree()
    
    def sendQueuedMails(self,obj):
        '''Send mails stored in outbox'''
        ordered_list=load_ordered_list()
        user_agent=self.VERSION

        try:
            mails=os.listdir(os.path.join(self.wdir,"outbox/mail"))
        except:
            self.statusbar.push(1,_("Problems while opening Mail OutBox"))
        else:
            total=len(mails)
            mail_sent=total
            i=0
            self.mailConnection=SMTPConnection(self.configs["smtp_server"],int(self.configs["smtp_port"]),self.configs["smtp_auth"],self.configs["smtp_username"],self.configs["smtp_password"])
            for mailName in mails:
                i=i+1
                try:
                    f=open(os.path.join(self.wdir,"outbox/mail/",mailName),"rb")
                except:
                    self.statusbar.push(1,_("Problems while opening mail :")+mailName)
                else:
                    self.statusbar.push(1,_("Sending Mail: ")+mailName)
                    while gtk.events_pending():
                        gtk.main_iteration(False)
                    draftMail=cPickle.load(f)
                    f.close()
                    to_name=draftMail.get("to_name","")
                    from_name=draftMail.get("from_name","")
                    subject=draftMail.get("subject","")
                    references=draftMail.get("references","")
                    output_charset=draftMail.get("output_charset","")
                    body=draftMail.get("body","")
                    date=draftMail.get("date","")

                    mail_to_send=Mail_To_Send(to_name,from_name,date,subject,references,user_agent,output_charset,ordered_list,body)
                    mail=mail_to_send.get_article()
                    f.close()
                    message,mailSent=self.mailConnection.sendMail(from_name,to_name,mail)
                    self.statusbar.push(1,message)
                    if mailSent:
                        os.remove(os.path.join(self.wdir,"outbox/mail/",mailName))
                        self.store_article(os.path.join(self.wdir,"sent/mail"),draftMail)
                    else:
                        mail_sent=mail_sent-1
                while gtk.events_pending():
                    gtk.main_iteration(False)
            self.statusbar.push(1,_("Sent %d Mails") % (mail_sent,))
            self.mailConnection.closeConnection()                        
            self.populateFolderTree()
    
    def save_sizes(self):
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"rb")
        except IOError:
            sizes={}        
        else:
            sizes=cPickle.load(f)
        if not self.outboxwin_width:
            sizes["outboxwin_width"],sizes["outboxwin_height"]=self.win.get_size()
        else:
            sizes["outboxwin_width"]=self.outboxwin_width
            sizes["outboxwin_height"]=self.outboxwin_height
        sizes["outboxwin_pos_x"],sizes["outboxwin_pos_y"]=self.win.get_position()
        sizes["outboxwin_col_subject"]=self.previewTreeColumnSubject.get_width()
        sizes["outboxwin_col_to"]=self.previewTreeColumnTo.get_width()
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"wb")
        except IOError:
            pass
        else:
            cPickle.dump(sizes,f,1)
            f.close()

    def set_sizes(self):
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"rb")
        except IOError:
            self.win.maximize()
        else:
            sizes=cPickle.load(f)
            f.close()
            outboxwin_width=sizes.get("outboxwin_width",None)
            outboxwin_height=sizes.get("outboxwin_height",None)
            if outboxwin_width and outboxwin_height:
                self.win.resize(int(outboxwin_width),int(outboxwin_height))
            else:
                self.win.maximize()
            outboxwin_pos_x=sizes.get("outboxwin_pos_x",None)
            outboxwin_pos_y=sizes.get("outboxwin_pos_y",None)
            self.previewTreeColumnSubject.set_fixed_width(int(sizes.get("outboxwin_col_subject",350)))
            self.previewTreeColumnTo.set_fixed_width(int(sizes.get("outboxwin_col_to",150)))
            if outboxwin_pos_x and outboxwin_pos_y:
                self.win.move(int(outboxwin_pos_x),int(outboxwin_pos_y))

    def create_ui(self):
        self.ui = gtk.UIManager()
        accelgroup = self.ui.get_accel_group()
        actiongroup= gtk.ActionGroup("OutboxWindowActions")
        self.win.add_accel_group(accelgroup)
        obcuts=load_shortcuts("outbox")        
        actions=[("Outbox",None,_("_Outbox")),
                ("send_article","xpn_send_queued_art",_("_Send Queued Articles"),obcuts["send_article"],_("Send Queued Articles"),self.sendQueuedArticles),
                ("send_mail","xpn_send_queued_mail",_("Send Queued _Mails"),obcuts["send_mail"],_("Send Queued Mails"),self.sendQueuedMails),
                ("edit","xpn_post",_("_Edit Article/Mail"),obcuts["edit"],_("Edit Article/Mail"),self.openArticle),
                ("delete","xpn_delete",_("_Delete Article/Mail"),obcuts["delete"],_("Delete Article/Mail"),self.deleteArticle),
                ("exit","xpn_exit",_("_Exit"),obcuts["exit"],_("Exit"),self.destroy)]
                

        for action in actions: 
            if len(action)<7:
                actiongroup.add_actions([action])
            else:
                actiongroup.add_actions([action[0:6]],action[6:])

        self.ui.insert_action_group(actiongroup,0)
        merge_id = self.ui.add_ui_from_string(ui_string)


    def __init__(self,mainWin,VERSION):
        self.configs=mainWin.configs
        self.VERSION=VERSION
        self.subscribedGroups=mainWin.subscribed_groups
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        #self.win.connect("destroy",self.destroy)
        self.win.set_title(_("Outbox Manager"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/outbox.xpm"))

        vbox=gtk.VBox()
       
        #MenuBar
        self.create_ui()
        menubar=self.ui.get_widget("/OutboxMenuBar")
        vbox.pack_start(menubar,False,True)
        menubar.show()

        #ToolBar
        toolbar=self.ui.get_widget("/OutboxToolBar")
        vbox.pack_start(toolbar,False,True)
        toolbar.show()
        #toolbar.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_style(gtk.SHADOW_NONE)

        self.win.add(vbox)
        
        #HBox
        hpaned=gtk.HPaned()
        vbox.pack_start(hpaned,True,True)
        
        
        #Folder Tree
        self.folderTree=gtk.TreeView()
        model=gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gtk.gdk.Pixbuf)
        self.folderTree.set_model(model)
        text_renderer_bold=gtk.CellRendererText()
        text_renderer_bold.set_property("weight",1000)
        text_renderer_number=gtk.CellRendererText()
        text_renderer_number.set_property("xalign",.5)
        pix_renderer=gtk.CellRendererPixbuf()


        self.folderTreeColumnFolder=gtk.TreeViewColumn(_("Folder"))
        self.folderTreeColumnFolder.pack_start(pix_renderer)
        self.folderTreeColumnFolder.pack_start(text_renderer_bold)
        self.folderTreeColumnFolder.set_attributes(pix_renderer,pixbuf=2)
        self.folderTreeColumnFolder.set_attributes(text_renderer_bold,text=0)
        self.folderTreeColumnNumber=gtk.TreeViewColumn(_("Number"),text_renderer_number,text=1)
        self.folderTree.append_column(self.folderTreeColumnFolder)
        self.folderTree.append_column(self.folderTreeColumnNumber)

        #self.folderTree.set_expander_column(self.folderTreeColumn)
        hpaned.add(self.folderTree)

        #Preview Tree
        scrolledwin=gtk.ScrolledWindow()
        scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        
        
        self.previewTree=gtk.TreeView()
        scrolledwin.add(self.previewTree)
        # 0: Subject, 1: Newsgroups/To, 2: Date, 3: Article, 4: IsMail, 5: PathToArticle, 6: Seconds
        model=gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_PYOBJECT,gobject.TYPE_BOOLEAN,gobject.TYPE_STRING,gobject.TYPE_INT)
        self.previewTree.set_model(model)
        text_renderer=gtk.CellRendererText()
        self.previewTreeColumnSubject=gtk.TreeViewColumn(_("Subject"),text_renderer,text=0)
        self.previewTreeColumnSubject.set_resizable(True)
        self.previewTreeColumnSubject.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.previewTreeColumnSubject.set_fixed_width(300)
        self.previewTreeColumnSubject.set_sort_column_id(0)
        self.previewTreeColumnTo=gtk.TreeViewColumn(_("Newsgroups/To"),text_renderer,text=1)
        self.previewTreeColumnTo.set_resizable(True)
        self.previewTreeColumnTo.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.previewTreeColumnTo.set_fixed_width(150)
        self.previewTreeColumnTo.set_sort_column_id(1)
        self.previewTreeColumnDate=gtk.TreeViewColumn(_("Date"),text_renderer,text=2)
        self.previewTreeColumnDate.set_sort_column_id(6)
        self.previewTree.append_column(self.previewTreeColumnSubject)
        self.previewTree.append_column(self.previewTreeColumnTo)
        self.previewTree.append_column(self.previewTreeColumnDate)
        hpaned.add(scrolledwin)
        model.set_sort_column_id(6,gtk.SORT_ASCENDING)
        self.statusbar=gtk.Statusbar()
        vbox.pack_start(self.statusbar,False,True)
        #self.win.maximize()

        self.wdir=get_wdir()

        #self.folderTree.connect("row_activated",self.openFolder)
        self.folderTree.get_selection().connect("changed",self.openFolder)
        self.previewTree.connect("row_activated",self.openArticle)
        
       
        self.set_sizes()
        self.outboxwin_width=None
        self.outboxwin_height=None
        self.populateFolderTree()
        
