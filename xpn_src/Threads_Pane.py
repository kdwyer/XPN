import gtk
import gobject
import pango
import cPickle
import os
from xpn_src.UserDir import get_wdir


class Threads_Pane:
    def get_widget(self):
        return self.scrolledwin

    def unparent(self):
        self.scrolledwin.unparent()

    def show(self):
        self.scrolledwin.show_all()

    def hide(self):
        self.scrolledwin.hide_all()

    def clear(self):
        model=self.threads_tree.get_model()
        model.clear()

    def set_background(self,color):
        color=gtk.gdk.color_parse(color)
        self.threads_tree.modify_base(gtk.STATE_NORMAL,color)

    def set_foreground(self,color):
        color=gtk.gdk.color_parse(color)
        self.threads_tree.modify_text(gtk.STATE_NORMAL,color)
        self.threads_tree.modify_fg(gtk.STATE_NORMAL,color)

    def delete_row(self,model,iter):
        model.remove(iter)

    def insert(self,model,iter_parent,iter_sibling,values):
        iter=model.insert_before(iter_parent,iter_sibling)
        if values[5]: values[5]=pango.WEIGHT_BOLD
        else :values[5]= pango.WEIGHT_NORMAL
        if len(values)==19: #quando cerco l'articolo padre non passo tutte le info
            if values[18]: values[18]=pango.UNDERLINE_SINGLE
            else :values[18]= pango.UNDERLINE_NONE
        
        for i in range(len(values)):
            if i==1 or i==2 or i==3:
                value=values[i].encode("utf-8")
            else:
                value=values[i]
            model.set_value(iter,i,value)
        return iter

    def get_subject(self,model,article_iter):
        return model.get_value(article_iter,1)

    def get_article(self,model,article_iter):
        return model.get_value(article_iter,4)
    
    def set_article(self,model,article_iter,article):
        model.set_value(article_iter,4,article)
        
    def get_unread_in_thread(self,model,article_iter):
        return model.get_value(article_iter,12)
    
    def get_watched_in_thread(self,model,article_iter):
        return model.get_value(article_iter,19)
    
    def get_watched_unread_in_thread(self,model,article_iter):
        return model.get_value(article_iter,20)

    def set_unread_in_thread(self,model,article_iter,unread_in_thread):
        model.set_value(article_iter,12,unread_in_thread)

    def set_watched_in_thread(self,model,article_iter,watched_in_thread):
        model.set_value(article_iter,19,watched_in_thread)
        
    def set_watched_unread_in_thread(self,model,article_iter,watched_unread_in_thread):
        model.set_value(article_iter,20,watched_unread_in_thread)
        model.set_value(article_iter,18,watched_unread_in_thread!=0)

    def set_unread_in_thread_visible(self,model,article_iter,unread_in_thread_visible):
        model.set_value(article_iter,13,unread_in_thread_visible)

    def update_unread_in_thread(self,is_read,show_threads,insert):
        if show_threads and ((is_read and insert) or (not is_read and not insert)):
            model,iter_selected=self.threads_tree.get_selection().get_selected()
            parent_path=tuple([model.get_path(iter_selected)[0],])
            parent_iter=model.get_iter(parent_path)
            unread_in_thread=self.get_unread_in_thread(model,parent_iter)
            if insert:  unread_in_thread=unread_in_thread+1
            else:       unread_in_thread=unread_in_thread-1
            self.set_unread_in_thread(model,parent_iter,unread_in_thread)
            self.set_unread_in_thread_visible(model,parent_iter,unread_in_thread!=0)
    
    def update_watched_in_thread(self,is_watched,show_threads,insert):
        if show_threads and ((is_watched and insert) or (not is_watched and not insert)):
            model,iter_selected=self.threads_tree.get_selection().get_selected()
            parent_path=tuple([model.get_path(iter_selected)[0],])
            parent_iter=model.get_iter(parent_path)
            watched_in_thread=self.get_watched_in_thread(model,parent_iter)
            if insert:  watched_in_thread=watched_in_thread+1
            else:       watched_in_thread=watched_in_thread-1
            self.set_watched_in_thread(model,parent_iter,watched_in_thread)
    
    def update_watched_unread_in_thread(self,is_read,is_watched,show_threads,insert_in_unreads,insert_in_watched,updating_unreads):
        print is_read,is_watched,show_threads,insert_in_unreads,insert_in_watched,updating_unreads
        inserting=((is_read and insert_in_unreads) and is_watched) or ((is_watched and insert_in_watched) and not is_read and not updating_unreads)
        removing=((not is_read and not insert_in_unreads) and is_watched) or ((not is_watched and not insert_in_watched) and not is_read and not updating_unreads)
        
        if show_threads and (inserting or removing):
            model,iter_selected=self.threads_tree.get_selection().get_selected()
            parent_path=tuple([model.get_path(iter_selected)[0],])
            parent_iter=model.get_iter(parent_path)
            watched_unread_in_thread=self.get_watched_unread_in_thread(model,parent_iter)
            print "BEFORE:",watched_unread_in_thread
            if inserting:  watched_unread_in_thread=watched_unread_in_thread+1
            else:          watched_unread_in_thread=watched_unread_in_thread-1
            print "AFTER:",watched_unread_in_thread
            self.set_watched_unread_in_thread(model,parent_iter,watched_unread_in_thread)

    def get_is_unread(self,model,article_iter):
        return model.get_value(article_iter,5)==pango.WEIGHT_BOLD

    def set_is_unread(self,model,article_iter,is_unread):
        if is_unread: weight=pango.WEIGHT_BOLD
        else: weight=pango.WEIGHT_NORMAL
        model.set_value(article_iter,5,weight)
    
    def new_model(self):
        #MODEL: 0 Icon, 1 Subject, 2 From, 3 Date, 4 XPN_article, 5 Use_Bold, 6 Seconds, 7 Score, 8 Score_Foreground,
        #       9 Score_Visible, 10 Icon2, 11 Icon3, 12 Unread_In_Thread, 13 Unread_Visible, 14 Article_FG_Set, 15 Article_FG
        #      16 Article_BG_Set,17 Article_BG, 18 Use_Underline, 19 Watched_In_Thread, Watched_Unread_in_Thread
        model=gtk.TreeStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT,gobject.TYPE_INT,gobject.TYPE_INT,gobject.TYPE_INT,gobject.TYPE_STRING, 
                            gobject.TYPE_BOOLEAN, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf,gobject.TYPE_INT,gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, 
                            gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,gobject.TYPE_BOOLEAN,gobject.TYPE_INT,gobject.TYPE_INT)
        return model

    def set_model(self,model):
        self.threads_tree.set_model(model)

    def find_next_row(self,model,current_iter):
        if model.iter_has_child(current_iter):
            next_iter = model.iter_children(current_iter)
        else:
            next_iter=model.iter_next(current_iter)
            while not next_iter:
                prev_iter=model.iter_parent(current_iter)
                current_iter=prev_iter
                if not prev_iter:
                    break
                next_iter=model.iter_next(current_iter)
        return next_iter

    def find_previous_row(self,model,current_iter):
        path=model.get_path(current_iter)
        new_path=[path[i] for i in xrange(len(path)-1)]
        if path[len(path)-1]>0:
            new_path.append(path[len(path)-1]-1)
        new_path=tuple(new_path)
        if new_path:
            prev_iter = model.get_iter(new_path)
            return prev_iter
        else:
            return current_iter

    def update_article_icon(self,name,iter_row=None):
        model,iter_selected=self.threads_tree.get_selection().get_selected()
        if iter_row:
            iter_selected=iter_row
        current_icon=model.get_value(iter_selected,0)
        current_icon2=model.get_value(iter_selected,10)
        current_icon3=model.get_value(iter_selected,11)
        icon=current_icon
        icon2=current_icon2
        icon3=current_icon3
        if name=="read":
            if current_icon!=self.art_fup:
                icon=self.art_read
            else:
                icon=self.art_fup
        elif name=="fup":
            icon=self.art_fup
        elif name=="unread":
            icon=self.art_unread
        elif name=="download":
            icon=self.art_mark
        elif name=="body":
            icon=self.art_body
        elif name=="keep":
            icon2=self.art_keep
        elif name=="unkeep":
            icon2=self.art_unkeep
        elif name=="watch":
            icon3=self.art_watch
        elif name=="unwatchignore":
            icon3=self.art_unwatchignore
        elif name=="ignore":
            icon3=self.art_ignore
        model.set_value(iter_selected,0,icon)
        model.set_value(iter_selected,10,icon2)
        model.set_value(iter_selected,11,icon3)


    def get_subthread(self,iter_parent,model,iter_list):
        '''Return the list of iters in the subthread without the father'''
        if model.iter_has_child(iter_parent):
            number=model.iter_n_children(iter_parent)
            for i in xrange(number):
                iter_child=model.iter_nth_child(iter_parent,i)
                self.get_subthread(iter_child,model,iter_list)
                iter_list.append(iter_child)
        return iter_list

   
    def __init__(self,configs):
        self.art_unread=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unread.xpm")
        self.art_read=gtk.gdk.pixbuf_new_from_file("pixmaps/art_read.xpm")
        self.art_fup=gtk.gdk.pixbuf_new_from_file("pixmaps/art_fup.xpm")
        self.art_mark=gtk.gdk.pixbuf_new_from_file("pixmaps/art_mark.xpm")
        self.art_body=gtk.gdk.pixbuf_new_from_file("pixmaps/art_body.xpm")
        self.art_keep=gtk.gdk.pixbuf_new_from_file("pixmaps/art_keep.xpm")
        self.art_unkeep=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unkeep.xpm")
        self.art_watch=gtk.gdk.pixbuf_new_from_file("pixmaps/art_watch.xpm")
        self.art_unwatchignore=gtk.gdk.pixbuf_new_from_file("pixmaps/art_unwatchignore.xpm")
        self.art_ignore=gtk.gdk.pixbuf_new_from_file("pixmaps/art_ignore.xpm")

        #ThreadsScrolledWin
        self.scrolledwin=gtk.ScrolledWindow()
        self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        try:
            f=open(os.path.join(get_wdir(),"dats/sizes.dat"),"rb")
        except IOError:
            column1_width=41
            column2_width=415
            column3_width=201
            column4_width=95
            column5_width=60
        else:
            sizes=cPickle.load(f)
            f.close()
            column1_width=sizes.get("threads_col_status",41)
            column2_width=sizes.get("threads_col_subject",415)
            column3_width=sizes.get("threads_col_from",201)
            column4_width=sizes.get("threads_col_date",95)
            column5_width=sizes.get("threads_col_score",60)

        #ThreadsTree
        self.threads_tree=gtk.TreeView()
        model=self.new_model()
        self.set_model(model)
        pix_renderer=gtk.CellRendererPixbuf()
        pix_renderer2=gtk.CellRendererPixbuf()
        pix_renderer3=gtk.CellRendererPixbuf()
        text_renderer=gtk.CellRendererText()
        text_renderer_unread=gtk.CellRendererText()
        text_renderer_unread.set_property("xalign",1)
        #text_renderer.set_property("weight",1000)
        text_renderer_score=gtk.CellRendererText()
        text_renderer_score.set_property("xalign",.5)
        self.column1=gtk.TreeViewColumn("Status")
        self.column1.pack_start(pix_renderer,False)
        self.column1.pack_start(pix_renderer2,False)
        self.column1.pack_start(pix_renderer3,False)
        self.column1.pack_start(text_renderer_unread,False)
        self.column1.set_attributes(pix_renderer,pixbuf=0)
        self.column1.set_attributes(pix_renderer2,pixbuf=10)
        self.column1.set_attributes(pix_renderer3,pixbuf=11)
        self.column1.set_attributes(text_renderer_unread,text=12,visible=13)

        self.column2=gtk.TreeViewColumn(_("Subject"),text_renderer,text=1,weight=5,foreground_set=14,foreground=15,background_set=16,background=17,underline=18)
        self.column3=gtk.TreeViewColumn(_("From"),text_renderer,text=2,weight=5,foreground_set=14,foreground=15,background_set=16,background=17)
        self.column4=gtk.TreeViewColumn(_("Date"),text_renderer,text=3,weight=5,foreground_set=14,foreground=15,background_set=16,background=17)
        self.column5=gtk.TreeViewColumn(_("Score"),text_renderer_score,text=7,foreground=8,visible=9)


        self.column2.set_resizable(True)
        self.column2.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column2.set_fixed_width(column2_width)
        self.column2.set_sort_column_id(1)

        self.column3.set_resizable(True)
        self.column3.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column3.set_fixed_width(column3_width)
        self.column3.set_sort_column_id(2)

        self.column4.set_resizable(True)
        self.column4.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column4.set_fixed_width(column4_width)
        self.column4.set_sort_column_id(6)

        self.column5.set_sort_column_id(7)

        self.threads_tree.append_column(self.column1)
        if configs["exp_column"]=="From":
            self.threads_tree.append_column(self.column3)       
            self.threads_tree.append_column(self.column2)
            self.threads_tree.set_expander_column(self.column3)
        else:
            self.threads_tree.append_column(self.column2)
            self.threads_tree.append_column(self.column3)       
            self.threads_tree.set_expander_column(self.column2)

        self.threads_tree.append_column(self.column4)
        self.threads_tree.append_column(self.column5)
        try: self.threads_tree.set_enable_tree_lines(True)
        except: pass
        self.scrolledwin.add(self.threads_tree)

        color=configs["background_color"]
        self.set_background(color)
        color=configs["text_color"]
        self.set_foreground(color)
        if configs["use_system_fonts"]=="True":
            self.threads_tree.modify_font(pango.FontDescription(""))
        else:
            self.threads_tree.modify_font(pango.FontDescription(configs["font_threads_name"]))

