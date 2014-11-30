from email.Utils import parsedate,parsedate_tz,mktime_tz,parseaddr,make_msgid, formataddr
from time import ctime,time
import gtk
import email
import email.Header
from StringIO import *
from string import find,replace
import base64

def old_parse_from(from_name):
    left=from_name.rfind("<")
    if left!=-1:
        # It is like "nick" <email> or nick <email>
        if from_name[0]=="\"":
            #It is like "nick" <email>
            nick=from_name[1:left-2].strip()
        else:
            #it is like nick <email>
            nick=from_name[0:left].strip()
        email=from_name[left+1:-1]
    else:
        left=from_name.rfind("(")
        if left!=-1:
            #it is like email (nick)
            right=from_name.rfind(")")
            nick=from_name[left+1:right].strip()
            email=from_name[0:left-1]
        else:
            #ther is only the email
            nick=""
            email=from_name
    if nick=="":
        nick=from_name
    return nick,email.strip()

class Article:

    def my_decode_header(self,header):
        try: parts=email.Header.decode_header(header)
        except: parts=[[header,None]]
        header_decoded=""
        for i in range(len(parts)):
            charset=parts[i][1]
            if parts[i][1]!=None:
                charset=parts[i][1]
            else:
                charset=self.fallback_cset
            try:
                header_decoded=header_decoded+" "+unicode(parts[i][0],charset,"replace").strip(" ")
            except :#LookupError: 
                # had to comment the LookupError and add a second except to catch an exception that popped up
                # trying to reopen an article with some encoded words in the xface ...
                try:
                    header_decoded=header_decoded+" "+unicode(parts[i][0],self.fallback_cset,"replace").strip(" ")
                except TypeError:
                    header_decoded=header_decoded+" "+parts[i][0].strip()
        header_decoded=header_decoded.strip()
        return header_decoded

    def decode_header_list(self,list):
        try:
            decoded_list=[unicode(line,self.cset,"replace") for line in list]
        except LookupError:
            decoded_list=[unicode(line,self.fallback_cset,"replace") for line in list]
        self.raw_header_list=decoded_list
        
    def parse_header_list(self,hlist,rebuild=False):
        i=0
        hlist_len=len(hlist)
        while i < hlist_len:
            ind=hlist[i].find(":")
            if ind>0:
                header_name=hlist[i][:ind].strip().lower()
                header_value=hlist[i][ind+1:].strip()
                j=i+1
                while j < hlist_len:
                    if (hlist[j][0]==" " or  hlist[j][0]=="\t"):
                        header_value=header_value+hlist[j]
                        j=j+1
                        i=i+1
                    else:
                        break
                header_value=self.my_decode_header( header_value.replace("\r","").replace("\n",""))
                self.hdict[header_name]=header_value
            i=i+1
        nick,email=self.parse_from(self.hdict.get("from",""))
        date_parsed=self.parse_date(self.hdict.get("date",""))
        self.nick=nick
        self.email=email
        self.from_name=self.hdict.get("from","")
        self.ngroups=self.hdict.get("newsgroups","")
        #self.ref=self.hdict.get("references","")  # I don't want to update this field
        self.fup_to=self.hdict.get("followup-to","")
        self.reply_to=self.hdict.get("reply-to","")
        self.user_agent=self.hdict.get("user-agent","")
        self.subj=self.hdict.get("subject","")
        self.date=self.hdict.get("date","")
        self.date_parsed=date_parsed
        self.x_face=self.hdict.get("x-face",None)
        self.face=self.hdict.get("face",None)
        ctype_dict=self.parse_content_type(self.hdict.get("content-type",""))
        self.ct_enc=self.hdict.get("content-transfer-encoding","")
        self.cset=ctype_dict.get("charset","")
        if self.cset=="":
            self.cset=self.fallback_cset
        if not rebuild:
            self.decode_header_list(hlist)
        else:
            self.raw_header_list=hlist

    def get_hdr(self,name):
        name=name.lower()
        return self.hdict.get(name,"")

    def parse_content_type(self,ctype):
        #split Content-Type in its components
        sub_parts=ctype.split(";")
        ctype_dic=dict()
        if len(sub_parts)>1:
            for part in sub_parts:
                if len(part)>0:
                    ind=part.find("=")
                    if ind!=-1:
                        param_name,param_value=part[:ind],part[ind+1:]
                        ctype_dic[param_name.strip()]=param_value.strip()
                    else:
                        ctype_dic["type"]=part.strip()
        return ctype_dic
    
    def parse_from(self,from_name):
        nick,email=parseaddr(from_name)
        if not nick:
            nick=email
        if not nick and not email:
            nick,email = old_parse_from(from_name)
        return nick,email
        

    def parse_date(self,date):
        #data=parsedate(date)
        try: #trying to prevent the rfc822.parsedate bug with Tue,26 instead of Tue, 26
            secs=mktime_tz(parsedate_tz(date))
        except:
            secs=time()
        self.secs=secs
        data=parsedate(ctime(secs))
        if data[3]<10:
            ora="0"+repr(data[3])
        else:
            ora=repr(data[3])
        if data[4]<10:
            minuti="0"+repr(data[4])
        else:
            minuti=repr(data[4])
        return repr(data[2])+"/"+repr(data[1])+"/"+repr(data[0])+" "+ora+":"+minuti

    def get_all_headers(self):
        return self.nick,self.email,self.from_name,self.ngroups,self.ref,self.fup_to,self.reply_to,self.ct_enc,self.cset,self.subj,self.date,self.date_parsed,self.user_agent

    def get_headers(self):
        return self.nick,self.from_name,self.ref,self.subj,self.date,self.date_parsed

    def get_body(self):
        return self.body
        
    def set_body(self,rawbody,rebuild=False):
        if rebuild: rawbody=rawbody.encode("utf-8")
        self.raw_body=rawbody
        msg = email.message_from_string(rawbody)
        charsets= msg.get_charsets()
        if msg.is_multipart():
            body = ''
            body_list=[]
            self.body_parts=[]
            i=0
            for part in msg.walk():
                mtype = part.get_content_maintype()
                ctype = part.get_content_type()
                # Skip multipart container
                if mtype != 'multipart':
                    payload=part.get_payload(decode=(mtype=='text'))
                    
                    if type(payload)==type([]):
                        try: body=payload[0].as_string()
                        except: body=str(payload[0])
                    else:
                        body=str(payload)
                    body = body +'\n'
                    if not rebuild:
                        try:
                            body = unicode(body, str(charsets[i]), 'replace')
                        except LookupError:
                            body = unicode(body, self.fallback_cset, 'replace')
                    body_list.append(body)
                    self.body_parts.append((ctype,body))
                i=i+1
            # Return one line per item list.
            body='\n'.join(body_list)
            self.body= body.splitlines()
        else:
            
            body=msg.get_payload(decode=False) #the q-printable could break if I'm reloading the article
            
            if not rebuild:
                body=msg.get_payload(decode=True)
                try:
                    body = unicode(body, self.cset, 'replace')
                except LookupError:
                    body = unicode(body, self.fallback_cset, 'replace')
            self.body=body.splitlines()
        self.has_body=True

        


    def get_raw(self,return_string=False):
        try:
            raw=self.raw_header_list+[""]+self.body
        except:
            raw=None
        if return_string:
            if raw: raw="\n".join(raw)
            else :  raw=None
        return raw

    def set_score(self,score):
        self.score=score

    def get_score(self):
        return self.score

    def reset_article_score_actions(self):
        self.score=0
        self.marked_for_download=False
        self.keep=False
        self.watch=False
        self.ignore=False
        self.fg_color=None
        self.bg_color=None

    def get_article_info(self,icons):
        art_fup,art_body,art_unread,art_read,art_mark,art_keep,art_unkeep,art_watch,art_unwatchignore,art_ignore=icons
            
            
        #number=self.number
        msgid=self.msgid
        nick,from_name,ref,subj,date,date_parsed=self.get_headers()
        if self.keep:
            icon2=art_keep
        else:
            icon2=art_unkeep

        if self.is_read:
            isUnread=False
            icon=art_read
        else:
            isUnread=True
            if self.has_body:
                icon=art_body
            elif self.marked_for_download:
                icon=art_mark
            else:
                icon=art_unread
            
        show_score=True          
        if self.score<0:
            score_foreground="red"
                
        elif self.score>0:
            score_foreground="darkgreen"
           
        else : #self.score==0
            score_foreground="darkgreen"
            show_score=False

           
        if self.watch:
            icon3=art_watch
        elif self.ignore:
            icon3=art_ignore
        else:
            icon3=art_unwatchignore
        
        try :
            fg_color=self.fg_color
        except:
            fg_color_set=False
            fg_color="black"
        else:
            if fg_color:
                if self.fg_color.lower()!="default":
                    fg_color_set=True
                    try: gtk.gdk.color_parse(fg_color)
                    except: 
                        fg_color="black"
                        fg_color_set=False
                else:
                    fg_color_set=False
                    fg_color="black"
            else:
                fg_color_set=False
                fg_color="black"


        try :
            bg_color=self.bg_color
        except:
            bg_color_set=False
            bg_color="white"
        else:
            if bg_color:
                if self.bg_color.lower()!="default":
                    bg_color_set=True
                    try: gtk.gdk.color_parse(bg_color)
                    except: 
                        bg_color="white"
                        bg_color_set=False
                else:
                    bg_color_set=False
                    bg_color="black"                           
            else:
                bg_color_set=False
                bg_color="white"
        article_info = [icon,subj,nick,date_parsed,self,isUnread,self.secs,self.score,score_foreground,show_score,icon2,icon3,0,False,fg_color_set,fg_color,bg_color_set,bg_color,False,0]
        return article_info


    def __init__(self,number,msgid,from_name,ref,subj,date,fallback_charset,original_group,xref,bytes,lines,rebuild=False):
        if not rebuild:
            self.hdict=dict()
            self.score=0
            self.number=number
            self.fallback_cset=fallback_charset
            self.msgid=self.my_decode_header(msgid)
            self.from_name=self.my_decode_header(from_name)
            self.nick,self.email=self.parse_from(self.from_name)
            self.ref=self.my_decode_header(ref)
            self.subj=self.my_decode_header(subj)
            self.date=date
            self.date_parsed=self.parse_date(date)
            self.hdict["message-id"]=msgid
            self.hdict["from"]=self.my_decode_header(from_name)
            self.hdict["references"]=self.my_decode_header(ref)
            self.hdict["subject"]=self.my_decode_header(subj)
            self.hdict["date"]=date
            self.hdict["xref"]=xref[5:].strip()
            self.hdict["bytes"]=bytes
            self.hdict["lines"]=lines

            self.body=None
            self.raw=None
            self.is_read=False
            self.marked_for_download=False
            self.keep=False
            self.watch=False
            self.ignore=False
            self.original_group=original_group
            self.x_face=None
            self.face=None
            self.raw_header_list=None
            self.fg_color=None
            self.bg_color=None
            self.xref=self.hdict.get("xref","")
            self.raw_body=""
            self.has_body=False
            try: self.bytes=int(bytes)
            except ValueError: self.bytes=0
            try: self.lines=int(lines)
            except ValueError: self.lines=0
        else:
            self.hdict=dict()
            self.score=0
            self.number=number
            self.fallback_cset=fallback_charset
            self.msgid=msgid
            self.from_name=from_name
            self.nick,self.email=self.parse_from(self.from_name)
            self.ref=ref
            self.subj=subj
            self.date=date
            self.date_parsed=self.parse_date(date)
            self.hdict["message-id"]=msgid
            self.hdict["from"]=self.from_name
            self.hdict["references"]=self.ref
            self.hdict["subject"]=self.subj
            self.hdict["date"]=date
            self.hdict["xref"]=xref
            self.hdict["bytes"]=bytes
            self.hdict["lines"]=lines
            self.body=None
            self.raw=None
            self.is_read=False
            self.marked_for_download=False
            self.keep=False
            self.watch=False
            self.ignore=False
            self.original_group=original_group
            self.x_face=None
            self.face=None
            self.raw_header_list=None
            self.fg_color=None
            self.bg_color=None
            self.xref=self.hdict.get("xref","")
            self.raw_body=""
            self.has_body=False
            try: self.bytes=int(bytes)
            except ValueError: self.bytes=0
            try: self.lines=int(lines)
            except ValueError: self.lines=0
        
class Article_To_Send:
    def best_enc(self,text):
        for best_enc in self.ordered_list:
            try:
                text.encode(best_enc,"strict")
            except:
                pass
            else:
                break
        return best_enc

    def my_encode_header(self,header):
        usascii=True
        for j in range(len(header)):
            if ord(header[j])>127:
                #String is not us-ascii
                usascii=False
                break
        if usascii:
            header_encoded=header
        else:
            #let's search the beginning of the word
            i=j
            char=header[i]
            while char!=" " and i>=0:
                i=i-1
                char=header[i]
            best_enc=self.best_enc(header)
            if i==0:
                head_new=header.encode(best_enc,"replace")
                header_encoded=str(email.Header.Header(head_new,best_enc))
            else:
                head_new=header[i+1:].encode(best_enc,"replace")
                header_new_encoded=str(email.Header.Header(head_new,best_enc))
                header_encoded=header[:i+1]+header_new_encoded
        return header_encoded.strip()


    def encode_body(self,body,output_charset):
        body_encoded=""
        for line in body:
            #string=unicode(list[i]+"\n",input_charset)
            line=line+"\n"
            line_encoded=line.encode(output_charset,"replace")
            body_encoded=body_encoded+line_encoded
        return body_encoded

    def get_article(self):
        article="Newsgroups: "+self.newsgroups+"\n"
        article=article+"From: "+formataddr([self.nick_encoded,self.email])+"\n"
        article=article+"Subject: "+self.subject_encoded+"\n"
        if self.references!="":
            article=article+"References: "+self.references+"\n"
        self.references=""
        article=article+"User-Agent: "+self.user_agent+"\n"
        article=article+"MIME-Version: 1.0\n"
        article=article+"Content-Type: text/plain; charset="+self.output_charset+"\n"
        if self.output_charset.lower()=="us-ascii":
            article=article+"Content-Transfer-Encoding: 7bit\n"
        else:
            article=article+"Content-Transfer-Encoding: 8bit\n"
        if self.generate_mid=="True":
            mid=make_msgid("XPN")
            if self.fqdn:
                left,right=mid.split("@")
                def clear_fqdn(s,chars):
                    s=s.encode("us-ascii","replace")
                    for char in chars:
                        s=s.replace(char,"")
                    return s
                mid=left+"@"+clear_fqdn(self.fqdn,"@\\\"<>()[];:,")+">"
            article=article+"Message-ID: "+mid+"\n"
        for header in self.custom_headers:
            article=article+header+"\n"
        article=article+"\n"
        article=article.encode("utf-8")+self.body_encoded
        return article

    def parse_from(self,from_name):
        nick,email=parseaddr(from_name)
        if not nick:
            nick=email
        if not nick and not email:
            nick,email = old_parse_from(from_name)
        return nick,email


    def __init__(self,newsgroups,from_name,subject,references,user_agent,output_charset,ordered_list,body,custom_names,custom_values,generate_mid,fqdn):
        self.newsgroups=newsgroups
        self.ordered_list=ordered_list
        nick,self.email=self.parse_from(from_name)
        self.nick_encoded=self.my_encode_header(nick)
        self.subject_encoded=self.my_encode_header(subject)
        self.references=references
        self.user_agent=user_agent
        self.output_charset=output_charset
        self.body_encoded=self.encode_body(body,output_charset)
        self.custom_headers=[]
        for i in range(len(custom_names)):
            custom_header=custom_names[i].encode("us-ascii","replace")+": "+self.my_encode_header(custom_values[i])
            self.custom_headers.append(custom_header)
        self.generate_mid=generate_mid
        self.fqdn=fqdn


class Mail_To_Send:
    def best_enc(self,text):
        for best_enc in self.ordered_list:
            try:
                text.encode(best_enc,"strict")
            except:
                pass
            else:
                break
        return best_enc

    def my_encode_header(self,header):
        usascii=True
        for j in range(len(header)):
            if ord(header[j])>127:
                #String is not us-ascii
                usascii=False
                break
        if usascii:
            header_encoded=header
        else:
            #let's search the beginning of the word
            i=j
            char=header[i]
            while char!=" " and i>=0:
                i=i-1
                char=header[i]
            best_enc=self.best_enc(header)
            if i==0:
                head_new=header.encode(best_enc,"replace")
                header_encoded=str(email.Header.Header(head_new,best_enc))
            else:
                head_new=header[i+1:].encode(best_enc,"replace")
                header_new_encoded=str(email.Header.Header(head_new,best_enc))
                header_encoded=header[:i+1]+header_new_encoded
        return header_encoded.strip()


    def encode_body(self,body,output_charset):
        body_encoded=""
        for line in body:
            #string=unicode(list[i]+"\n",input_charset)
            line=line+"\n"
            line_encoded=line.encode(output_charset,"replace")
            body_encoded=body_encoded+line_encoded
        return body_encoded

    def get_article(self):
        article="To: "+formataddr([self.to_nick_encoded,self.to_email])+"\n"
        article=article+"From: "+formataddr([self.nick_encoded,self.email])+"\n"
        article=article+"Subject: "+self.subject_encoded+"\n"
        article=article+"Date: "+self.date+"\n"
        if self.references!="":
            article=article+"References: "+self.references+"\n"
        self.references=""
        article=article+"User-Agent: "+self.user_agent+"\n"
        article=article+"MIME-Version: 1.0\n"
        article=article+"Content-Type: text/plain; charset="+self.output_charset+"\n"
        if self.output_charset.lower()=="us-ascii":
            article=article+"Content-Transfer-Encoding: 7bit\n"
        else:
            article=article+"Content-Transfer-Encoding: 8bit\n"
        article=article+"\n"
        article=article.encode("utf-8")+self.body_encoded
        return article

    def parse_from(self,from_name):
        nick,email=parseaddr(from_name)
        if not nick:
            nick=email
        if not nick and not email:
            nick,email = old_parse_from(from_name)
        return nick,email


    def __init__(self,to_name,from_name,date,subject,references,user_agent,output_charset,ordered_list,body):
        self.ordered_list=ordered_list
        self.to_name=to_name
        to_nick,self.to_email=self.parse_from(to_name)
        self.to_nick_encoded=self.my_encode_header(to_nick)
        self.date=date
        nick,self.email=self.parse_from(from_name)
        self.nick_encoded=self.my_encode_header(nick)
        self.subject_encoded=self.my_encode_header(subject)
        self.references=references
        self.user_agent=user_agent
        self.output_charset=output_charset
        self.body_encoded=self.encode_body(body,output_charset)
