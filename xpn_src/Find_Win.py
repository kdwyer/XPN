import gtk
import re
from xpn_src.Article import Article
import cPickle

import os
import glob
from xpn_src.UserDir import get_wdir
from xpn_src.Articles_DB import Articles_DB


class Find_Win:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget):
        self.window.destroy()

    def show(self):
        self.window.show_all()

    def is_match(self,non_empty,article,rule,match_rule,from_string,subj_string,msgid_string,ref_string,body_string):
        found_vet=[]
        if 0 in non_empty:
            if match_rule(article.from_name,from_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 1 in non_empty:
            if match_rule(article.subj,subj_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 2 in non_empty:
            if match_rule(article.msgid,msgid_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 3 in non_empty:
            if match_rule(article.ref,ref_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 4 in non_empty:
            body=article.get_body()
            if body!=None:
                body=" ".join(body)
                if match_rule(body,body_string):
                    found_vet.append(True)
                else:
                    found_vet.append(False)
            else:
                found_vet.append(False)

        if rule=="And":
            found=reduce(lambda x,y: x and y, found_vet,True)
        else:
            found=reduce(lambda x,y: x or y, found_vet,False)
        return found


    def next_match(self,obj):
        non_empty=[]
        from_string=self.entry_from.get_text().decode("utf-8")
        if from_string!="":
            non_empty.append(0)
        subj_string=self.entry_subject.get_text().decode("utf-8")
        if subj_string!="":
            non_empty.append(1)
        msgid_string=self.entry_msgid.get_text().decode("utf-8")
        if msgid_string!="":
            non_empty.append(2)
        ref_string=self.entry_ref.get_text().decode("utf-8")
        if ref_string!="":
            non_empty.append(3)
        body_string=self.entry_body.get_text().decode("utf-8")
        if body_string!="":
            non_empty.append(4)

        rule=["And","Or"][self.opt_menu.get_active()]
        case_insensitive=self.checkbutton_case.get_active()
        use_regex=self.checkbutton_regex.get_active()
        start_beginning=self.checkbutton_start.get_active()

        def match_re_case_ins(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE|re.IGNORECASE).findall(field)
            except:
                match_rule=False
            return match_rule

        def match_re_case_sens(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE).findall(field)
            except:
                match_rule=False
            return match_rule

        #select the correct function
        if use_regex:
            if case_insensitive:
                match_rule=lambda field,regex: match_re_case_ins(field,regex)
            else:
                match_rule=lambda field,regex: match_re_case_sens(field,regex)
        else:
            if case_insensitive:
                match_rule=lambda field,word: field.lower().find(word.lower())+1
            else:
                match_rule=lambda field,word: field.find(word)+1

        #select the iter
        treesel=self.main_win.threads_pane.threads_tree.get_selection()
        model,iter_selected=treesel.get_selected()
        column=self.main_win.threads_pane.threads_tree.get_column(0)

        found=False
        if iter_selected==None or start_beginning:
            iter_selected=model.get_iter_first()

            if iter_selected!=None:
                article=self.main_win.threads_pane.get_article(model,iter_selected)
                found=self.is_match(non_empty,article,rule,match_rule,from_string,subj_string,msgid_string,ref_string,body_string)


        #begin the loop
        while (not found) and (iter_selected!=None):
            iter_selected=self.main_win.threads_pane.find_next_row(model,iter_selected)
            if iter_selected!=None:
                article=self.main_win.threads_pane.get_article(model,iter_selected)
                found=self.is_match(non_empty,article,rule,match_rule,from_string,subj_string,msgid_string,ref_string,body_string)
            else:
                found=False


        if found:
            path=model.get_path(iter_selected)
            root_path=[]
            root_path.append(path[0])
            root_path=tuple(root_path)
            self.main_win.threads_pane.threads_tree.expand_row(root_path,True)
            self.main_win.threads_pane.threads_tree.grab_focus()
            self.main_win.threads_pane.threads_tree.scroll_to_cell(path,None,True,0.4,0.0)
            self.main_win.threads_pane.threads_tree.set_cursor(path,None,False)
            self.main_win.threads_pane.threads_tree.row_activated(path,column)
            self.checkbutton_start.set_active(False)

    def __init__(self,main_win):
        self.main_win=main_win
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Find Article"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(350,300)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/find.xpm"))


        vbox=gtk.VBox()
        vbox.set_border_width(8)
        label_from=gtk.Label(_("From"))
        label_from.set_use_markup(True)
        label_from.set_alignment(0,0.5)
        label_subject=gtk.Label(_("Subject"))
        label_subject.set_use_markup(True)
        label_subject.set_alignment(0,0.5)
        label_msgid=gtk.Label(_("Message-ID"))
        label_msgid.set_use_markup(True)
        label_msgid.set_alignment(0,0.5)
        label_ref=gtk.Label(_("References"))
        label_ref.set_use_markup(True)
        label_ref.set_alignment(0,0.5)
        label_body=gtk.Label(_("Body"))
        label_body.set_use_markup(True)
        label_body.set_alignment(0,0.5)
        self.entry_from=gtk.Entry()
        self.entry_subject=gtk.Entry()
        self.entry_msgid=gtk.Entry()
        self.entry_ref=gtk.Entry()
        self.entry_body=gtk.Entry()
        fields_label=gtk.Label("<b>"+_("Fields")+"</b>")
        fields_label.set_alignment(0,0.5)
        fields_label.set_use_markup(True)
        fields_vbox=gtk.VBox()
        fields_vbox.set_border_width(4)
        fields_vbox.pack_start(fields_label,False,False,4)
        find_table=gtk.Table(6,2,False)
        find_table.set_border_width(4)

        find_table.attach(label_from,0,1,0,1,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_subject,0,1,1,2,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_msgid,0,1,2,3,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_ref,0,1,4,5,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_body,0,1,5,6,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(self.entry_from,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_subject,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_msgid,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_ref,1,2,4,5,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_body,1,2,5,6,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)

        fields_vbox.pack_start(find_table,True,True,4)
        vbox.pack_start(fields_vbox,True,False,2)

        rule_table=gtk.Table(4,1,False)
        rule_table.set_border_width(4)
        hbox=gtk.HBox()
        self.checkbutton_start=gtk.CheckButton(_("Start from the Beginning"))
        self.checkbutton_regex=gtk.CheckButton(_("Use Regular Expression"))
        self.checkbutton_case=gtk.CheckButton(_("Case Insensitive"))

        label=gtk.Label(_("Rule used to combine search results"))
        self.opt_menu=gtk.combo_box_new_text()
        self.opt_menu.append_text(_("AND"))
        self.opt_menu.append_text(_("OR"))
        self.opt_menu.set_active(0)

        rule_table.attach(self.checkbutton_start,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        rule_table.attach(self.checkbutton_regex,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        rule_table.attach(self.checkbutton_case,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        hbox.pack_start(self.opt_menu,False,True,2)
        hbox.pack_start(label,False,True)
        rule_table.attach(hbox,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        rule_label=gtk.Label("<b>"+_("Rules")+"</b>")
        rule_label.set_alignment(0,0.5)
        rule_label.set_use_markup(True)
        rule_vbox=gtk.VBox()
        rule_vbox.pack_start(rule_label,False,False,4)
        rule_vbox.set_border_width(4)
        rule_vbox.pack_start(rule_table,True,True,4)
        vbox.add(rule_vbox)

        hbox_buttons=gtk.HBox()
        hbox_buttons.set_border_width(8)
        self.button_close=gtk.Button(None,gtk.STOCK_CLOSE)
        self.button_close.connect("clicked",self.destroy)
        self.button_next=gtk.Button(None,gtk.STOCK_GO_FORWARD)
        self.button_next.connect("clicked",self.next_match)
        hbox_buttons.pack_start(self.button_close,True,True,2)
        hbox_buttons.pack_start(self.button_next,True,True,2)
        vbox.pack_start(hbox_buttons,True,False,6)

        self.window.add(vbox)


class Search_Win:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget):
        self.window.destroy()

    def show(self):
        self.window.show_all()

    def next_match(self,obj):
        text=self.entry_text.get_text().decode("utf-8")
        case_insensitive=self.checkbutton_case.get_active()
        use_regex=self.checkbutton_regex.get_active()
        start_beginning=self.checkbutton_start.get_active()

        def match_re_case_ins(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE|re.IGNORECASE).search(field)
            except:
                match_rule=False
            return match_rule

        def match_re_case_sens(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE).search(field)
            except:
                match_rule=False
            return match_rule


        if use_regex:
            if case_insensitive:
                #match_rule=lambda field,regex: re.compile(regex,re.UNICODE|re.IGNORECASE).search(field)
                match_rule=lambda field,regex: match_re_case_ins(field,regex)
            else:
                #match_rule=lambda field,regex: re.compile(regex,re.UNICODE).search(field)
                match_rule=lambda field,regex: match_re_case_sens(field,regex)
        else:
            if case_insensitive:
                match_rule=lambda field,word: field.lower().find(word.lower())+1
            else:
                match_rule=lambda field,word: field.find(word)+1

        if text!="":
            start,end=self.main_win.article_pane.buffer.get_bounds()
            sel_bounds=self.main_win.article_pane.buffer.get_selection_bounds()
            line_number=0
            char_offset=0
            if sel_bounds:
                #There is selected text, let's start after it
                start=sel_bounds[1]
                line_number=start.get_line()
                char_offset=start.get_line_offset()
            if start_beginning:
                start,end=self.main_win.article_pane.buffer.get_bounds()
                line_number=0
                char_offset=0
            body=self.main_win.article_pane.buffer.get_text(start,end,True).decode("utf-8").split("\n")
            success=False
            for line in body:
                pos=match_rule(line,text)
                if pos:
                    if use_regex:
                        start=pos.start()
                        end=pos.end()
                    else:
                        start=pos-1
                        end=pos+len(text)-1
                    iter_start=self.main_win.article_pane.buffer.get_start_iter()
                    iter_start.set_line(line_number)
                    iter_stop=iter_start.copy()
                    iter_start.set_line_offset(start+char_offset)
                    iter_stop.set_line_offset(end+char_offset)
                    match=self.main_win.article_pane.buffer.get_text(iter_start,iter_stop,True)
                    success=True
                    break
                line_number=line_number+1
                char_offset=0
            if success:
                self.main_win.article_pane.buffer.move_mark_by_name("insert",iter_start)
                self.main_win.article_pane.buffer.move_mark_by_name("selection_bound",iter_stop)
                self.checkbutton_start.set_active(False)
                self.main_win.article_pane.textview.scroll_to_iter(iter_start,0.3)



    def __init__(self,main_win):
        self.main_win=main_win
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Search in the Body"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(350,150)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/search.xpm"))


        vbox=gtk.VBox()
        vbox.set_border_width(8)
        text_label=gtk.Label(_("Text or Regular Expression"))
        self.entry_text=gtk.Entry()
        vbox.pack_start(text_label,True,False,2)
        vbox.pack_start(self.entry_text,True,False,2)
        self.checkbutton_start=gtk.CheckButton(_("Start from the Beginning"))
        self.checkbutton_regex=gtk.CheckButton(_("Use Regular Expression"))
        self.checkbutton_case=gtk.CheckButton(_("Case Insensitive"))
        vbox.pack_start(self.checkbutton_start,True,False,4)
        vbox.pack_start(self.checkbutton_regex,True,False,4)
        vbox.pack_start(self.checkbutton_case,True,False,4)
        hbox_buttons=gtk.HBox()
        hbox_buttons.set_border_width(8)
        self.button_close=gtk.Button(None,gtk.STOCK_CLOSE)
        self.button_close.connect("clicked",self.destroy)
        self.button_next=gtk.Button(None,gtk.STOCK_GO_FORWARD)
        self.button_next.connect("clicked",self.next_match)
        hbox_buttons.pack_start(self.button_close,True,True,2)
        hbox_buttons.pack_start(self.button_next,True,True,2)
        vbox.pack_start(hbox_buttons,True,False,6)

        self.window.add(vbox)


class GlobalSearch:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget):
        self.window.destroy()

    def show(self):
        self.window.show_all()

    def is_match(self,non_empty,article,rule,match_rule,from_string,subj_string,msgid_string,ref_string,body_string):
        found_vet=[]
        if 0 in non_empty:
            if match_rule(article.from_name,from_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 1 in non_empty:
            if match_rule(article.subj,subj_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 2 in non_empty:
            if match_rule(article.msgid,msgid_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 3 in non_empty:
            if match_rule(article.ref,ref_string):
                found_vet.append(True)
            else:
                found_vet.append(False)
        if 4 in non_empty:
            body=article.get_body()
            if body!=None:
                body=" ".join(body)
                if match_rule(body,body_string):
                    found_vet.append(True)
                else:
                    found_vet.append(False)
            else:
                found_vet.append(False)

        if rule=="And":
            found=reduce(lambda x,y: x and y, found_vet,True)
        else:
            found=reduce(lambda x,y: x or y, found_vet,False)
        return found


    def next_match(self,obj):
        non_empty=[]
        from_string=self.entry_from.get_text().decode("utf-8")
        if from_string!="":
            non_empty.append(0)
        subj_string=self.entry_subject.get_text().decode("utf-8")
        if subj_string!="":
            non_empty.append(1)
        msgid_string=self.entry_msgid.get_text().decode("utf-8")
        if msgid_string!="":
            non_empty.append(2)
        ref_string=self.entry_ref.get_text().decode("utf-8")
        if ref_string!="":
            non_empty.append(3)
        body_string=self.entry_body.get_text().decode("utf-8")
        if body_string!="":
            non_empty.append(4)

        rule=["And","Or"][self.opt_menu.get_active()]
        case_insensitive=self.checkbutton_case.get_active()
        use_regex=self.checkbutton_regex.get_active()

        def match_re_case_ins(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE|re.IGNORECASE).findall(field)
            except:
                match_rule=False
            return match_rule

        def match_re_case_sens(field,regex):
            try:
                match_rule=re.compile(regex,re.UNICODE).findall(field)
            except:
                match_rule=False
            return match_rule

        #select the correct function
        if use_regex:
            if case_insensitive:
                match_rule=lambda field,regex: match_re_case_ins(field,regex)
            else:
                match_rule=lambda field,regex: match_re_case_sens(field,regex)
        else:
            if case_insensitive:
                match_rule=lambda field,word: field.lower().find(word.lower())+1
            else:
                match_rule=lambda field,word: field.find(word)+1

        #select the iter
        treesel=self.main_win.threads_pane.threads_tree.get_selection()
        model,iter=treesel.get_selected()
        column=self.main_win.threads_pane.threads_tree.get_column(0)

        subscribed=self.art_db.getSubscribed()
        name="global.search.results."+str(len(glob.glob(os.path.join(self.wdir,"groups_info","global.search.results*")))+1)
        if not os.path.isdir(os.path.join(self.wdir,"groups_info",name)):
            os.makedirs(os.path.join(self.wdir,"groups_info",name))
        self.art_db.createGroup(name)
        unread_number=0
        for group in subscribed:
            for article in self.art_db.getArticles(group[0]):
                found=self.is_match(non_empty,article,rule,match_rule,from_string,subj_string,msgid_string,ref_string,body_string)
                if found:
                    self.art_db.insertArticle(name,article)
                    if not article.is_read:
                        unread_number=unread_number+1
        total,unread_number=self.art_db.getArticlesNumbers(name)
        #self.main_win.groups_pane.show_list([("global.search.results",str(unread_number)+" ("+str(total)+")"),],True)
        self.main_win.groups_pane.model.append((name,str(unread_number)+" ("+str(total)+")",False))
        self.main_win.threads_pane.clear()
        self.main_win.article_pane.clear()



    def __init__(self,main_win):
        self.wdir=get_wdir()
        self.art_db=main_win.art_db
        self.main_win=main_win
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Global Search"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(350,300)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/global_search.xpm"))
        

        vbox=gtk.VBox()
        vbox.set_border_width(8)
        label_from=gtk.Label(_("From"))
        label_from.set_use_markup(True)
        label_from.set_alignment(0,0.5)
        label_subject=gtk.Label(_("Subject"))
        label_subject.set_use_markup(True)
        label_subject.set_alignment(0,0.5)
        label_msgid=gtk.Label(_("Message-ID"))
        label_msgid.set_use_markup(True)
        label_msgid.set_alignment(0,0.5)
        label_ref=gtk.Label(_("References"))
        label_ref.set_use_markup(True)
        label_ref.set_alignment(0,0.5)
        label_body=gtk.Label(_("Body"))
        label_body.set_use_markup(True)
        label_body.set_alignment(0,0.5)
        self.entry_from=gtk.Entry()
        self.entry_subject=gtk.Entry()
        self.entry_msgid=gtk.Entry()
        self.entry_ref=gtk.Entry()
        self.entry_body=gtk.Entry()
        fields_label=gtk.Label("<b>"+_("Fields")+"</b>")
        fields_label.set_alignment(0,0.5)
        fields_label.set_use_markup(True)
        fields_vbox=gtk.VBox()
        fields_vbox.set_border_width(4)
        fields_vbox.pack_start(fields_label,False,False,4)
        find_table=gtk.Table(6,2,False)
        find_table.set_border_width(4)


        find_table.attach(label_from,0,1,0,1,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_subject,0,1,1,2,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_msgid,0,1,2,3,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_ref,0,1,4,5,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(label_body,0,1,5,6,gtk.FILL,gtk.FILL,16,4)
        find_table.attach(self.entry_from,1,2,0,1,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_subject,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_msgid,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_ref,1,2,4,5,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)
        find_table.attach(self.entry_body,1,2,5,6,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,0,4)

        fields_vbox.pack_start(find_table,True,True,4)
        vbox.pack_start(fields_vbox,True,False,2)

        rule_table=gtk.Table(3,1,False)
        rule_table.set_border_width(4)
        hbox=gtk.HBox()
        self.checkbutton_regex=gtk.CheckButton(_("Use Regular Expression"))
        self.checkbutton_case=gtk.CheckButton(_("Case Insensitive"))

        label=gtk.Label(_("Rule used to combine search results"))
        self.opt_menu=gtk.combo_box_new_text()
        self.opt_menu.append_text(_("AND"))
        self.opt_menu.append_text(_("OR"))
        self.opt_menu.set_active(0)

        rule_table.attach(self.checkbutton_regex,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        rule_table.attach(self.checkbutton_case,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        hbox.pack_start(self.opt_menu,False,True,2)
        hbox.pack_start(label,False,True)
        rule_table.attach(hbox,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,4)
        rule_label=gtk.Label("<b>"+_("Rules")+"</b>")
        rule_label.set_alignment(0,0.5)
        rule_label.set_use_markup(True)
        rule_vbox=gtk.VBox()
        rule_vbox.pack_start(rule_label,False,False,4)
        rule_vbox.set_border_width(4)
        rule_vbox.pack_start(rule_table,True,True,4)
        vbox.pack_start(rule_vbox,True,True,4)

        hbox_buttons=gtk.HBox()
        hbox_buttons.set_border_width(8)
        self.button_close=gtk.Button(None,gtk.STOCK_CLOSE)
        self.button_close.connect("clicked",self.destroy)
        self.button_next=gtk.Button(None,gtk.STOCK_FIND)
        self.button_next.connect("clicked",self.next_match)
        hbox_buttons.pack_start(self.button_close,True,True,2)
        hbox_buttons.pack_start(self.button_next,True,True,2)
        vbox.pack_start(hbox_buttons,True,False,6)
        self.window.add(vbox)
