import cPickle
import socket
import time
import gtk
import sys
import os
import ConfigParser
from xpn_src.Article import Article
from xpn_src.Score import Score_Rules
from xpn_src.Connections_Handler import Connection, SSLConnection
from xpn_src.UserDir import get_wdir
from xpn_src.Dialogs import Dialog_OK
from xpn_src.Articles_DB import Articles_DB,Groups_DB


try:
    set()
except:
    from sets import Set as set

class ExportNewsrc:
    def open_groups_list(self):
        "returns the newsgroups lists, divided on a per server base"
        file_list=os.listdir(os.path.join(self.wdir,"groups_info"))
        groups=[]
        for file_name in file_list:
            if file_name.endswith(".groups.sqlitedb"):
                groups_list=self.groups_list_db.getList(file_name)
                groups.append(groups_list)
        return groups


    def open_subscribed_list(self):
        "returns subscribed_list and the read_articles lists"
        subscribed=self.art_db.getSubscribed()
        name_list=[]
        read_list={}
        first_list={}
        for group in subscribed:
            name_list.append([group[0],group[2]])
            last=group[1]
            sorted=[]
            for article in self.art_db.getArticles(group[0],[],True):
                sorted.append(article)
            if sorted:
                first=int(sorted[0].number)
                read_articles=range(first,int(last)+1)
                for article in sorted:
                    if not article.is_read:
                        read_articles.remove(int(article.number))
                read_list[group[0]]=read_articles
                first_list[group[0]]=first
            else:
                read_list[group[0]]=range(int(last),int(last)+1)
                first_list[group[0]]=int(last)
        return name_list,read_list,first_list
    
    def build_clist(self,read_articles,first):
        if not read_articles:
            clist=""
        else:
            clist=self.format_intervals(self.compact_list(read_articles))
        if first in read_articles:
            splitted=clist.split(",")
            if "-" in splitted[0]:
                first_block=splitted[0].split("-")
                first_block[0]="1"
                splitted[0]="-".join(first_block)
            else:
                splitted[0]="1-"+str(first)
            clist=",".join(splitted)
        else:
            if first >1: clist="1-"+str(first-1)+","+clist
        if clist.endswith(","): clist=clist[:-1]
        return clist

    def compact_list(self,L):
        intervals = [[L[0]] * 2]
        for item in L:
            if item == 1+intervals[-1][-1]:
                intervals[-1][-1] = item
            else:
                intervals.append([item]*2)
        intervals.pop(0)
        return intervals

    def format_intervals(self,intervals):
        string=""
        for interval in intervals:
            if interval[0]==interval[1]:
                string=string+str(interval[0])+","
            else:
                string=string+str(interval[0])+"-"+str(interval[1])+","
        return string[0:-1]

    def build_line(self,group,subscribed_list,read_list,first_list):
        if subscribed_list!=None:
            if group in subscribed_list:
                clist=self.build_clist(read_list[group[0]],first_list[group[0]])
                return (group[0]+": "+clist).strip()
            else:
                return group[0]+"!"
        else:
            return group[0]+"!"

    def build_newsrc(self):
        subscribed_list,read_list,first_list=self.open_subscribed_list()
        groups_lists=self.open_groups_list()
        
        def build_file(groups_list,server):
            newsrc=[]
            for group in groups_list:
                line=self.build_line([group[0],group[2]],subscribed_list,read_list,first_list)+"\n"
                newsrc.append(line)
            newsrc="".join(newsrc)
            return newsrc

        if not groups_lists:
            return None
        else:
            newsrc_files=dict()
            for groups_list in groups_lists:
                server=groups_list[0][2]
                newsrc_file=build_file(groups_list,server)
                newsrc_files[server]=newsrc_file
            return newsrc_files

    def save_newsrc(self,where):
        if self.newsrc:
            for server,newsrc_file in self.newsrc.iteritems():
                try:
                    f=open(os.path.join(where,server+".newsrc"),"wb")
                except IOError:
                    pass
                else:
                    f.write(self.newsrc[server])
                    f.close()


    def __init__(self,art_db):
        self.wdir=get_wdir()
        self.art_db=art_db
        self.groups_list_db=Groups_DB()
        self.message=""
        self.newsrc=""
        self.newsrc=self.build_newsrc()
        if self.newsrc==None:
            self.message="You have to download the newsgroups list first"
        else:
            self.message=_("Newsrc successful exported")



class ImportNewsrc:
    def extract_ranges(self,L):
        list=[]
        if L!="":
            intervals=L.split(",")
            for interval in intervals:
                if "-" in interval:
                    #this is a range
                    start,stop=int(interval.split("-")[0]),int(interval.split("-")[1])
                    #list.extend(range(start,stop+1))
                else:
                    #this is a single number
                    list.append(int(interval))
        return list



    def find_first_unread(self,L):
        first_interval=L.split(",")[0]
        if "-" in first_interval:
            if first_interval.split("-")[0]=="1":
                first_unread=int(first_interval.split("-")[1])+1
            else:
                first_unread=1
        else:
            if first_interval=="1":
                first_unread=2
            else:
                first_unread=1
        return first_unread

    def subscribe_groups(self,newsrc,server_name):
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","id.txt"))
        try:
            id_name=cp.sections()[0]
        except IndexError:
            Dialog_OK(_("First you have to create at least one Identity"))
        else:
            for group in newsrc:
                if group.find(":")!=-1:
                    #this is a subscribed group
                    group_info=group.split(":")
                    group_name=group_info[0].strip()
                    group_read_ranges=group_info[1].strip()
                    if group_read_ranges.find("/")!=-1: #Xnews extension for kept articles
                        group_read_ranges,group_kept_ranges=group_read_ranges.split("/")
                    #group_read_list=self.extract_ranges(group_read_ranges)
                    group_first_unread=self.find_first_unread(group_read_ranges)
                    self.subscribe_group(group_name,group_first_unread,group_read_ranges,server_name,id_name)

    def retrieve_body(self,article_to_read,group,server_name=None):
        if not server_name: server_name=self.current_server    
        body=article_to_read.get_body()
        if not body:
            message,headerList,body,bodyRetrieved=self.connectionsPool[server_name].getBody(article_to_read.number,article_to_read.msgid,group)
            if headerList:
                article_to_read.parse_header_list(headerList)
            if bodyRetrieved:
                article_to_read.set_body('\n'.join(headerList+['']+body))
                body=article_to_read.get_body()
                article_to_read.marked_for_download=False
        return body

    def download_headers(self,group,first_unread,read_list,server_name):
        last_number=str(first_unread)
        #Here I deleted the controls I made on first_unread before I changed
        #the nntplib, it works with leafnode, I must test with other servers.
        first=int(first_unread)
        #Downloading headers
        self.main_win.progressbar.set_text(_("Fetching Headers"))
        self.main_win.progressbar.set_fraction(1/float(2))
        while gtk.events_pending():
            gtk.main_iteration(False)
        message,total_headers,last=self.connectionsPool[server_name].getHeaders(group,first)
        if last!=-1:
            last_number=str(last)
        self.main_win.statusbar.push(1,message)
        if total_headers:
            self.main_win.progressbar.set_text(_("Building Articles"))
        else:
            self.main_win.progressbar.set_text(_("No New Headers"))
        self.main_win.progressbar.set_fraction(2/float(2))
        while gtk.events_pending():
            gtk.main_iteration(False)
        
        self.art_db.createGroup(group)
        self.art_db.addHeaders(group,total_headers,server_name,self.connectionsPool,read_list)

        self.main_win.statusbar.push(1,_("Group subscribed"))
        self.main_win.progressbar.set_fraction(0)
        self.main_win.progressbar.set_text("")
        return last_number
        
    def subscribe_group(self,group_to_subscribe,first_unread,read_list,server_name,id_name):
        last=self.download_headers(group_to_subscribe,int(first_unread),read_list,server_name)
        self.art_db.removeSubscribed(group_to_subscribe)
        self.art_db.addSubscribed(group_to_subscribe,last,server_name,id_name)
        
        
      

    def delete_files(self):
        subscribed=self.art_db.getSubscribed()

        for group in subscribed_list:
            try:
                os.remove(os.path.join(self.wdir,"groups_info/",group[0]))
            except:
                pass
        try:
            os.remove(os.path.join(self.wdir,"groups_info/subscribed.sqlitedb"))
        except:
            pass


    def __init__(self,newsrc,main_win,configs,server_name):
        self.main_win=main_win
        self.configs=configs
        self.wdir=get_wdir()
        self.art_db=main_win.art_db
        
        #cleaning files
        #self.delete_files()

        #opening connection with server
        
        cp=ConfigParser.ConfigParser()
        cp.read(os.path.join(get_wdir(),"dats","servers.txt"))
        self.connectionsPool=dict()        
        for server in cp.sections():
            if cp.get(server,"nntp_use_ssl")=="True":
                self.connectionsPool[server]=SSLConnection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))
            else:
                self.connectionsPool[server]=Connection(cp.get(server,"server"),cp.get(server,"port"),cp.get(server,"auth"),cp.get(server,"username"),cp.get(server,"password"))


        #subscribing groups
        self.subscribe_groups(newsrc,server_name)

        #closing connection with server
        for connection in self.connectionsPool.itervalues():
            connection.closeConnection()


