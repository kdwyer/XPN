import gtk
import pango
import sys
import time
import smtplib
import cPickle
import os
import re
import ConfigParser
from email.Utils import formatdate, parseaddr
from random import randint,seed
from locale import getdefaultlocale
from xpn_src.Article import Mail_To_Send
from xpn_src.Dialogs import Dialog_YES_NO, Dialog_OK
from xpn_src.Charset_List import encodings_list, guess_list, encodings_tip, load_ordered_list
from xpn_src.Connections_Handler import SMTPConnection
from xpn_src.UserDir import get_wdir
from xpn_src.KeyBindings import load_shortcuts

ui_string="""<ui>
    <menubar name='EditMenuBar'>
        <menu action="Article">
            <menuitem action='send' />
            <menuitem action='send_later' />
            <menuitem action='save_draft' />
            <separator />
            <menuitem action='rot13' />
            <menuitem action='spoiler' />
            <separator />
            <menuitem action='editor' />
            <separator />
            <menuitem action='discard' />
            
        </menu>
    </menubar>
    <toolbar name='EditToolBar'>
        <toolitem action='send' />
        <toolitem action='send_later' />
        <toolitem action='save_draft' />
        <separator />
        <toolitem action='rot13' />
        <toolitem action='spoiler' />
        <toolitem action='editor' />
        <separator />
        <toolitem action='discard' />
        
    </toolbar>
</ui>"""

class Edit_Mail_Win:
    def show(self):
        self.win.show_all()
        #setting the focus
        self.textview.grab_focus()

    def delete_event(self,widget,event,data=None):
        self.editwin_width,self.editwin_height=self.win.get_size()
        self.save_sizes()
        return False

    def destroy(self,obj):
        self.buffer.disconnect(self.mark_set_handler)
        self.save_sizes()        
        self.win.destroy()
        if self.outboxManager: self.outboxManager.populateFolderTree()

    def guess_encoding(self,text):
        for best_enc in guess_list:
            try:
                unicode(text,best_enc,"strict")
            except:
                pass
            else:
                break
        return best_enc

    def external_editor(self,obj,command):
        body=""
        bounds=self.buffer.get_bounds()
        if bounds:
            start,stop=bounds
            body=self.buffer.get_text(start,stop,True).decode("utf-8")
            self.buffer.delete(start,stop)
        try:
            system_enc=getdefaultlocale()[1]
            body=body.encode(system_enc,"replace")
        except:
            body=body.encode(self.fallback_charset,"replace")
        filename=(os.path.join(self.wdir,"temp_article.txt"))
        f=open(filename,"w")
        f.write(body)
        f.close()

        command=command.replace("%s",filename)
        result=os.system(command)
        if result==0:
            f=open(filename,"r")
            body=f.read().split("\n")
            f.close()
            os.remove(filename)
            best_enc=self.guess_encoding("".join(body))
            body=[unicode(line,best_enc,"strict") for line in body]
            self.show_article(body)
        else:
            self.statusbar.push(1,_("Error while opening external editor"))

    def update_to_name_entry(self,value):
        to_name=value
        self.to_name_entry.set_text(to_name.encode("utf-8"))


    def update_subject_entry(self,subj):
        if subj[0:3].lower()!="re:":
            subj="Re: "+subj
        self.subj_entry.set_text(subj.encode("utf-8"))

    def update_references(self,article_references):
        mom=article_references.split()
        article_references=" ".join(mom)  #in this way I removed FWSP tabs
        if len(mom)>21:
            #The number of References is greater than 21
            for i in range(0,len(mom)-21):
                mom.remove(mom[1])
            refs=""
            for i in range(len(mom)):
                refs=refs+mom[i]+" "
            article_references=refs.strip()

        refs_len=len(article_references)
        if refs_len>980:
            #References plus "References: " excedes 998 octets
            mom=article_references.split()
            while refs_len>980:
                mom_len=len(mom[1])
                mom.remove(mom[1])
                refs_len=refs_len-mom_len
            refs=""
            for i in range(len(mom)):
                refs=refs+mom[i]+" "
            article_references=refs.strip()
        article_references=article_references.strip()
        return article_references

    def wrap_line(self,string_to_wrap,wrap=73):
        split_string=string_to_wrap.split()
        new_line=""
        lines=[]
        for word in split_string:
            if len(new_line)+len(word)+1<wrap:
                new_line=new_line+word+" "
            else:
                lines.append(new_line.strip())
                new_line=word+" "
        lines.append(new_line.strip())
        return lines

    def add_attribution_line(self,art):
        attribution_line=self.cp_id.get(self.id_name,"attribution").replace("%n",art.nick).replace("%e",art.email).replace("%f",art.from_name).replace("%d",art.date_parsed).replace("%g",art.ngroups).replace("%s",art.subj)
        line_splitted=self.wrap_line(attribution_line)
        self.attr_line_splitted=line_splitted #I need this line when I count new text lines in article
        for line in line_splitted:
            self.insert(line+"\n")
        self.insert("\n")
        start,insert_point=self.buffer.get_bounds()
        self.buffer.create_mark("insert_point",insert_point,True)

    def update_body(self,article,selected_text):
        if selected_text==None:
            body=article.get_body()
        else:
            body=selected_text
        quoted_body=[]
        sign=0
        for line in body:
            if (len(line)==2 and line[0:2]=="--") or (len(line)==3 and line=="-- "):
                sign=1
            if sign!=1:
                if len(line)>0:
                    if line[0]!=">":
                        quoted_body.append("> "+line)
                    else:
                        quoted_body.append(">"+line)
                else:
                    quoted_body.append(">"+line)

        self.show_article(quoted_body)


    def tag_line(self):
        try:
            f=open(os.path.join(self.wdir,"tags.txt"),"r")
        except IOError:
            return _("tags.txt not found")
        else:
            list=f.readlines()
            f.close()
            seed()
            if len(list)>0:
                tag=list[randint(0,len(list)-1)]
                best_enc=self.guess_encoding(tag)
                tag=unicode(tag,best_enc)
                tag_wrapped=self.wrap_line(tag)
                tag=""
                for line in tag_wrapped:
                    tag=tag+line+"\n"
                return tag
            else:
                return "XPN :: http://xpn.altervista.org"

    def add_sign(self):
        sign=[]
        delimiter=False
        if self.cp_id.get(self.id_name,"sign")!="":
            try:
                sign_file=open(os.path.join(self.wdir,self.cp_id.get(self.id_name,"sign")),"r")
            except IOError:
                sign=_("Signature file not found")
                best_enc="utf-8"
            else:
                sign=sign_file.readlines()
                best_enc=self.guess_encoding("".join(sign))
                sign_file.close()
            self.insert_with_tags("\n-- \n","sign")
            delimiter=True
        use_tags=self.cp_id.get(self.id_name,"use_tags")
        if use_tags=="True":
            tag=self.tag_line()#unicode(self.tag_line(),"iso8859-1","replace")
            if delimiter==False:
                self.insert_with_tags("\n-- \n","sign")
            self.insert_with_tags(tag,"sign")
        for i in range(len(sign)):
            #self.insert_with_tags(unicode(sign[i],"iso8859-1","replace"),"sign")
            self.insert_with_tags(sign[i].decode(best_enc),"sign")


    def show_article(self,article):
        is_sign=False
        is_quote=False
        def quote_depth(line):
            count=0
            for char in line:
                if char==">":
                    count=count+1
                else:
                    break
            if count>3:
                count=3
            return str(count)
        for line in article:
            line=line.replace("\r","") #this is needed for some strange articles
            if len(line)>0:
                if line[0]==">":
                    is_quote=True
                elif (len(line)==2 and line[0:2]=="--") or (len(line)==3 and line[0:3]=="-- "):
                    is_sign=True
                    is_quote=False
                else:
                    is_quote=False
                if is_quote and not is_sign:
                    quote_level=quote_depth(line)
                    self.insert_with_tags(line,"quote"+quote_level)
                elif is_sign:
                    self.insert_with_tags(line,"sign")
                else:
                    self.insert_with_tags(line,"text")
            self.insert("\n")

    def set_text_color(self,color):
        text_color=gtk.gdk.color_parse(color)
        self.tag_table=self.buffer.get_tag_table()
        if not self.text_tag:
            self.text_tag=gtk.TextTag("text")
            self.tag_table.add(self.text_tag)
        self.text_tag.set_property("foreground-gdk",text_color)

    def set_quote_color(self,color,level):
        if level==1:
            quote1_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote1_tag:
                self.quote1_tag=gtk.TextTag("quote1")
                self.tag_table.add(self.quote1_tag)
            self.quote1_tag.set_property("foreground-gdk",quote1_color)

        elif level==2: 
            quote2_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote2_tag:
                self.quote2_tag=gtk.TextTag("quote2")
                self.tag_table.add(self.quote2_tag)
            self.quote2_tag.set_property("foreground-gdk",quote2_color)

        else:    
            quote3_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote3_tag:
                self.quote3_tag=gtk.TextTag("quote3")
                self.tag_table.add(self.quote3_tag)
            self.quote3_tag.set_property("foreground-gdk",quote3_color)

    def set_sign_color(self,color):
        sign_color=gtk.gdk.color_parse(color)
        self.tag_table=self.buffer.get_tag_table()
        if not self.sign_tag:
            self.sign_tag=gtk.TextTag("sign")
            self.tag_table.add(self.sign_tag)
        self.sign_tag.set_property("foreground-gdk",sign_color)


    def set_background(self,configs):
        color=configs["background_color"]
        color=gtk.gdk.color_parse(color)
        self.textview.modify_base(gtk.STATE_NORMAL,color)

    def set_foreground(self,configs):
        color=configs["text_color"]
        color=gtk.gdk.color_parse(color)
        self.textview.modify_text(gtk.STATE_NORMAL,color)

    def insert(self,string):
        mark=self.buffer.get_insert()
        iter=self.buffer.get_iter_at_mark(mark)
        self.buffer.insert(iter,string.encode("utf-8"))

    def insert_with_tags(self,string,tag):
        self.buffer.insert_with_tags_by_name(self.buffer.get_end_iter(),string.encode("utf-8"),tag)

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
        bounds=self.buffer.get_selection_bounds()
        if bounds:
            start=bounds[0]
            stop=bounds[1]
            text=self.buffer.get_text(start,stop,True).decode("utf-8")
            text_rotted=self.rot13(text)
            self.buffer.delete_selection(False,False)
            self.insert(text_rotted)

    def check_article(self,to_name,from_name,subject):
        """Checks if the article is wellformed.
        Performs checks on from_name, to_name, subject header fields and
        on the body.
        Returns two strings, errors, warnings
        """
        def check_from(from_name):
            nick,mail=parseaddr(from_name)
            if not nick and not mail: return _("* <b>From</b> field appears to be invalid\n")
            elif "@" not in mail: return _("* <b>From</b> field appears to be invalid\n")
            else: return ""
        
        def check_to(to_name):
            nick,mail=parseaddr(to_name)
            if not nick and not mail: return _("* <b>To</b> field appears to be invalid\n")
            elif "@" not in mail: return _("* <b>To</b> field appears to be invalid\n")
            else: return ""
                
        def check_body(body):
            quoted=0
            text=0
            total=len(body)
            if self.mode=="Normal":
                for attr_line in self.attr_line_splitted: 
                    if attr_line in body :body.remove(attr_line)
            for line in body:
                if line=="--" or line=="-- ": break
                elif line.startswith(">"): quoted=quoted+1
                elif line.strip()!="": text=text+1
                else: continue
            if text+quoted==0: return _("* <b>Article</b> seems to be empty\n"),""
            elif text==0: return _("* <b>Article</b> doesn't contain new text\n"),""
            elif quoted*100/float(quoted+text)>95: return "",_("* <b>Article</b> contains more than 95% of quoted text\n")
            else: return "",""
            
        errors=""
        warnings=""
        if not subject:
            errors=errors+_("* <b>Subject</b> field is empty\n")
        if not from_name:
            errors=warnings+_("* <b>From</b> field is empty\n")
        else:
            errors=errors+check_from(from_name)
        if not to_name:
            errors=warnings+_("* <b>To</b> field is empty\n")
        else:
            errors=errors+check_to(to_name)
        bounds=self.buffer.get_bounds()
        if bounds:
            start,stop=bounds
            text=self.buffer.get_text(start,stop,True).decode("utf-8")
            body=text.split("\n")
        else:
            body=[]
        body_errors,body_warnings=check_body(body)
        errors=errors+body_errors
        warnings=warnings+body_warnings
        return errors,warnings


    def send_article(self,obj,configs,send_later=False,isDraft=False):
        to_name=self.to_name_entry.get_text().decode("utf-8")
        from_name=self.from_entry.get_text().decode("utf-8")
        subject=self.subj_entry.get_text().decode("utf-8")
        date=formatdate(localtime=True)
        if not isDraft: errors,warnings=self.check_article(to_name,from_name,subject)
        else: errors,warnings=None,None
        if errors:
            message="<span size='large' weight='heavy'>"+_("Errors:")+"</span>\n\n"+errors
            if warnings:
                message=message+"\n\n<span size='large' weight='heavy'>"+_("Warnings:")+"</span>\n\n"+warnings
            dialog=Dialog_OK(message)
            do_send=False
        elif warnings:
            message="<span size='large' weight='heavy'>"+_("Warnings:")+"</span>\n\n"+warnings+_("\n\nDo you want to send the Article?")
            dialog=Dialog_YES_NO(message)
            do_send=dialog.resp
        else:
            do_send=True

        if do_send:
            references=self.references
            user_agent=self.VERSION
            output_charset=self.charset_combo.child.get_text()

            bounds=self.buffer.get_bounds()
            if bounds:
                start,stop=bounds
                text=self.buffer.get_text(start,stop,True).decode("utf-8")
                body=text.split("\n")
            else:
                body=[]
            mail_to_send=Mail_To_Send(to_name,from_name,date,subject,references,user_agent,output_charset,self.ordered_list,body)
            mail=mail_to_send.get_article()
            article_backup=dict() # this is needed for outbox/sent storing
            id_name=self.id_name
            for item in ["to_name","from_name","subject","references","user_agent","output_charset","body","date","id_name"]:
                article_backup[item]=eval(item)
                
            def _store_article(dirName,article_backup):
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
                    if self.pathToArticle and not self.isSent:
                        try: os.remove(os.path.join(self.wdir,self.pathToArticle))
                        except: pass
                    self.destroy(None)

            if send_later:
                if isDraft: outDir="draft"
                else: outDir="outbox"
                _store_article(os.path.join(self.wdir,outDir,"mail"),article_backup)
                    
            else:
                self.mailConnection=SMTPConnection(configs["smtp_server"],int(configs["smtp_port"]),configs["smtp_auth"],configs["smtp_username"],configs["smtp_password"])
                message,mailSent=self.mailConnection.sendMail(from_name,to_name,mail)
                if not mailSent:
                    self.statusbar.push(1,message)
                    self.mailConnection.closeConnection()
                else:
                    self.mailConnection.closeConnection()
                    _store_article(os.path.join(self.wdir,"sent","mail"),article_backup)
                
    def update_position_and_cset(self,arg1=None,arg2=None,arg4=None):
        #getting the position
        pos_mark=self.buffer.get_insert()
        pos=self.buffer.get_iter_at_mark(pos_mark)
        line_number=pos.get_line()
        chars=pos.get_line_offset()

        #getting the encoding
        bounds=self.buffer.get_bounds()
        start,stop=bounds
        text=self.buffer.get_text(start,stop,True).decode("utf-8")
        for best_enc in self.ordered_list:
            try:
                text.encode(best_enc,"strict")
            except:
                pass
            else:
                break
        self.row_col_label.set_text(_("row:%d, col:%d") % (int(line_number),int(chars)))
        self.best_charset_label.set_text(best_enc)
        self.charset_combo.child.set_text(best_enc)


    def wrap_on_change(self,obj):
        def get_line_from_buffer(iter_start,buffer):
            chars_in_line=iter_start.get_chars_in_line()-1
            if chars_in_line<0:
                chars_in_line=0
            iter_end=iter_start.copy()
            iter_end.set_line_offset(chars_in_line)
            line=buffer.get_text(iter_start,iter_end,True).decode("utf-8")
            return line,iter_end,chars_in_line
        wrap=int(self.cp_id.get(self.id_name,"wrap"))
        pos_mark=self.buffer.get_insert()
        start=self.buffer.get_start_iter()
        #pos is cursor position
        pos=self.buffer.get_iter_at_mark(pos_mark)
        line_number=pos.get_line()
        #start is the beginning of the line edited
        start.set_line(line_number)
        line,end_line,line_length=get_line_from_buffer(start,self.buffer)
        if (line_length>wrap) and (" " in line) and (not line.startswith(">")):
            pos_start=start.copy()
            #pos_start is equal to end_line-1
            pos_start.set_line_offset(wrap)
            char=self.buffer.get_text(pos_start,end_line,True).decode("utf-8")
            offset_before_wrap=self.buffer.get_iter_at_mark(self.buffer.get_insert()).get_offset()
            if char!=" ":
                success=False
                i=0
                pos_end=pos_start.copy()
                while not success and i<wrap:
                    pos_start.set_line_offset(wrap-i-1)
                    pos_end.set_line_offset(wrap-i)
                    char=self.buffer.get_text(pos_start,pos_end,True).decode("utf-8")
                    if char==" ":
                        success=True
                        word=self.buffer.get_text(pos_end,end_line,True).decode("utf-8")
                        new_line_start=start.copy()
                        line_numbers=self.buffer.get_line_count()
                        line_number=line_number+1
                        new_lines=[]
                        while line_number<line_numbers:
                            new_line_start.set_line(line_number)
                            new_line,new_line_end_iter,new_line_length=get_line_from_buffer(new_line_start,self.buffer)
                            if new_line and new_line!="-- " and not new_line.startswith(">"):
                                new_lines.append(new_line)
                                end_line=new_line_end_iter
                            else:
                                break
                            line_number=line_number+1
                        if new_lines:
                            new_lines[0]=word+" "+new_lines[0]
                            new_text=" ".join([line for line in new_lines])
                            new_text_wrapped="\n".join(self.wrap_line(new_text,wrap))
                            self.buffer.delete(pos_start,end_line)
                            self.buffer.insert(pos_start,"\n"+new_text_wrapped.encode("utf-8"))
                            iter_insert=self.buffer.get_iter_at_mark(self.buffer.get_insert())
                            iter_insert.set_offset(offset_before_wrap)
                            self.buffer.place_cursor(iter_insert)
                        else:
                            self.buffer.delete(pos_start,end_line)
                            self.buffer.insert(pos_start,"\n"+word.encode("utf-8"))
                    else:
                        i=i+1
            else:
                self.buffer.delete(pos_start,end_line)
                self.buffer.insert(pos_start,"\n")
        self.update_position_and_cset()


    def insert_spoiler_char(self,obj):
        pos_mark=self.buffer.get_insert()
        pos=self.buffer.get_iter_at_mark(pos_mark)
        self.buffer.insert(pos,chr(12))

    def clear_pane(self):
        start,end=self.buffer.get_bounds()
        self.buffer.delete(start,end)


    def save_sizes(self):
        try:
            f=open(os.path.join(self.wdir,"dats/sizes.dat"),"rb")
        except IOError:
            sizes={}        
        else:
            sizes=cPickle.load(f)
        if not self.editwin_width:
            sizes["editwin_width"],sizes["editwin_height"]=self.win.get_size()
        else:
            sizes["editwin_width"]=self.editwin_width
            sizes["editwin_height"]=self.editwin_height
        sizes["editwin_pos_x"],sizes["editwin_pos_y"]=self.win.get_position()
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
            editwin_width=sizes.get("editwin_width",None)
            editwin_height=sizes.get("editwin_height",None)
            if editwin_width and editwin_height:
                self.win.resize(int(editwin_width),int(editwin_height))
            else:
                self.win.maximize()
            editwin_pos_x=sizes.get("editwin_pos_x",None)
            editwin_pos_y=sizes.get("editwin_pos_y",None)
            if editwin_pos_x and editwin_pos_y:
                self.win.move(int(editwin_pos_x),int(editwin_pos_y))

    def create_ui(self,configs):
        self.ui = gtk.UIManager()
        accelgroup = self.ui.get_accel_group()
        actiongroup= gtk.ActionGroup("EditMailWindowActions")
        self.win.add_accel_group(accelgroup)
        ecuts=load_shortcuts("edit")
        actions=[("Article",None,_("_Article")),
                ("send","xpn_send",_("_Send Article"),ecuts["send"],_("Send Article"),self.send_article,configs),
                ("send_later","xpn_send_queue",_("Send Article _Later"),ecuts["send_later"],_("Send Article Later"),self.send_article,configs,True),
                ("save_draft",gtk.STOCK_SAVE,_("Save Article as Draft"),ecuts["save_draft"],_("Save Article as Draft"),self.send_article,configs,True,True),
                ("discard","xpn_discard",_("_Discard Article"),ecuts["discard"],_("Discard Article"),self.destroy),
                ("rot13","xpn_rot13",_("_ROT13 Selected Text"),ecuts["rot13"],_("ROT13 Selected Text"),self.apply_rot13),
                ("editor","xpn_editor",_("Launch External _Editor"),ecuts["editor"],_("Launch External Editor"),self.external_editor,configs["editor_launcher"]),
                ("spoiler","xpn_spoiler_char",_("_Insert Spoiler Char"),ecuts["spoiler"],_("Insert Spoiler Char"),self.insert_spoiler_char)]

        for action in actions: 
            if len(action)<7:
                actiongroup.add_actions([action])
            else:
                actiongroup.add_actions([action[0:6]],action[6:])

        self.ui.insert_action_group(actiongroup,0)
        merge_id = self.ui.add_ui_from_string(ui_string)


    def load_id(self):
        nick=self.cp_id.get(self.id_name,"nick").encode("utf-8")
        email=self.cp_id.get(self.id_name,"email").encode("utf-8")
        
        if self.cp_id.get(self.id_name,"use_mail_from")=="True":             
            nick=self.cp_id.get(self.id_name,"mail_nick").encode("utf-8")
            if not nick:
                nick=self.cp_id.get(self.id_name,"nick").encode("utf-8")            
            email=self.cp_id.get(self.id_name,"mail_email").encode("utf-8")
            if not email:
                email=self.cp_id.get(self.id_name,"email").encode("utf-8")            
        else:
            nick=self.cp_id.get(self.id_name,"nick").encode("utf-8")
            email=self.cp_id.get(self.id_name,"email").encode("utf-8")
        nick=nick+" <"+email+">"        
        self.from_entry.set_text(nick)
        
    def id_changed(self,obj,art):
        self.id_name=self.id_combo.get_active_text()
        self.load_id()
        start,end=self.buffer.get_bounds()
        body=self.buffer.get_text(start,end,True).decode("utf-8").split("\n")
        found=False
        #removing old sign
        i=0
        for line in reversed(body):
            i=i+1
            if line=="-- ":
                found=True
                break
        for x in range(i): body.pop()
        if not found: body=self.buffer.get_text(start,end,True).decode("utf-8").split("\n")
        #removing old sign
        
        
        found= False
        i=0
        #removing old attribution line
        old_body=body[:]
        for line in body:
            if line==self.attr_line_splitted[-1]:
                found=True
                i=i+1
                break
            i=i+1
        for x in range(i): body.pop(0)
        if body[0]=="": body.pop(0) 
        if not found: body=old_body
        start,end=self.buffer.get_bounds()
        self.buffer.delete(start,end)
        self.add_attribution_line(art)

        self.show_article(body)

        self.add_sign()




    def __init__(self,configs,to_name,article,selected_text,mode="Normal",draft_article=None,pathToArticle="",outboxManager=None,isSent=False,id_name=""):
        self.pathToArticle=pathToArticle
        self.mode=mode
        self.outboxManager=outboxManager
        self.isSent=isSent
        self.id_name=id_name.encode("utf-8")



        self.wdir=get_wdir()

        self.fallback_charset=configs["fallback_charset"]
        
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("Edit Mail"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/reply.xpm"))

        #main_vbox
        main_vbox=gtk.VBox()
        self.win.add(main_vbox)

        self.create_ui(configs)
        menubar=self.ui.get_widget("/EditMenuBar")
        main_vbox.pack_start(menubar,False,True,0)
        menubar.show()

        toolbar=self.ui.get_widget("/EditToolBar")
        main_vbox.pack_start(toolbar,False,True,0)
        toolbar.show()
        #toolbar.set_icon_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_style(gtk.SHADOW_NONE)


        id_label=gtk.Label("<b>"+_("Identity")+"</b>")
        id_label.set_alignment(0,0.5)
        id_label.set_use_markup(True)
        id_hbox=gtk.HBox()
        self.id_combo=gtk.combo_box_new_text()
        self.cp_id=ConfigParser.ConfigParser()
        self.cp_id.read(os.path.join(get_wdir(),"dats","id.txt"))
        positions=dict()
        i=0
        for id in self.cp_id.sections(): 
            self.id_combo.append_text(id)
            positions[id]=i
            i=i+1

        if self.id_name: self.id_combo.set_active(positions[self.id_name])
        else: 
            self.id_combo.set_active(0)
            self.id_name=self.id_combo.get_active_text()
        
        id_sep=gtk.VSeparator()
        id_hbox.pack_start(id_label,False,True,4)
        id_hbox.pack_start(self.id_combo,False,True,4)
        id_hbox.pack_start(id_sep,False,False,4)
        main_vbox.pack_start(id_hbox,False,True,2)

        self.headers_table=gtk.Table(3,2,False)
        self.headers_table.set_border_width(2)
        self.to_name_label=gtk.Label("<b>"+_("To : ")+"</b>")
        self.to_name_label.set_use_markup(True)
        self.to_name_label.set_alignment(1,0.5)
        self.from_label=gtk.Label("<b>"+_("From : ")+"</b>")
        self.from_label.set_use_markup(True)
        self.from_label.set_alignment(1,0.5)
        self.subj_label=gtk.Label("<b>"+_("Subject : ")+"</b>")
        self.subj_label.set_use_markup(True)
        self.subj_label.set_alignment(1,0.5)
        self.charset_label=gtk.Label("<b>"+_("Charset : ")+"</b>")
        self.charset_label.set_use_markup(True)
        self.charset_label.set_alignment(1,0.5)

        self.to_name_entry=gtk.Entry()
        self.from_entry=gtk.Entry()
        self.subj_entry=gtk.Entry()
        self.charset_combo=gtk.combo_box_entry_new_text()
        for encoding in encodings_list:
            self.charset_combo.append_text(encoding)
        self.charset_tooltip=gtk.Tooltips()
        self.charset_tooltip.set_tip(self.charset_combo.child,encodings_tip) 

        self.charset_combo.child.set_editable(False)


        self.headers_table.attach(self.to_name_label,0,1,0,1,gtk.FILL,gtk.FILL)
        self.headers_table.attach(self.from_label,0,1,1,2,gtk.FILL,gtk.FILL)
        self.headers_table.attach(self.subj_label,0,1,2,3,gtk.FILL,gtk.FILL)
        self.headers_table.attach(self.to_name_entry,1,2,0,1)
        self.headers_table.attach(self.from_entry,1,2,1,2)
        self.headers_table.attach(self.subj_entry,1,2,2,3)
        self.headers_table.attach(self.charset_label,0,1,3,4,gtk.FILL,gtk.FILL)
        self.headers_table.attach(self.charset_combo,1,2,3,4)



        #buffer
        self.buffer=gtk.TextBuffer()

        self.quote1_tag=None
        self.quote2_tag=None
        self.quote3_tag=None
        self.sign_tag=None
        self.text_tag=None
        color=configs["text_color"]
        self.set_text_color(color)
        color=configs["quote1_color"]
        self.set_quote_color(color,1)
        color=configs["quote2_color"]
        self.set_quote_color(color,2)
        color=configs["quote3_color"]
        self.set_quote_color(color,3)
        color=configs["sign_color"]
        self.set_sign_color(color)

        #TextView
        text_scrolledwin=gtk.ScrolledWindow()
        text_scrolledwin.set_border_width(2)
        text_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        text_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.textview=gtk.TextView(self.buffer)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textview.set_indent(4)
        text_scrolledwin.add(self.textview)

        self.text_vbox=gtk.VBox()
        self.text_vbox.pack_start(self.headers_table,False,False)
        self.text_vbox.pack_start(text_scrolledwin,True,True)


        main_vbox.pack_start(self.text_vbox,True,True,0)

        #statusbar
        statusbar_hbox=gtk.HBox()
        statusbar_hbox.set_border_width(2)
        self.row_col_label=gtk.Label()
        vsep=gtk.VSeparator()
        vsep2=gtk.VSeparator()
        self.best_charset_label=gtk.Label()
        self.statusbar=gtk.Statusbar()
        statusbar_hbox.pack_start(self.row_col_label,False,True,2)
        statusbar_hbox.pack_start(vsep,False,False,2)
        statusbar_hbox.pack_start(self.best_charset_label,False,True,2)
        statusbar_hbox.pack_start(vsep2,False,False,2)
        statusbar_hbox.pack_start(self.statusbar,True,True,2)
        main_vbox.pack_start(statusbar_hbox,False,False,0)

        #some updates
        self.ordered_list=load_ordered_list()
        self.references=""
        self.update_to_name_entry(to_name)
        self.mark_set_handler=self.buffer.connect("mark_set",self.update_position_and_cset)
        if mode=="Normal":
            self.update_subject_entry(article.subj)
            self.references=self.update_references(article.ref+" "+article.msgid)
            self.add_attribution_line(article)
            self.update_body(article,selected_text)
            start,insert_point=self.buffer.get_bounds()
            self.buffer.create_mark("insert_point_after_text",insert_point,True)
            self.add_sign()
            self.buffer.connect("changed",self.wrap_on_change)
            if selected_text==None:
                insert_pos=self.buffer.get_iter_at_mark(self.buffer.get_mark("insert_point"))
            else:
                insert_pos=self.buffer.get_iter_at_mark(self.buffer.get_mark("insert_point_after_text"))
            self.buffer.place_cursor(insert_pos)
        if mode=="Draft":
            self.from_entry.set_text(draft_article.get("from_name","").encode("utf-8"))
            self.subj_entry.set_text(draft_article.get("subject","").encode("utf-8"))
            self.clear_pane()
            self.show_article([line.encode("utf-8") for line in draft_article.get("body","")])
            self.references=self.update_references(draft_article.get("references",""))
             

    
        self.set_background(configs)
        self.set_foreground(configs)
        self.update_position_and_cset()
        if configs["external_editor"]=="True":
            self.external_editor(None,configs["editor_launcher"])
        self.set_sizes()
        self.editwin_width=None
        self.editwin_height=None
        self.textview.modify_font(pango.FontDescription(configs["font_name"]))
        self.load_id()
        self.id_combo.connect("changed",self.id_changed,article)
        
