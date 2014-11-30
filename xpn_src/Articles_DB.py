try:                # >= Python 2.5
    import sqlite3 as sqlite
except ImportError: # Python 2.4
    try:
        from pysqlite2 import dbapi2 as sqlite
    except ImportError:
        print "you need to install PySqlite2 and SQlite"
        sys.exit()
import os,shutil
import cPickle
from email.Utils import parsedate_tz,mktime_tz
import time
from xpn_src.UserDir import get_wdir
from xpn_src.Article import Article
from xpn_src.Config_File import Config_File
from xpn_src.Score import Score_Rules

class Groups_DB:
    '''This class wraps the interface to the groups DataBase'''
    def __init__(self):
        '''Class constructor'''
        self._wdir=get_wdir()
        self._base_path=os.path.join(self._wdir,"groups_info/")
        self._conf=Config_File()
        self._configs=self._conf.get_configs()
    
    def createList(self,groups_list,server_name,file_name=""):
        '''Create the groups list DB'''
        if file_name:
            try: os.remove(os.path.join(self._base_path,file_name))
            except: pass
            conn=sqlite.connect(os.path.join(self._base_path,file_name))
        else:
            try: os.remove(os.path.join(self._base_path,server_name+".groups.sqlitedb"))
            except: pass
            conn=sqlite.connect(os.path.join(self._base_path,server_name+".groups.sqlitedb"))
        c=conn.cursor()
        c.execute('''create table groups (group_name TEXT, 
                                          mode TEXT, 
                                          server_name TEXT, 
                                          PRIMARY KEY(group_name,server_name))''')
        for group in groups_list:
            c.execute(''' insert into groups values(?,?,?)''',group)
        conn.commit()
        conn.close()
    
    def getList(self,file_name):
        '''Get the groups list'''
        conn=sqlite.connect(os.path.join(self._base_path,file_name))
        c=conn.cursor()
        groups_list=c.execute('''select * from groups''').fetchall()
        return groups_list
        conn.close()
        
    

class Articles_DB:
    '''This class wraps the interface to the articles DataBase.

    It has two types of methods, user-level methods and class-level methodos.
    The user is intended to use only user-level methods.
    Class-level methods are used internally also to implement user-level methods.
    
    '''
    def __init__(self,groups=[]):
        '''Class constructor
        it performs some initializations, and open all the DB connections
        
        Arguments:
        groups: a list of groups
        '''
        self._wdir=get_wdir()
        self._base_path=os.path.join(self._wdir,"groups_info/")
        self._conf=Config_File()
        self._configs=self._conf.get_configs()
        self._connections=dict()
        self._openSubscribed()
        for group in groups : self._openGroup(group)

    def _getCursor(self,group):
        '''Get the cursor for the group'''
        return self._connections[group]["cursor"]
    
    def _getConnection(self,group):
        '''Get the cursor for the group'''
        return self._connections[group]["conn"]

    def _openGroup(self,group):
        '''Open the connection to the group DB and create a cursor'''
        conn = sqlite.connect(os.path.join(self._base_path,group,group+".sqlitedb"))
        c=conn.cursor()
        c.execute('''pragma synchronous = OFF;''')
        self._connections[group]={"conn":conn,"cursor":c}
    
    def _closeGroup(self,group):
        '''Close the connection to the group DB'''
        self._connections[group]["conn"].close()
        
    
    def closeGroups(self,groups=[]):
        '''Close all the connections, if groups is given, close only listed groups'''
        if groups: 
            for group in groups:
                self._closeGroup(group)
        else:
            for group in self._connections.iterkeys():
                self._closeGroup(group)
    
    def _commitGroups(self,groups=[]):
        '''Commit changes in all the groups'''
        if groups: 
            for group in groups:
                self._getConnection(group).commit()

        else:
            for group in self._connections.iterkeys():
                self._getConnection(group).commit()

    
    def addGroups(self,groups):
        '''Open the connections for the groups DB and create cursors'''
        for group in groups:
            self._openGroup(group)
    
    def _openSubscribedConn(self):
        conn = sqlite.connect(os.path.join(self._base_path,"subscribed.sqlitedb"))
        c=conn.cursor()
        self._subscribedConnection={"conn":conn,"cursor":c}
    
    def _getSubscribedConnection(self):
        return self._subscribedConnection["conn"]
    
    def _getSubscribedCursor(self):
        return self._subscribedConnection["cursor"]
        
    def _openSubscribed(self):
        '''Open the connection to the subscribed DB and create a cursor'''
        try: #Test if the file already exists
            f=open(os.path.join(self._base_path,"subscribed.sqlitedb"),"rb")
        except IOError:
            self._openSubscribedConn()
            self._createSubscribed()
        else:
            self._openSubscribedConn()
            
    def _createSubscribed(self):
        '''Create the table for a subscribed groups'''   
        
        c=self._getSubscribedCursor()
        conn=self._getSubscribedConnection()
        c.execute('''create table subscribed (group_name TEXT, 
                                              last TEXT, 
                                              server_name TEXT, 
                                              id_name TEXT,
                                              PRIMARY KEY(group_name))''')
        
        conn.commit()
    
    def addSubscribed(self,group,last,server_name,id_name):
        '''Add a subscribed group'''
        c=self._getSubscribedCursor()
        conn=self._getSubscribedConnection()
        c.execute('''insert into subscribed values (?,?,?,?)''',(group,last,server_name,id_name))
        conn.commit()
        
    def removeSubscribed(self,group):
        '''Remove a subscribed group'''
        c=self._getSubscribedCursor()
        conn=self._getSubscribedConnection()
        removed=bool(len(c.execute('''select * from subscribed where group_name=?''',(group,)).fetchall()))
        c.execute('''delete from subscribed where group_name=?''',(group,))
        conn.commit()
        return removed
    
    def getSubscribed(self):
        '''Get subscribed list'''
        c=self._getSubscribedCursor()
        conn=self._getSubscribedConnection()
        c.execute('''select * from subscribed''')
        subscribed=c.fetchall()
        subscribed= [list(group) for group in subscribed]
        return subscribed
    
    def updateSubscribed(self,subscribed):
        '''Update Subscribed table'''
        c=self._getSubscribedCursor()
        conn=self._getSubscribedConnection()
        for group in subscribed:
            c.execute('''update subscribed set last=?, 
                                               server_name =?, 
                                               id_name =? where group_name=? ''',(group[1],group[2],group[3],group[0]))
        conn.commit()

    def closeSubscribed(self):
        '''Close subscribed connection'''
        c=self._getSubscribedCursor()
        c.execute("""vacuum""")
        self._subscribedConnection["conn"].close()
    
    def getWatched(self,group):
        '''Get the watched mids in the group'''
        c=self._getCursor(group)
        result=c.execute("select msgid from articles where watched='1'")
        result=[item[0] for item in result]
        return result
        
    def getIgnored(self,group):
        '''Get the watched mids in the group'''
        c=self._getCursor(group)
        result=c.execute("select msgid from articles where ignored='1'")
        result=[item[0] for item in result]
        return result
        
    def inIgnored(self,mid,group,cursor=None):
        '''True if mid is ignored'''
        c=self._getCursor(group)
        result=len(c.execute("select * from articles where ignored='1' and msgid=?",(mid,)).fetchall())!=0
        return result
        
        
    def inWatched(self,mid,group,cursor=None):
        '''True if mid is watched'''
        c=self._getCursor(group)
        result=len(c.execute("select * from articles where watched='1' and msgid=?",(mid,)).fetchall())!=0
        return result
    
    def getArticlesNumbers(self,group):
        '''Return the number of the articles and the unreads number'''
        c=self._getCursor(group)
        total=len(c.execute("select msgid from articles").fetchall())
        unread_number=len(c.execute("select msgid from articles where read='0'").fetchall())
        return total,unread_number
        
    def retrieveBody(self,article_to_read,group,server_name,connectionsPool,doCommit=True):
        '''Retrieve the body of the article
        
        Arguments:
        article_to_read: the xpn_article
        group          : article group
        server_name    : the name of the server to use
        connectionsPool: the dict of the NNTP connections
        '''
        
        body=article_to_read.get_body()
        bodyRetrieved=True
        message=""
        raw_body=""
        if not body:
            c=self._getCursor(group)
            c.execute('''select raw_body from bodies where msgid=? and number=?''',(article_to_read.msgid,article_to_read.number))
            try: raw_body= c.fetchall()[0][0]
            except: raw_body=""
            if not raw_body:
                message,headerList,body,bodyRetrieved=connectionsPool[server_name].getBody(article_to_read.number,article_to_read.msgid,group)
                if headerList:
                    article_to_read.parse_header_list(headerList)
                if bodyRetrieved:
                    raw_body='\n'.join(headerList+['']+body)
                    article_to_read.set_body(raw_body)
                    body=article_to_read.get_body()
                    article_to_read.marked_for_download=False
                    self.updateArticle(group,article_to_read,doCommit)
                    self._insertBody(group,article_to_read,doCommit)
            else:
                raw_body_list=raw_body.split("\n")
                ind=raw_body_list.index("")
                header_list=raw_body_list[:ind]
                article_to_read.parse_header_list(header_list,True)
                article_to_read.set_body(raw_body,True)
                body=article_to_read.get_body()
                article_to_read.marked_for_download=False
                self.updateArticle(group,article_to_read,doCommit)
        return body,bodyRetrieved,message   
    
    def getBodyFromDB(self,group,article):
        '''Get the body of the article from the DB if it is available'''
        c=self._getCursor(group)
        c.execute("select raw_body from bodies where msgid=? and number=?",(article.msgid,article.number))
        body=None
        try: raw_body= c.fetchall()[0][0]
        except: raw_body=""
        if raw_body:
            raw_body_list=raw_body.split("\n")
            ind=raw_body_list.index("")
            header_list=raw_body_list[:ind]
            article.parse_header_list(header_list,True)
            article.set_body(raw_body,True)
            body=article.get_body()
        return body

    def deleteArticle(self,group,xpn_article,doCommit=True):
        '''Delete the article from the  DB'''
        c=self._getCursor(group)
        c.execute("""delete from articles where msgid=?""",(xpn_article.msgid,))
        if doCommit:
            conn=self._getConnection(group)
            conn.commit()

    def updateArticle(self,group,xpn_article,doCommit=True):
        '''Update the article in the DB.
        
        Only fields that can change are updated
        '''
        c=self._getCursor(group)
        c.execute("""update articles set    has_body =?,
                                            score =?,
                                            marked_for_download =?,
                                            kept =?,
                                            read =?,
                                            watched =?,
                                            ignored =?,
                                            fg_color =?,
                                            bg_color =? where msgid=?""",
              (xpn_article.has_body,
              xpn_article.score,
              xpn_article.marked_for_download,
              xpn_article.keep,
              xpn_article.is_read,
              xpn_article.watch,
              xpn_article.ignore,
              xpn_article.fg_color,
              xpn_article.bg_color,
              xpn_article.msgid))

        if doCommit:
            conn=self._getConnection(group)
            conn.commit()


    def insertArticle(self,group,xpn_article,doCommit=True):
        '''Insert the article in the DB.'''
        c=self._getCursor(group)
        try:
            c.execute("""insert into articles values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                              (xpn_article.msgid,
                              xpn_article.number,
                              xpn_article.subj,
                              xpn_article.from_name,
                              xpn_article.date,
                              xpn_article.secs,
                              xpn_article.ref,
                              xpn_article.bytes,
                              xpn_article.lines,
                              xpn_article.xref,
                              xpn_article.original_group,
                              xpn_article.has_body,
                              xpn_article.score,
                              xpn_article.marked_for_download,
                              xpn_article.keep,
                              xpn_article.is_read,
                              xpn_article.watch,
                              xpn_article.ignore,
                              xpn_article.fg_color,
                              xpn_article.bg_color))
        except sqlite.IntegrityError:
            print "Found Duplicated Article ... skipping"

        if doCommit:
            conn=self._getConnection(group)
            conn.commit()

    def _insertBody(self,group,xpn_article,doCommit=True):
        '''Insert the body in the bodies DB'''
        c=self._getCursor(group)
        raw_body=xpn_article.get_raw(True)
        if raw_body:
            c.execute('''insert into bodies values (?,?,?)''',(xpn_article.msgid,xpn_article.number,raw_body))

        if doCommit:
            conn=self._getConnection(group)
            conn.commit()

    def markGroupForDownload(self,group):
        '''Mark the whole group for dowload'''
        c=self._getCursor(group)
        c.execute("""update articles set marked_for_download='1' where has_body='0'""")
        conn=self._getConnection(group)
        conn.commit()

    def markGroupRead(self,group,read):
        '''Mark the whole group read or unread'''
        c=self._getCursor(group)
        c.execute('''update articles set read=?''',(read,))
        conn=self._getConnection(group)
        conn.commit()

    def keepGroup(self,group):
        '''Keep or unKeep the whole group
        The first query is used to retrieve the keep status of the first article
        it will be used as reference for all the other articles.
        That's because I don't know if I have to keep or unkeep
        '''
        c=self._getCursor(group)
        keep=not bool(int(c.execute("""select kept from articles limit 1""").fetchall()[0][0]))
        c.execute("""update articles set kept=?""",(keep,))
        conn=self._getConnection(group)
        conn.commit()
        
        
    def _buildQuery(self,show_bools,search_type=None,text=None):
        show_read_articles,show_unread_articles,show_kept_articles,show_unkept_articles,show_watched_articles,show_ignored_articles,show_unwatchedignored_articles,show_score_neg_articles,show_score_zero_articles,show_score_pos_articles,show_threads,show_all_read_threads=show_bools
        
        pieces=[]
        nothing_to_show=False
        
        if search_type=="bodies.raw_body" and text:
            pieces.append(" ") #fake piece I need to prevent adding another where
            base_query="""select articles.msgid,
                                 articles.number, 
                                 articles.subject,
                                 articles.from_name,
                                 articles.art_date,
                                 articles.secs,
                                 articles.ref,
                                 articles.bytes,
                                 articles.lines,
                                 articles.xref,
                                 articles.group_name,
                                 articles.has_body,
                                 articles.score,
                                 articles.marked_for_download,
                                 articles.kept,
                                 articles.read,
                                 articles.watched,
                                 articles.ignored,
                                 articles.fg_color,
                                 articles.bg_color from articles,bodies where articles.msgid=bodies.msgid and """
        else: base_query="select * from articles "


        def add_piece(piece,addOR=False):
            if not pieces: pieces.append("where")
            if len(pieces)>1:
                if addOR: pieces.append("or")
                else:     pieces.append("and")
            pieces.append(piece)

            
        if show_read_articles and not show_unread_articles      : add_piece("read='1'")
        elif not show_read_articles and show_unread_articles    : add_piece("read='0'")
        elif not show_read_articles and not show_unread_articles: nothing_to_show=True

        if show_kept_articles and not show_unkept_articles      : add_piece("kept='1'")
        elif not show_kept_articles and show_unkept_articles    : add_piece("kept='0'")
        elif not show_kept_articles and not show_unkept_articles: nothing_to_show=True

        if   not show_unwatchedignored_articles and not show_watched_articles and not show_ignored_articles : nothing_to_show=True
        elif not show_unwatchedignored_articles and not show_watched_articles and     show_ignored_articles : add_piece("ignored='1'")
        elif not show_unwatchedignored_articles and     show_watched_articles and not show_ignored_articles : add_piece("watched='1'")
        elif not show_unwatchedignored_articles and     show_watched_articles and     show_ignored_articles : add_piece("(watched='1' OR ignored='1')")
        elif     show_unwatchedignored_articles and not show_watched_articles and not show_ignored_articles : add_piece("watched='0' and ignored='0'")
        elif     show_unwatchedignored_articles and not show_watched_articles and     show_ignored_articles : add_piece("watched='0'")
        elif     show_unwatchedignored_articles and     show_watched_articles and not show_ignored_articles : add_piece("ignored='0'")
        


        if show_score_neg_articles and not show_score_pos_articles and not show_score_zero_articles : add_piece("score<0")
        elif show_score_neg_articles and show_score_pos_articles and not show_score_zero_articles : add_piece("score!=0")
        elif show_score_neg_articles and not show_score_pos_articles and show_score_zero_articles : add_piece("score<=0")
        elif not show_score_neg_articles and not show_score_pos_articles and not show_score_zero_articles : nothing_to_show=True
        elif not show_score_neg_articles and not show_score_pos_articles and show_score_zero_articles: add_piece("score=0")
        elif not show_score_neg_articles and show_score_pos_articles and not show_score_zero_articles: add_piece("score>0")
        elif not show_score_neg_articles and show_score_pos_articles and  show_score_zero_articles: add_piece("score>=0")
        
        if search_type and text: add_piece(search_type+""" like '%"""+text+"""%'""")


        if nothing_to_show: query="select * from articles where 1=0"
        else: query=base_query+" ".join(pieces)
        return query

    def getArticles(self,group,show_bools=[],sort_by_num=False,search_type=None,text=None):
        '''Return all the articles in the group in form of xpn_articles
        
        It is a generator.
        '''
        c=self._getCursor(group)

        if show_bools:
            query=self._buildQuery(show_bools,search_type,text)
        else:
            query="select * from articles"
        if sort_by_num: query=query+" order by number"
        
        headers=c.execute(query).fetchall()
        for article_header in headers:
            msgid,number,subject,from_name,date,secs,ref,bytes,lines,xref,group,has_body,score,marked_for_download,kept,read,watched,ignored,fg_color,bg_color=article_header
            xpn_article=Article(number,msgid,from_name,ref,subject,date,self._configs["fallback_charset"],group,xref,bytes,lines,True)
            xpn_article.score=int(score)
            xpn_article.marked_for_download=bool(int(marked_for_download))
            xpn_article.keep=bool(int(kept))
            xpn_article.is_read=bool(int(read))
            xpn_article.watch=bool(int(watched))
            xpn_article.ignore=bool(int(ignored))
            xpn_article.fg_color=fg_color
            xpn_article.bg_color=bg_color
            xpn_article.has_body=bool(int(has_body))
            yield xpn_article

    
    def createGroup(self,group):
        '''Create the table for a new group'''
        try: self.closeGroups((group,))
        except:pass
        try: shutil.rmtree(os.path.join(self._base_path,group))
        except: pass
        os.makedirs(os.path.join(self._base_path,group))     
        
        self._openGroup(group)
        c=self._getCursor(group)
        conn=self._getConnection(group)
        c.execute('''create table articles (msgid TEXT, 
                                            number TEXT, 
                                            subject TEXT,
                                            from_name TEXT,
                                            art_date DATE,
                                            secs INTEGER,
                                            ref TEXT,
                                            bytes TEXT,
                                            lines TEXT,
                                            xref TEXT,
                                            group_name TEXT,
                                            has_body TEXT,
                                            score INTEGER,
                                            marked_for_download TEXT,
                                            kept TEXT,
                                            read TEXT,
                                            watched TEXT,
                                            ignored TEXT,
                                            fg_color TEXT,
                                            bg_color TEXT,
                                            PRIMARY KEY (msgid,number));''')
        c.execute('''create trigger delete_article before delete on articles
                     begin
                        delete from bodies where msgid=OLD.msgid and number=OLD.number;
                     end;''')
        c.execute('''create index watched_index on articles(watched);''')
        c.execute('''create index ignored_index on articles(ignored);''')
        c.execute('''create index read_index on articles(read);''')
        c.execute('''create index kept_index on articles(kept);''')
        c.execute('''create index marked_index on articles(marked_for_download);''')       
        c.execute('''create table bodies (msgid TEXT, 
                                          number TEXT,
                                          raw_body TEXT,
                                          PRIMARY KEY (msgid,number));''')
        conn.commit()

    def _isInReadList(self,number,L):
        if L!="":
            intervals=L.split(",")
            for interval in intervals:
                if "-" in interval:
                    #this is a range
                    start,stop=int(interval.split("-")[0]),int(interval.split("-")[1])
                    if (number <= stop) and (number >=start):
                        return True
                else:
                    #this is a single number
                    if number == int(interval):
                        return True
            return False


    def _applyRules(self,xpn_article,group,score_rules,server_name,connectionsPool,update=False,read_list=""):
        '''Apply rules to the article and add it to the DB
        
        Arguments:
        article_to_read: the xpn_article
        group          : article group
        score_rules    : score_rules object
        server_name    : the name of the server to use
        connectionsPool: the dict of the NNTP connections
        update         : true if the article is already in the DB
        read_list      : list of read articles, it is used when resuming a newsrc file
        '''
        
        c=self._getCursor(group)
        try:
            index=xpn_article.ref.rindex("<")
        except ValueError:
            last_ref=""
        else:
            last_ref=xpn_article.ref[index:]
        #applying score rules
        score=score_rules.apply_score_rules(xpn_article,group)
        xpn_article.set_score(score)
        #applying score actions
        xpn_article,actions=score_rules.apply_action_rules(xpn_article,group)
        #save only the last mid of references:
        #xpn_article.ref=last_ref   #with this operation Reapplying rules doesn't work correctly
                                    #I loose the othere mids in references
        if not "kill" in actions:
            to_ignore    = self.inIgnored(last_ref,group,c)
            to_watch     = self.inWatched(last_ref,group,c)
            to_mark_read = self._isInReadList(int(xpn_article.number),read_list)
            raw_body="None"
            if ((self._configs["download_bodies"]=="True" and not "markread" in actions) or ("retrieve" in actions) or (to_watch)) and not (to_ignore):
                body,bodyRetrieved,message=self.retrieveBody(xpn_article,group,server_name,connectionsPool,False)
            if to_ignore:
                xpn_article.is_read=True
                xpn_article.ignore=True
                xpn_article.watch=False
            if to_watch:
                xpn_article.watch=True
                xpn_article.ignore=False
            if to_mark_read:
                xpn_article.is_read=True
            if update:
                self.updateArticle(group,xpn_article,False)
            else:
                self.insertArticle(group,xpn_article,False)
            #self._getConnection(group).commit()
        else:
            if update:
                self.deleteArticle(group,xpn_article,True)

    def addHeaders(self,group,total_headers,server_name,connectionsPool,read_list=""):
        '''Add articles to the DB
        
        Arguments:
        group          : group name
        total_headers  : the list of headers retrieved with XOVER
        server_name    : the name of the server to use
        connectionsPool: the dict of the NNTP connections
        '''
        #t1=time.time()
        c=self._getCursor(group)        
        #print "pragma: ",c.execute('''pragma synchronous;''').fetchall()

        score_rules=Score_Rules()
        for headers in total_headers:
            number,subject,from_name,date,msgid,references,bytes,lines,xref=headers
            xpn_article=Article(number,msgid,from_name,references,subject,date,self._configs["fallback_charset"],group,xref,bytes,lines)
            self._applyRules(xpn_article,group,score_rules,server_name,connectionsPool,False,read_list)
        self._getConnection(group).commit()
        #t2=time.time()
        #print "Tempo per aggiungere Header: ",t2-t1

        
    def reapply_rules(self,group,server_name,connectionsPool):
        '''Reapply scoring and actions rules
        
        Arguments:
        group          : group name
        total_headers  : the list of headers retrieved with XOVER
        server_name    : the name of the server to use
        connectionsPool: the dict of the NNTP connections
        '''
        
        
        sorted=[]
        for xpn_article in self.getArticles(group):
            sorted.append((xpn_article.secs,xpn_article))
        
        sorted.sort()

        score_rules=Score_Rules()
        for secs,xpn_article in sorted:
            #reset the article
            #xpn_article.reset_article_score_actions()
            self._applyRules(xpn_article,group,score_rules,server_name,connectionsPool,True)
        self._getConnection(group).commit()


    def purgeGroups(self):
        purge_read_limit=int(self._configs["purge_read"])
        purge_read_limit_secs=purge_read_limit*24*60*60
        purge_unread_limit=int(self._configs["purge_unread"])
        purge_unread_limit_secs=purge_unread_limit*24*60*60

        time_now=mktime_tz(parsedate_tz(time.ctime()))

        
        subscribed=self.getSubscribed()

        for group in subscribed:

            c=self._getCursor(group[0])
            conn=self._getConnection(group[0])
            
            
            if purge_read_limit_secs >0:
                c.execute("""delete from articles where secs < ? and read='1' and kept='0'""",(time_now-purge_read_limit_secs,))
                conn.commit()
            if purge_unread_limit_secs >0:
                c.execute("""delete from articles where secs < ? and read='0' and kept='0'""",(time_now-purge_unread_limit_secs,))
                conn.commit()
            
            c.execute("""vacuum""")
            conn.commit()
            
            yield group[0]




