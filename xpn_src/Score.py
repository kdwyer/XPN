import time
import re
import gtk
import gobject
import pango
import cPickle
import os
from email.Utils import parsedate_tz, mktime_tz
from xpn_src.Article import Article
from xpn_src.Dialogs import Dialog_OK
from xpn_src.UserDir import get_wdir


try:
    set()
except:
    from sets import Set as set


def escape(data):
    """Escape &, <, and > in a string of data.
    """

    # must do ampersand first
    data = data.replace("&", "&amp;")
    data = data.replace(">", "&gt;")
    data = data.replace("<", "&lt;")
    return data


class Score_Rules:
    def valid_re(self,regex):
        try :
            re.compile(regex)
        except:
            return False
        else:
            return True

    def match_is_valid(self,match,header):
        interval_re=re.compile(r"\[\d+,\d+\]")
        header_is_string=lambda header: header.lower() in ("from","subject","date","message-id","references","xref")
        header_is_number=lambda header: header.lower() in ("age","lines","bytes","xpost","score")

        #match is a string case insensitive
        match_is_string_c_ins=lambda match: (match[0]=="\"" and match[-1]=="\"") or \
                                            (match[0]=="{" and match[-1]=="}" and self.valid_re(match[1:]))
        #match is a string case sensitive:
        match_is_string_c_sens=lambda match: match[0].lower()=="c" and ((match[1]=="\"" and match[-1]=="\"") or \
                                            (match[1]=="{" and match[-1]=="}" and self.valid_re(match[2:])))
        #match is a inverted string case insensitive:
        match_is_string_c_ins_neg=lambda match: match[0]=="~" and match_is_string_c_ins(match[1:])
        #match is a inverted string case sensitive:
        match_is_string_c_sens_neg=lambda match: match[0]=="~" and match_is_string_c_sens(match[1:])

        #match is a string:
        match_is_string = lambda match: match_is_string_c_ins_neg(match) or match_is_string_c_sens_neg(match) or\
                                        match_is_string_c_ins(match) or match_is_string_c_sens(match)
                                        
        match_is_numb=lambda match: (match[0]=="%" and ( ((match[1]==">" or match[1]=="<" or match[1]=="=") and \
                                       (match[2:].isdigit() or (match[2]=="-" and match[3:].isdigit()))) or \
                                       (match[1]=="[" and interval_re.search(match[1:])) ))
        match_is_numb_neg= lambda match: match[0]=="~" and match_is_numb(match[1:])

        #match is a number:
        match_is_number = lambda match: match_is_numb(match) or match_is_numb_neg(match)


        if len(match)>2:
            if (header_is_string(header) and (match_is_string(match))) or \
               (header_is_number(header) and (match_is_number(match))):
                return True
            else:
                return False
        else:
            return False

    def score_mod_is_valid(self,score_mod):
        if score_mod[0]=="=":
            if (score_mod[1]=="+" or score_mod[1]=="-"):
                return score_mod[2:].isdigit()
            else:
                return False
        if score_mod[0]=="+" or score_mod[0]=="-":
            return score_mod[1:].isdigit()
        else:
            if score_mod[1:].startswith("setcolor"):
                regex=re.compile("(^setcolor)\((([a-z]+)|(#\w+));(([a-z]+)|(#\w+))\)")
                match=regex.match(score_mod[1:])
                if match:
                    if (match.groups()[0] and match.groups()[1] and match.groups()[4]):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return score_mod[1:] in self.actions
           
           
    def header_is_valid(self,header,score_mod):
        if score_mod[0]=="!":
            return header in self.action_headers
        else:
            return header in self.headers

    def scan_for_rule(self,line):
        scope_number=len(self.group_scope_list)-1
        ind1=line.find(" ")
        score_mod=""
        header=""
        match=""
        if ind1!=-1:
            score_mod=line[:ind1].strip().lower()
            line2=line[ind1+1:]
            ind2=line2.strip().find(" ")
            if ind2!=-1:
                header=line2.strip()[:ind2].strip().lower()
                match=line2.strip()[ind2+1:].strip()
        if not self.score_mod_is_valid(score_mod):
            if score_mod[0]=="!":
                self.errors.append("<b>"+_("Syntax Error: Unknown Action on line:: ")+"</b>\n%s\n" % (escape(line),))
            else:
                self.errors.append("<b>"+_("Syntax Error: Bad Score Modifier on line:: ")+"</b>\n%s\n" % (escape(line),))
        elif not self.header_is_valid(header,score_mod):
            self.errors.append("<b>"+_("Syntax Error: Unknown Header Name on line:: ")+"</b>\n%s\n" % (escape(line),))
        elif not self.match_is_valid(match,header):
            self.errors.append("<b>"+_("Syntax Error: Bad Match Rule on line:: ")+"</b>\n%s\n" % (escape(line),))

        else:
            self.group_rules_list[scope_number].append({"score_mod":score_mod,"header":header,"match":match})

    def scan_for_block(self,line):
        scope=line[1:-1].strip()
        groups=[]
        if scope!="":
            if scope=="*":
                groups="*"
            else:
                groups=scope.split(" ")
            self.raw_scopes.append(line)
        return groups

    def load_file(self):
        "Score file parser"
        try:
            f=open(os.path.join(self.wdir,"scores.txt"),"r")
        except IOError:
            lines=[]
        else:
            lines=f.readlines()
            lines=[line.strip("\n").decode("utf-8") for line in lines]
            f.close()
        return lines

    def load_rules(self,lines):
        self.raw_file="\n".join(lines)
        self.group_scope_list=[]
        self.group_rules_list=[]
        self.errors=[]
        self.raw_scopes=[]

        current_group_scope=[]
        for line in lines:
            line=line.strip()
            if line!="":
                if line[0]!="#":
                    #It's not empty nor a comment
                    if line[0]=="[" and line[-1]=="]":
                        #This is the group scope
                        current_group_scope=self.scan_for_block(line)
                        self.group_scope_list.append(current_group_scope)
                        self.group_rules_list.append([])

                    elif line[0]=="+" or line[0]=="-" or line[0]=="=" or line[0]=="!":
                        #This is a rule
                        if current_group_scope:
                            self.scan_for_rule(line)
                        else:
                            self.errors.append("<b>"+_("Syntax Error: Missing scope for line :: ")+"</b>\n%s\n" % (escape(line),))
                    else:
                        self.errors.append("<b>"+_("Syntax Error: Bad Line:: ")+"</b>\n%s\n" % (escape(line),))

    def build_match_rule(self,match):
        def build_plain_match_rule(match,index=1):
            """ Builds the match rule without the inverter information,
                index point to the start of the match (i.e. without the ~)"""
            if match[0].lower()=="c":
                #case sensitive
                if match[1]=="{":
                    #regular expression
                    match_rule=lambda field,regex: bool(re.compile(regex[index+1:-1],re.UNICODE).search(field))
                else:
                    #normal match
                    match_rule=lambda field,word: bool(field.find(word[index+1:-1])+1)
            elif match[0].lower()!="%":
                #case sensitive
                if match[0]=="{":
                    #regular expression
                    match_rule=lambda field,regex: bool(re.compile(regex[index:-1],re.UNICODE|re.IGNORECASE).search(field))
                else:
                    #normal match
                    match_rule=lambda field,word: bool(field.lower().find(word[index:-1].lower())+1)
            else:
                #numeric rule
                if match[1]==">":
                    match_rule=lambda field,num: field>int(num[index+1:])
                elif match[1]=="<":
                    match_rule=lambda field,num: field<int(num[index+1:])
                elif match[1]=="=":
                    match_rule=lambda field,num: field==int(num[index+1:])
                else:
                    match_rule=lambda field,interval: field in range(int(interval[index+1:-1].split(",")[0]),int(interval[index+1:-1].split(",")[1])+1)
            return match_rule

        if match[0]=="~":
            #inverted rule
                plain_match_rule=build_plain_match_rule(match[1:])
                return lambda field,match: not plain_match_rule(field,match[1:])

        else:
            #not inverted rule
                plain_match_rule=build_plain_match_rule(match)
                return lambda field,match: plain_match_rule(field,match)
            

    def apply_score_rules(self,xpn_article,group):
        score=xpn_article.get_score()
        i=0
        time_now=mktime_tz(parsedate_tz(time.ctime()))
        age=(time_now-xpn_article.secs)/(24.0*60*60)

        #compatibility check
        try: xpn_article.xref
        except AttributeError: xpn_article.xref=""
        try: xpn_article.bytes
        except AttributeError: xpn_article.bytes=0
        try: xpn_article.lines
        except AttributeError: xpn_article.lines=0

        xpost=xpn_article.xref.count(":")

        fields={"subject":xpn_article.subj,"from":xpn_article.from_name,"date":xpn_article.date,
                "message-id":xpn_article.msgid,"references":xpn_article.ref,"age":age,"xref":xpn_article.xref,
                "bytes":xpn_article.bytes,"lines":xpn_article.lines,"xpost":xpost}

        for group_scope in self.group_scope_list:
            if group_scope=="*" or (group in group_scope):
                #current group is in this scope
                for rule in self.group_rules_list[i]:
                    #let's apply rule
                    score_mod=rule["score_mod"]
                    if score_mod[0]=="!":
                        #this is an action
                        continue
                    match_rule=self.build_match_rule(rule["match"])
                    if match_rule(fields[rule["header"]],rule["match"]):
                        score_mod=rule["score_mod"]
                        if score_mod[0]=="=":
                            score=int(score_mod[1:])
                            if score>9999: score=9999
                            if score<-9999: score=-9999
                            return score
                        else:
                            score=score+int(score_mod)
            i=i+1
        if score>9999: score=9999
        if score<-9999: score=-9999
        return score

    def apply_action_rules(self,xpn_article,group):
        score=xpn_article.get_score()
        i=0
        time_now=mktime_tz(parsedate_tz(time.ctime()))
        age=(time_now-xpn_article.secs)/(24.0*60*60)

        #compatibility check
        #there is no need here, it's has been already performed in apply_score_rules
        
        xpost=xpn_article.xref.count(":")

        fields={"subject":xpn_article.subj,"from":xpn_article.from_name,"date":xpn_article.date,
                "message-id":xpn_article.msgid,"references":xpn_article.ref,"age":age,"xref":xpn_article.xref,
                "bytes":xpn_article.bytes,"lines":xpn_article.lines,"xpost":xpost,"score":score}
        
        actions=[]
        for group_scope in self.group_scope_list:
            if group_scope=="*" or (group in group_scope):
                #current group is in this scope
                for rule in self.group_rules_list[i]:
                    #let's apply rule
                    match_rule=self.build_match_rule(rule["match"])
                    if match_rule(fields[rule["header"]],rule["match"]):
                        action=rule["score_mod"]
                        if action[0]=="!":
                            #this is an action
                            if action[1:]=="kill":
                                #xpn_article=None
                                pass #need this to let reapply_rules work
                            elif action[1:]=="markread":
                                xpn_article.is_read=True
                            elif action[1:]=="markunread":
                                xpn_article.is_read=False
                            elif action[1:]=="mark":
                                xpn_article.marked_for_download=True
                            elif action[1:]=="unmark":
                                xpn_article.marked_for_download=False                                
                            elif action[1:]=="keep":
                                xpn_article.keep=True
                            elif action[1:]=="unkeep":
                                xpn_article.keep=False
                            elif action[1:]=="watch":
                                xpn_article.watch=True
                                xpn_article.ignore=False
                            elif action[1:]=="ignore":
                                xpn_article.watch=False
                                xpn_article.ignore=True
                                xpn_article.is_read=True
                            elif action[1:]=="unsetwatchignore":
                                xpn_article.watch=False
                                xpn_article.ignore=False
                            elif action[1:].startswith("setcolor"):
                                regex=re.compile("(^setcolor)\((([a-z]+)|(#\w+));(([a-z]+)|(#\w+))\)")
                                matches=regex.match(action[1:])
                                xpn_article.fg_color=str(matches.groups()[1])
                                xpn_article.bg_color=str(matches.groups()[4])
                            actions.append(action[1:])
            i=i+1
        return xpn_article,actions
       
    
    def __init__(self):
        self.wdir=get_wdir()
        self.headers=["from","subject","date","message-id","references","age","xref","xpost","bytes","lines"]
        self.action_headers=["from","subject","date","message-id","references","age","xref","xpost","bytes","lines","score"]
        self.actions=["kill","markread","markunread","mark","unmark","retrieve","keep","unkeep","watch","ignore","unsetwatchignore","setcolor"]
        self.group_scope_list=[]
        self.group_rules_list=[]
        self.errors=[]
        self.raw_file=""
        self.raw_scopes=[]
        self.lines=self.load_file()
        self.load_rules(self.lines)

class Rules_Tree:
    def get_widget(self):
        return self.scrolledwin

    def insert(self,iter_parent,iter_sibling,values):
        iter=self.model.insert_before(iter_parent,iter_sibling)
        for i in range(len(values)):
            if i<3:
                value=values[i].encode("utf-8")
            else:
                value=values[i]
            self.model.set_value(iter,i,value)
        return iter

    def __init__(self):
        self.scrolledwin=gtk.ScrolledWindow()
        self.scrolledwin.set_border_width(4)
        self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.rules_tree=gtk.TreeView()
        self.rules_tree.set_border_width(4)
        self.model=gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_INT)
        text_renderer_scope=gtk.CellRendererText()
        text_renderer_scope.set_property("weight",1000)
        text_renderer=gtk.CellRendererText()

        self.column1=gtk.TreeViewColumn(_("Scope/Score Mod"),text_renderer_scope,text=0,weight=3)
        self.column2=gtk.TreeViewColumn(_("Header"),text_renderer,text=1)
        self.column3=gtk.TreeViewColumn(_("Match Rule"),text_renderer,text=2)
        self.rules_tree.append_column(self.column1)
        self.rules_tree.append_column(self.column2)
        self.rules_tree.append_column(self.column3)
        self.scrolledwin.add(self.rules_tree)
        self.rules_tree.set_model(self.model)

class Score_Win:
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,widget):
        lines=self.score_rules.load_file()
        self.score_rules.load_rules(lines)
        self.window.destroy()

    def show(self):
        self.window.show_all()
        self.match_value2_entry.hide()
        self.match_value2_label.hide()
        self.match_value_label.hide()
        self.action_match_value2_entry.hide()
        self.action_match_value2_label.hide()
        self.action_match_value_label.hide()
        self.color1_entry.hide()
        self.color1_button.hide()
        self.color1_label.hide()
        self.color2_entry.hide()
        self.color2_button.hide()
        self.color2_label.hide()

    def show_rules(self):
        self.rules_tree.model.clear()
        iter_scope=None
        group_scope_list=self.score_rules.group_scope_list
        group_rules_list=self.score_rules.group_rules_list
        for i in range(len(group_scope_list)):
            if group_scope_list[i]=="*":
                scope="[*]"
            else:
                scope="[ "+",\n".join(group_scope_list[i])+" ]"
            iter_scope=self.rules_tree.insert(None,None,[str(scope),"","",pango.WEIGHT_BOLD])
            for rule in group_rules_list[i]:
                self.rules_tree.insert(iter_scope,None,[rule["score_mod"],rule["header"],rule["match"],pango.WEIGHT_NORMAL])

    def show_errors(self,obj):
        errors="\n".join(self.score_rules.errors)
        if errors:
            self.dialog=Dialog_OK(errors.encode("utf-8"))
        else:
            self.dialog=Dialog_OK(_("No Errors"))

    def close_window(self,obj):
        start,stop=self.file_buffer.get_bounds()
        text=self.file_buffer.get_text(start,stop,True)
        f=open(os.path.join(self.wdir,"scores.txt"),"w")
        f.write(text)
        f.close()
        self.window.destroy()

    def rescan_rules(self,obj):
        start,stop=self.file_buffer.get_bounds()
        lines=self.file_buffer.get_text(start,stop,True).decode("utf-8").split("\n")
        self.score_rules.load_rules(lines)
        self.score_rules.lines=lines
        self.show_rules()
        subscribed=self.art_db.getSubscribed()
        subscribed=["["+subscribed[i][0]+"]" for i in range(len(subscribed))]
        popdown=self.score_rules.raw_scopes
        for item in subscribed:
            if item not in popdown:
                popdown.append(item)
        if "[*]" not in popdown:
            popdown.insert(0,"[*]")
        model=self.scope_combo.get_model()
        model.clear()
        self.scope_combo.set_model(model)
        model=self.action_scope_combo.get_model()
        model.clear()
        self.action_scope_combo.set_model(model)
        for item in popdown:
            self.scope_combo.append_text(item)
            self.action_scope_combo.append_text(item)
        iter_first=self.scope_combo.get_model().get_iter_first()
        self.scope_combo.set_active_iter(iter_first)
        iter_first=self.action_scope_combo.get_model().get_iter_first()
        self.action_scope_combo.set_active_iter(iter_first)

    def add_new_rule(self,obj):
        scope=self.scope_combo.child.get_text().decode("utf-8")
        header=self.score_rules.headers[self.header_opt_menu.get_active()]
        match_type=self.match_type_opt_menu.get_active()
        match_type, match_type_inverted =match_type/2,match_type%2
        match_value=self.match_value_entry.get_text().decode("utf-8")
        case=self.case_checkbutton.get_active()
        action_type=self.score_mod_opt_menu.get_active()
        number=self.score_mod_spinbutton.get_value_as_int()
        if scope!="" and match_value!="":
            rule=[]
            if action_type==0 and number<0:
                number=repr(abs(number))
            elif action_type==1:
                number=repr(abs(number))
            elif action_type==2 and number>=0:
                number="+"+repr(number)
            else:
                number=repr(number)
            rule.append(["+","-","="][action_type]+number)
            rule.append(header.capitalize())
            if match_type==0:
                match_value="\""+match_value+"\""
            elif match_type==1:
                match_value="{"+match_value+"}"
            elif match_type==2:
                match_value="%>"+match_value
            elif match_type==3:
                match_value="%<"+match_value
            elif match_type==4:
                match_value="%="+match_value
            else:
                match_value2=self.match_value2_entry.get_text().decode("utf-8")
                match_value="%["+match_value+","+match_value2+"]"
            if (match_type in [0,1]) and case:
                match_value="c"+match_value
            if match_type_inverted:
                match_value="~"+match_value
            rule.append(match_value)
            rule=" ".join(rule)

            found_scope=False
            for i in range(len(self.score_rules.lines)):
                if scope==self.score_rules.lines[i]:
                    found_scope=True
                    break
            if found_scope==True:
                found_block_end=False
                for j in range(i,len(self.score_rules.lines)):
                    if self.score_rules.lines[j]=="":
                        found_block_end=True
                        break
                if found_block_end:
                    self.score_rules.lines.insert(j,rule)
                else:
                    self.score_rules.lines.insert(i+1,rule)
            if found_scope==False:
                self.score_rules.lines.append("")
                self.score_rules.lines.append(scope)
                self.score_rules.lines.append(rule)
                self.score_rules.lines.append("")
            self.file_buffer.set_text(("\n".join(self.score_rules.lines)).encode("utf-8"))
            self.rescan_rules(None)

    def add_new_action_rule(self,obj):
        scope=self.action_scope_combo.child.get_text().decode("utf-8")
        header=self.score_rules.action_headers[self.action_header_opt_menu.get_active()]
        action_match_type=self.action_match_type_opt_menu.get_active()
        action_match_type, action_match_type_inverted =action_match_type/2,action_match_type%2

        action_value=self.action_match_value_entry.get_text().decode("utf-8")
        case=self.action_case_checkbutton.get_active()
        #values=["Kill","Mark Read","Mark Unread","Mark for Download","UnMark for Download","Retrieve","Keep","UnKeep","Watch","Ignore","UnSetWatchIgnore"]
        action_type=self.action_type_opt_menu.get_active()
        if scope!="" and action_value!="":
            rule=[]
            if action_type!=11:
                rule.append(["!kill","!markread","!markunread","!mark","!unmark","!retrieve","!keep","!unkeep","!watch","!ignore","!unsetwatchignore"][action_type])
            else:
                color_fg=self.color1_entry.get_text().decode("utf-8")
                color_bg=self.color2_entry.get_text().decode("utf-8")
                if color_fg=="": color_fg="Default"
                if color_bg=="": color_bg="Default"
                rule.append("!setcolor(%s;%s)" % (color_fg,color_bg))
            rule.append(header.capitalize())
            if action_match_type==0:
                action_value="\""+action_value+"\""
            elif action_match_type==1:
                action_value="{"+action_value+"}"
            elif action_match_type==2:
                action_value="%>"+action_value
            elif action_match_type==3:
                action_value="%<"+action_value
            elif action_match_type==4:
                action_value="%="+action_value
            else:
                action_value2=self.action_match_value2_entry.get_text().decode("utf-8")
                action_value="%["+action_value+","+action_value2+"]"

            if (action_match_type in [0,1]) and case:
                action_value="c"+action_value
            if action_match_type_inverted:
                action_value="~"+action_value
            rule.append(action_value)
            rule=" ".join(rule)

            found_scope=False
            for i in range(len(self.score_rules.lines)):
                if scope==self.score_rules.lines[i]:
                    found_scope=True
                    break
            if found_scope==True:
                found_block_end=False
                for j in range(i,len(self.score_rules.lines)):
                    if self.score_rules.lines[j]=="":
                        found_block_end=True
                        break
                if found_block_end:
                    self.score_rules.lines.insert(j,rule)
                else:
                    self.score_rules.lines.insert(i+1,rule)
            if found_scope==False:
                self.score_rules.lines.append("")
                self.score_rules.lines.append(scope)
                self.score_rules.lines.append(rule)
                self.score_rules.lines.append("")
            self.file_buffer.set_text(("\n".join(self.score_rules.lines)).encode("utf-8"))
            self.rescan_rules(None)


        
    def test_re(self,obj):
        RE=self.re_entry.get_text().decode("utf-8")
        bounds=self.text_buffer.get_bounds()
        if bounds and RE:
            start,stop=bounds
            test_text=self.text_buffer.get_text(start,stop,True).decode("utf-8")
            self.text_buffer.delete(start,stop)
            self.text_buffer.set_text(test_text.encode("utf-8"))
            if self.test_case_checkbutton.get_active()==True:
                matches=re.compile(RE,re.UNICODE).finditer(test_text)
            else:
                matches=re.compile(RE,re.UNICODE|re.IGNORECASE).finditer(test_text)
            for match in matches:
                match_start,match_stop,match_text= match.start(), match.end(), match.group()
                iter_start=self.text_buffer.get_iter_at_offset(match_start)
                iter_stop=self.text_buffer.get_iter_at_offset(match_stop)
                self.text_buffer.delete(iter_start,iter_stop)
                self.text_buffer.insert_with_tags_by_name(iter_start,match_text.encode("utf-8"),"match")

    def match_type_changed(self,obj):
        if self.match_type_opt_menu.get_active()/2==5:
            self.match_value2_entry.show()
            self.match_value2_label.show()
            self.match_value_label.show()
            self.match_value_entry.set_size_request(-1,-1)
            self.match_value2_entry.set_size_request(-1,-1)

        else:
            self.match_value2_entry.hide()
            self.match_value2_label.hide()
            self.match_value_label.hide()
            self.match_value_entry.set_size_request(200,-1)
    
    def action_match_type_changed(self,obj):
        if self.action_match_type_opt_menu.get_active()/2==5:
            self.action_match_value2_entry.show()
            self.action_match_value2_label.show()
            self.action_match_value_label.show()
            self.action_match_value_entry.set_size_request(-1,-1)
            self.action_match_value2_entry.set_size_request(-1,-1)

        else:
            self.action_match_value2_entry.hide()
            self.action_match_value2_label.hide()
            self.action_match_value_label.hide()
            self.action_match_value_entry.set_size_request(200,-1)
    
    def action_type_changed(self,obj):
        if self.action_type_opt_menu.get_active()==11:
            self.color1_label.show()
            self.color1_entry.show()
            self.color1_button.show()
            self.color2_entry.show()
            self.color2_button.show()
            self.color2_label.show()
        else:
            self.color1_label.hide()
            self.color1_entry.hide()
            self.color1_button.hide()
            self.color2_entry.hide()
            self.color2_button.hide()
            self.color2_label.hide()

    def get_color_from_button(self,color_button):
        def gdkcolor_to_hex(gdk_color):
            colors=[gdk_color.red,gdk_color.green,gdk_color.blue]
            colors= [("0"+str(hex(col*255/65535))[2:])[-2:].upper() for col in (colors)]
            color = "#"+colors[0]+colors[1]+colors[2]
            return color

        color=color_button.get_color()
        color=gdkcolor_to_hex(color)
        if color_button==self.color1_button:
            self.color1_entry.set_text(color)
        else:
            self.color2_entry.set_text(color)

    def __init__(self,score_rules,main_win):
        self.score_rules=score_rules
        self.wdir=get_wdir()
        self.art_db=main_win.art_db
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Scoring Rules"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(450,450)
        self.window.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/score.xpm"))



        main_vbox=gtk.VBox()
        main_vbox.set_border_width(2)
        self.notebook=gtk.Notebook()


        #Rules Page
        vpaned=gtk.VPaned()
        vpaned.set_border_width(4)
        rules_vbox=gtk.VBox()
        rules_vbox_label=gtk.Label("<b>"+_("Correct Rules")+"</b>")
        rules_vbox_label.set_alignment(0,0.5)
        rules_vbox_label.set_use_markup(True)
        rules_vbox.pack_start(rules_vbox_label,False,False,4)
        self.rules_tree=Rules_Tree()
        rules_table=gtk.Table(1,1,False)
        rules_table.attach(self.rules_tree.get_widget(),0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,16)
        rules_vbox.pack_start(rules_table,True,True)

        file_vbox=gtk.VBox()
        file_vbox_label=gtk.Label("<b>"+_("Score File Editor")+"</b>")
        file_vbox_label.set_alignment(0,0.5)
        file_vbox_label.set_use_markup(True)
        file_vbox.pack_start(file_vbox_label,False,False,4)
        file_table=gtk.Table(3,2,False)
        file_scrolledwin=gtk.ScrolledWindow()
        file_scrolledwin.set_border_width(4)
        file_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        file_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.file_buffer=gtk.TextBuffer()
        self.file_view=gtk.TextView(self.file_buffer)
        self.file_view.set_border_width(4)
        self.file_view.modify_font(pango.FontDescription("Monospace 8"))
        self.file_buffer.set_text(self.score_rules.raw_file.encode("utf-8"))
        file_scrolledwin.add(self.file_view)

        file_butt_hbox=gtk.HBox()
        file_butt_hbox.set_border_width(4)
        self.button_rescan=gtk.Button(_("ReScan Rules"))
        self.button_rescan.connect("clicked",self.rescan_rules)
        self.button_show_errors=gtk.Button(_("Show Errors"))
        self.button_show_errors.connect("clicked",self.show_errors)
        file_butt_hbox.pack_start(self.button_rescan,True,True,2)
        file_butt_hbox.pack_start(self.button_show_errors,True,True,2)
       
        file_table.attach(file_scrolledwin,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,16)
        file_table.attach(file_butt_hbox,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16)

        
        file_vbox.pack_start(file_table,True,True)
        vpaned.add(file_vbox)
        vpaned.add(rules_vbox)
        rules_label=gtk.Label("<b>"+_("Rules")+"</b>")
        rules_label.set_use_markup(True)
        self.notebook.append_page(vpaned,rules_label)



        #New Score Rule Page
        new_rule_vbox=gtk.VBox()
        new_rule_vbox.set_border_width(4)

        scope_vbox=gtk.VBox()
        scope_vbox.set_border_width(4)
        scope_label=gtk.Label("<b>"+_("Groups Scope")+"</b>")
        scope_label.set_alignment(0,0.5)
        scope_label.set_use_markup(True)
        scope_vbox.pack_start(scope_label,False,False,4)

        self.scope_combo=gtk.combo_box_entry_new_text()
        popdown=self.score_rules.raw_scopes
        if "[*]" not in popdown:
            popdown.insert(0,"[*]")
        subscribed=self.art_db.getSubscribed()
        subscribed=["["+subscribed[i][0]+"]" for i in range(len(subscribed))]
        popdown=popdown+subscribed
        for item in popdown:
            self.scope_combo.append_text(item)
        self.scope_combo.set_active(0)
        self.scope_combo.set_size_request(250,-1)
        scope_hbox=gtk.HBox()
        scope_hbox.set_border_width(4)
        scope_hbox.pack_start(self.scope_combo,True,False,2)
        scope_vbox.add(scope_hbox)

        condition_main_vbox=gtk.VBox()
        condition_label=gtk.Label("<b>"+_("Condition")+"</b>")
        condition_label.set_alignment(0,0.5)
        condition_label.set_use_markup(True)
        condition_main_vbox.pack_start(condition_label,False,False,4)
        condition_table=gtk.Table(3,1,False)
        condition_hbox=gtk.HBox()
        self.header_opt_menu=gtk.combo_box_new_text()
        self.header_opt_menu.set_size_request(130,-1)
        for header in self.score_rules.headers:
            self.header_opt_menu.append_text(header.capitalize())
        self.header_opt_menu.set_active(0)
        condition_hbox.pack_start(self.header_opt_menu,True,False,2)
        values=[_("Contains String"),_("Doesn't Contain String"),_("Matches RegEx"),_("Doesn't Match RegEx"), _("Greater Than"), _("Not Greater Than"), _("Lower Than"),_("Not Lower Than"), _("Equal To (numbers only)"),_("Different From (numbers only)"), _("In Range"),_("Out Of Range")]
        self.match_type_opt_menu=gtk.combo_box_new_text()
        self.match_type_opt_menu.set_size_request(130,-1)
        for value in values:
            self.match_type_opt_menu.append_text(value)
        self.match_type_opt_menu.set_active(0)
        self.match_type_opt_menu.connect("changed",self.match_type_changed)
        condition_hbox.pack_start(self.match_type_opt_menu,True,False)
        self.case_checkbutton=gtk.CheckButton(_("Case Sensitive"))
        self.match_value_entry=gtk.Entry()
        self.match_value_entry.set_size_request(200,-1)
        self.match_value2_entry=gtk.Entry()
        self.match_value_label=gtk.Label(_("Lower Limit"))
        self.match_value2_label=gtk.Label(_("Upper Limit"))
        match_value_hbox=gtk.HBox()
        match_value_hbox.pack_start(self.match_value_label,True,False,2)
        match_value_hbox.pack_start(self.match_value_entry,True,True,2)
        match_value_hbox.pack_start(self.match_value2_label,True,False,2)
        match_value_hbox.pack_start(self.match_value2_entry,True,True,2)
        condition_table.attach(condition_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        condition_table.attach(match_value_hbox,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        condition_table.attach(self.case_checkbutton,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        condition_main_vbox.pack_start(condition_table,True,True)

        score_mod_vbox=gtk.VBox()
        score_mod_label=gtk.Label("<b>"+_("Score")+"</b>")
        score_mod_label.set_use_markup(True)
        score_mod_label.set_alignment(0,0.5)
        score_mod_vbox.pack_start(score_mod_label,False,False,4)
        score_mod_table=gtk.Table(1,1,False)
        score_mod_hbox=gtk.HBox()
        values=[_("Raise Score"),_("Lower Score"), _("Set Score")]
        self.score_mod_opt_menu=gtk.combo_box_new_text()
        for value in values:
            self.score_mod_opt_menu.append_text(value)
        self.score_mod_opt_menu.set_active(0)
        self.score_mod_opt_menu.set_size_request(130,-1)
        score_mod_hbox.pack_start(self.score_mod_opt_menu,True,False,2)
        score_mod_table.attach(score_mod_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,2)
        score_mod_vbox.add(score_mod_table)
        self.score_mod_spinbutton=gtk.SpinButton(gtk.Adjustment(value=100,lower=-9999,upper=9999,step_incr=100,page_incr=1000))
        self.score_mod_spinbutton.set_size_request(130,-1)
        score_mod_hbox.pack_start(self.score_mod_spinbutton,True,False,2)

        #add rule button
        self.add_rule_button=gtk.Button(_("Add Rule"))
        self.add_rule_button.connect("clicked",self.add_new_rule)

        new_rule_vbox.pack_start(scope_vbox,False,True,2)
        new_rule_vbox.pack_start(condition_main_vbox,True,True,2)
        new_rule_vbox.pack_start(score_mod_vbox,True,True,2)
        new_rule_vbox.pack_start(self.add_rule_button,True,False,2)
        new_rule_label=gtk.Label("<b>"+_("New Scoring Rule")+"</b>")
        new_rule_label.set_use_markup(True)
        self.notebook.append_page(new_rule_vbox,new_rule_label)



        #New Action Rule Page
        new_action_rule_vbox=gtk.VBox()
        new_action_rule_vbox.set_border_width(4)

        action_scope_vbox=gtk.VBox()
        action_scope_vbox.set_border_width(4)
        action_scope_label=gtk.Label("<b>"+_("Groups Scope")+"</b>")
        action_scope_label.set_use_markup(True)
        action_scope_label.set_alignment(0,0.5)
        action_scope_vbox.pack_start(action_scope_label,False,False,4)
        self.action_scope_combo=gtk.combo_box_entry_new_text()
        popdown=self.score_rules.raw_scopes
        if "[*]" not in popdown:
            popdown.insert(0,"[*]")
        subscribed=self.art_db.getSubscribed()
        subscribed=["["+subscribed[i][0]+"]" for i in range(len(subscribed))]
        popdown=popdown+subscribed
        for item in popdown:
            self.action_scope_combo.append_text(item)
        self.action_scope_combo.set_active(0)
        self.action_scope_combo.set_size_request(250,-1)
        action_scope_hbox=gtk.HBox()
        action_scope_hbox.set_border_width(4)
        action_scope_hbox.pack_start(self.action_scope_combo,True,False,2)
        action_scope_vbox.add(action_scope_hbox)

        action_condition_main_vbox=gtk.VBox()
        action_condition_label=gtk.Label("<b>"+_("Condition")+"</b>")
        action_condition_label.set_alignment(0,0.5)
        action_condition_label.set_use_markup(True)
        action_condition_main_vbox.pack_start(action_condition_label,False,False,4)
        action_condition_table=gtk.Table(3,1,False)
        action_condition_hbox=gtk.HBox()
        self.action_header_opt_menu=gtk.combo_box_new_text()
        self.action_header_opt_menu.set_size_request(130,-1)
        for header in self.score_rules.action_headers:
            self.action_header_opt_menu.append_text(header.capitalize())
        self.action_header_opt_menu.set_active(0)
        action_condition_hbox.pack_start(self.action_header_opt_menu,True,False,2)
        values=[_("Contains String"),_("Doesn't Contain String"),_("Matches RegEx"),_("Doesn't Match RegEx"), _("Greater Than"), _("Not Greater Than"), _("Lower Than"),_("Not Lower Than"), _("Equal To (numbers only)"),_("Different From (numbers only)"), _("In Range"),_("Out Of Range")]
        self.action_match_type_opt_menu=gtk.combo_box_new_text()
        self.action_match_type_opt_menu.set_size_request(130,-1)
        for value in values:
            self.action_match_type_opt_menu.append_text(value)
        self.action_match_type_opt_menu.set_active(0)
        self.action_match_type_opt_menu.connect("changed",self.action_match_type_changed)
        action_condition_hbox.pack_start(self.action_match_type_opt_menu,True,False)
        self.action_case_checkbutton=gtk.CheckButton(_("Case Sensitive"))
        self.action_match_value_entry=gtk.Entry()
        self.action_match_value_entry.set_size_request(200,-1)
        self.action_match_value2_entry=gtk.Entry()
        self.action_match_value_label=gtk.Label(_("Lower Limit"))
        self.action_match_value2_label=gtk.Label(_("Upper Limit"))
        action_match_value_hbox=gtk.HBox()
        action_match_value_hbox.pack_start(self.action_match_value_label,True,False,2)
        action_match_value_hbox.pack_start(self.action_match_value_entry,True,True,2)
        action_match_value_hbox.pack_start(self.action_match_value2_label,True,False,2)
        action_match_value_hbox.pack_start(self.action_match_value2_entry,True,True,2)
        action_condition_table.attach(action_condition_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        action_condition_table.attach(action_match_value_hbox,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        action_condition_table.attach(self.action_case_checkbutton,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        action_condition_main_vbox.add(action_condition_table)


        action_vbox=gtk.VBox()
        action_label=gtk.Label("<b>"+_("Action")+"</b>")
        action_label.set_use_markup(True)
        action_label.set_alignment(0,0.5)
        action_vbox.pack_start(action_label,False,False,4)
        action_table=gtk.Table(1,1,False)
        action_hbox=gtk.HBox()
        action_setcolor_hbox=gtk.HBox()
        action_setcolor_color_hbox=gtk.HBox()
        values=[_("Kill"),_("Mark Read"),_("Mark Unread"),_("Mark for Download"),_("UnMark for Download"),_("Retrieve"),_("Keep"),_("UnKeep"),_("Watch"),_("Ignore"),_("UnSetWatchIgnore"),_("SetColor")]
        self.action_type_opt_menu=gtk.combo_box_new_text()
        for value in values:
            self.action_type_opt_menu.append_text(value)
        self.action_type_opt_menu.set_active(0)
        self.action_type_opt_menu.set_size_request(130,-1)
        self.action_type_opt_menu.connect("changed",self.action_type_changed)
        action_hbox.pack_start(self.action_type_opt_menu,True,False,2)
        self.color1_label=gtk.Label(_("Foreground Color"))
        self.color2_label=gtk.Label(_("Background Color"))
        self.color1_entry=gtk.Entry()
        self.color2_entry=gtk.Entry()
        self.color1_button=gtk.ColorButton()
        self.color2_button=gtk.ColorButton()
        self.color1_button.connect("color_set",self.get_color_from_button)
        self.color2_button.connect("color_set",self.get_color_from_button)
        action_setcolor_color_hbox.pack_start(self.color1_label,True,False)
        action_setcolor_color_hbox.pack_start(self.color2_label,True,False)
        action_setcolor_hbox.pack_start(self.color1_entry,True,False,2)
        action_setcolor_hbox.pack_start(self.color1_button,True,False,2)
        action_setcolor_hbox.pack_start(self.color2_entry,True,False,2)
        action_setcolor_hbox.pack_start(self.color2_button,True,False,2)
        action_table.attach(action_hbox,0,1,0,1,gtk.EXPAND|gtk.FILL,16,6)
        action_table.attach(action_setcolor_color_hbox,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        action_table.attach(action_setcolor_hbox,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        action_vbox.pack_start(action_table,True,True)

        #add action rule button
        self.add_action_rule_button=gtk.Button(_("Add Rule"))
        self.add_action_rule_button.connect("clicked",self.add_new_action_rule)

        new_action_rule_vbox.pack_start(action_scope_vbox,False,True,2)
        new_action_rule_vbox.pack_start(action_condition_main_vbox,True,True,2)
        new_action_rule_vbox.pack_start(action_vbox,True,True,2)
        new_action_rule_vbox.pack_start(self.add_action_rule_button,True,False,2)
        new_action_rule_label=gtk.Label("<b>"+_("New Action Rule")+"</b>")
        new_action_rule_label.set_use_markup(True)
        self.notebook.append_page(new_action_rule_vbox,new_action_rule_label)



        #RegEx Tester Page
        re_tester_vbox=gtk.VBox()
        re_tester_vbox.set_border_width(4)

        re_vbox=gtk.VBox()
        re_label=gtk.Label("<b>"+_("Regular Expression")+"</b>")
        re_label.set_use_markup(True)
        re_label.set_alignment(0,0.5)
        re_vbox.pack_start(re_label,False,False,4)
        re_table=gtk.Table(1,1,False)
        re_table.set_border_width(2)
        self.re_entry=gtk.Entry()
        re_test_button=gtk.Button(_("Test Regular Expression"))
        re_test_button.connect("clicked",self.test_re)
        self.test_case_checkbutton=gtk.CheckButton(_("Case Sensitive"))
        re_table.attach(self.re_entry,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        re_table.attach(self.test_case_checkbutton,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        re_table.attach(re_test_button,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,16,6)
        re_vbox.add(re_table)
        re_tester_vbox.pack_start(re_vbox,False,True,2)

        text_vbox=gtk.VBox()
        text_label=gtk.Label("<b>"+_("Test Text")+"</b>")
        text_label.set_alignment(0,0.5)
        text_label.set_use_markup(True)
        text_vbox.pack_start(text_label,False,False,4)
        text_table=gtk.Table(1,1,False)
        text_scrolledwin=gtk.ScrolledWindow()
        text_scrolledwin.set_border_width(4)
        text_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        text_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.text_buffer=gtk.TextBuffer()
        self.text_view=gtk.TextView(self.text_buffer)
        self.text_view.set_border_width(4)
        text_scrolledwin.add(self.text_view)
        text_table.attach(text_scrolledwin,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,16)
        text_vbox.pack_start(text_table,True,True)
        re_tester_vbox.pack_start(text_vbox,True,True,2)

        re_tester_label=gtk.Label("<b>"+_("RE Tester")+"</b>")
        re_tester_label.set_use_markup(True)
        self.notebook.append_page(re_tester_vbox,re_tester_label)

        #OK CANCEL buttons
        main_buttons_hbox=gtk.HBox()
        main_buttons_hbox.set_border_width(4)

        cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        cancel_button_tooltip=gtk.Tooltips()
        cancel_button_tooltip.set_tip(cancel_button,_("Close window. Discard changes"))
        cancel_button.connect("clicked",self.destroy)
        main_buttons_hbox.pack_start(cancel_button,True,True,0)
        ok_button=gtk.Button(None,gtk.STOCK_OK)
        ok_button_tooltip=gtk.Tooltips()
        ok_button_tooltip.set_tip(ok_button,_("Close window. Save Changes"))
        ok_button.connect("clicked",self.close_window)
        main_buttons_hbox.pack_start(ok_button,True,True,2)

        vpaned.set_position(200)
        main_vbox.pack_start(self.notebook,True,True,0)

        main_vbox.pack_start(main_buttons_hbox,False,False,0)
        self.window.add(main_vbox)


        #some init
        self.show_rules()

        tag_table=self.text_buffer.get_tag_table()
        tag_match=gtk.TextTag("match")
        tag_table.add(tag_match)
        color_bg=gtk.gdk.color_parse("#0000FF")
        color_fg=gtk.gdk.color_parse("#FFFFFF")
        tag_match.set_property("weight",1000)
        tag_match.set_property("background-gdk",color_bg)
        tag_match.set_property("foreground-gdk",color_fg)




if __name__=="__main__":
    Score_Rules()
