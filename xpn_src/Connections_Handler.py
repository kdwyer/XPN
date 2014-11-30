import nntplib
import xpn_src.nntplib_ssl as nntplib_ssl
import smtplib
import sys
import time
import StringIO
import os
from urllib import quote as url_quote
from xpn_src.UserDir import get_wdir


def my_xover(self,start,end):
    """Process an XOVER command (optional server extension) Arguments:
    - start: start of range
    - end: end of range
    Returns:
    - resp: server response if successful
    - list: list of (art-nr, subject, poster, date,
                    id, references, size, lines,xref)"""

    resp, lines = self.longcmd('XOVER ' + start + '-' + end)
    xover_lines = []
    for line in lines:
        elem = line.split("\t")
        try:
            xover_lines.append((elem[0],
                                elem[1],
                                elem[2],
                                elem[3],
                                elem[4],
                                elem[5],
                                elem[6],
                                elem[7],
                                elem[8]))
        except IndexError:
            raise nntplib.NNTPDataError(line)
    return resp,xover_lines


class Connection:
    '''This class wraps an nntp connection.

    It has two types of methods, user-level methods and class-level methodos.
    The user is intended to use only user-level methods that astract nntp
    operation at a higher lever. Class-level methods are used internally
    also to implement user-level methods.

    User-level methods are: closeConnection, getBody, getHeaders, getXHDRHeaders, sendArticle

    Class-level methods are:__init__, _isUp, _tryConnection, _addLog, _enterGroup
   
    
    Attributes:
    serverConnection     : it is None or an nntplib.NNTP instance representing
                           the connection with the server
    serverAddress        : server address
    serverPort           : port number
    requireAuthentication: True if server requires authentication
    username             : username for the server
    password             : password for the server
    groupEntered         : the group we sent the command GROUP for
    '''
    
    def __init__(self,serverAddress,serverPort=119,requireAuthentication=False,username="",password=""):
        '''Class constructor'''
       
        self.serverConnection = None # when there is no connection with the server this attribute
                                     # should be None
        self.serverAddress = serverAddress
        self.serverPort = int(serverPort)
        self.requireAuthentication = requireAuthentication
        self.username = username
        self.password = password
        self.groupEntered= ""
        nntplib.NNTP.my_xover=my_xover

    def reInit(self,serverAddress,serverPort=119,requireAuthentication=False,username="",password=""):
        '''Reset the class attributes.

        It is useful when you change some attributes like server name and don't want to create
        a new object
        '''
        self.closeConnection()
        self.__init__(serverAddress,serverPort,requireAuthentication,username,password)
    
    def _isUp(self):
        '''Return the state of the connection.'''
        return self.serverConnection!=None
        
    def closeConnection(self):
        ''' Close connection and add a log of the operation.'''
        if self._isUp():
            self._addLog("QUIT",True)
            try:
                message=self.serverConnection.quit()
            except :
                message=str(sys.exc_info()[0])+","+str(sys.exc_info()[1])
            self.serverConnection=None
            self._addLog(message,False)
                
         
    def _addLog(self,message,is_command):
        ''' Adds an entry in server_logs.dat.

        Arguments:
        message    : is the entry to add
        is_command : if it is True we are adding a message sent to the server, else
                     we are adding a message received from the server
        '''
        
        try:
            f=open(os.path.join(get_wdir(),"server_logs.dat"),"a")
        except IOError:
            pass
        else:
            if is_command:
                f.write(time.ctime(time.time())+" :: >> "+message+"\n")
            else:
                f.write(time.ctime(time.time())+" :: << "+message+"\n")
            f.close()

            
    def _tryConnection(self):
        '''Tries to estabilish a connection with the server or check if it is still up.

        If self.serverConnection is None must set-up a new connection, else the connection
        could be still up, test it, and if it is down try to estabilish a new connection.

        Return: 
        message : you can use it to interact with the user.
        isUp : a boolean indicating the state of the connection
        '''
        if self.serverConnection==None:
            #we must set-up a new connection
            self.groupEntered=""
            try:
                if self.requireAuthentication=="True":
                    self._addLog("AUTHINFO USER "+self.username,True)
                    self._addLog("AUTHINFO PASS "+"".join(["*" for i in self.password]),True)
                self._addLog("MODE READER",True)
                self.serverConnection=nntplib.NNTP(self.serverAddress,port=self.serverPort,user=self.username,password=self.password,readermode=True)
            except :
                message=_("No connection with server : %s. Configure NNTP Server Address or try later.") % (self.serverAddress,)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                self.serverConnection=None
            else:
                message=_("Connection estabilished with server: %s") % (self.serverAddress,)
                self._addLog(self.serverConnection.getwelcome(),False)
            return message, self._isUp()
        else:
            #the connection probably is still up, let's test it
            try:
                # I use stat only to test if the connection is still up
                #self.serverConnection.stat("<>") # this stat seems to cause some problems to Hamster.
                #self.serverConnection.stat("")
                self.serverConnection.date() #devo vedere come risponde dopo il timeout
            except nntplib.NNTPPermanentError:
                # the connection is broken, I try to estabilish a new connection
                self.serverConnection=None
                message,isUp=self._tryConnection()
                return message,isUp
            #except nntplib.NNTPTemporaryError:
                # This exception is raised because the article <> doesn't exist
                # I haven't to do anything
            #    return "",True 
            except :
                #This is another type of exception, however we have problems with server
                message=_("No connection with server : %s. Configure NNTP Server Address or try later.") % (self.serverAddress,)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                self.serverConnection=None
                message,isUp=self._tryConnection()
                return message,isUp
            else:
                #the connection is active
                return "",True

    def _enterGroup(self,group,force=False):
        ''' Send GROUP command if it is needed.

        Arguments:
        group : the group to enter
        force : if force is True GROUP command is always sent
        
        Return:
        message : it can be used to interact with the user
        first   : first article in group
        last    : last article in group
        '''
        message,connectionIsUp=self._tryConnection()
        first=0
        last=0
        if connectionIsUp:
            if group!=self.groupEntered or force:
                #we have to send group command
                try:
                    self._addLog("GROUP "+group,True)
                    resp,count,first,last,name=self.serverConnection.group(group)
                except :
                    message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                    self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                else:
                    message=_("%s response : %s") % (self.serverAddress,resp)
                    self._addLog(resp,False)
                    self.groupEntered=group
        return message,first,last

    def getArticleNumber(self,group,msgid):
        '''Return the article number using the message-id to query the server'''
        number=-1
        header_list=[]
        message,first,last=self._enterGroup(group)
        if self._isUp():
            try:
                resp,number,msgid,header_list=self.serverConnection.head(msgid)
            except :
                message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
            else:
                message=_("%s response : %s") % (self.serverAddress,resp)
                self._addLog(resp,False)
            if int(number)==0:
                #some servers send a 0 when called with the message-id
                for header in header_list:
                    if header.lower().startswith("xref:"): 
                        try: number=int(header.split(group+":")[1].split()[0].strip())
                        except : number= -1
        return message,int(number)

                
            
        
        
    def getBody(self,number,msgid,group):
        '''Retrieve the body of the article.

        First need to enter the group, then retrieve with an HEAD the command
        the headers list and then retrieve the body.

        Arguments:
        number      : article number
        msgid       : article message-id
        group       : the group the article is in
        
        Return:
        message       : it can be used to interact with the user
        headerList    : the headers list, XPN uses it with xpn_src.Article.parse_header_list
        rawBody       : the body retrieved (or phantom article). XPN uses it with xpn_src.Article.set_body
                        (not in the case it is the phantom article)
        bodyRetrieved : True if the bosy has been successfully retrieved from the server (so rawBody isn't
                        [] or phantom article)
        '''
        bodyRetrieved=False
        headerList=[]
        rawBody=[]
        message,first,last=self._enterGroup(group)
        if self._isUp():
            try:
                self._addLog("ARTICLE "+number,True)
                resp,number,id,rawBody=self.serverConnection.article(number)
            except nntplib.NNTPTemporaryError:
                message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                if str(sys.exc_info()[1])[:1]=="4":
                    #article is not on the server, we use a phantom article
                    link=r"http://groups.google.com/groups?selm="+url_quote(msgid[1:-1])
                    rawBody=(_("Server Error: ")+str(sys.exc_info()[1]),"",_("You can try on Google:"),"",link)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
            except :
                #every other type of errors
                message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
            else:
                self._addLog(resp,False)
                message=_("%s response : %s") % (self.serverAddress,resp)
                ind=rawBody.index("")
                headerList=rawBody[:ind]
                rawBody=rawBody[ind+1:]
                bodyRetrieved=True
        return message,headerList,rawBody,bodyRetrieved 
        
         
    def getHeaders(self,group,first,last=None,count=None):
        '''Retrieve Headers in a given range.

        Arguments:
        group : the group to download the headers for
        first : the first article to consider
        last  : tha last article to consider, if it is None last will be the last article on group
        count : the number of article to headers, the 'count' newest headers will be downloaded.
                If you are subscribing the group, first=0 and then it is ignored.
                If you also pass the 'last' argument 'count' will be ignored

        Return:
        message     : it can be used to interact with the user
        headersList : a list of lists, every element is a list containing the headers of an article
        lastOnServer : last number on server
        '''
        headersList=[]
        lastOnServer=-1
        message,group_first,group_last=self._enterGroup(group,True)
        argumentLast=last
        if not last: last=group_last
        if count and not argumentLast: 
            first,last=max(int(group_last)-count+1,first),group_last
        if first<0: first=0
        if int(first)<=int(last):
            if self._isUp():
                try:
                    self._addLog("XOVER "+str(first)+"-"+str(last),True)
                    resp,headersList=self.serverConnection.my_xover(str(first),str(last))
                except :
                    message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                    self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                else:
                    lastOnServer=int(group_last)
                    message=_("%s response : %s") % (self.serverAddress,resp)
                    self._addLog(resp,False)
        return message,headersList,lastOnServer
        
    def getXHDRHeaders(self,group,headerName,first,last=None,count=None):
        '''Retrieve a given Header in a given range.

        Arguments:
        group     : the group to download the headers for
        headerName: the header to download
        first     : the first article to consider
        last      : tha last article to consider, if it is None last will be the last article on group
        count     : the number of article to headers, the 'count' newest headers will be downloaded,
                    'first' is ignored in this case. If you also pass the 'last' argument 'count' will be 
                    ignored

        Return:
        message      : it can be used to interact with the user
        headerList   : a list of the header values
        '''

        headerList=[]
        lastOnServer=-1
        message,group_first,group_last=self._enterGroup(group,True)
        argumentLast=last
        if not last: last=group_last
        if count and not argumentLast: first,last=int(group_last)-count+1,group_last
        if first<0: first=0
        if int(first)<=int(last):
            if self._isUp():
                try:
                    self._addLog("XHDR "+headerName+" "+str(first)+"-"+str(last),True)
                    resp,headerList=self.serverConnection.xhdr(headerName,str(first)+"-"+str(last))
                except :
                    message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                    self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                else:
                    lastOnServer=int(group_last)
                    message=_("%s response : %s") % (self.serverAddress,resp)
                    self._addLog(resp,False)
        return message,headerList

    def sendArticle(self,article):
        '''Send an article to the Server.

        Arguments:
        article : a string representing a well-formed usenet article
        
        Returns:
        message       : it can be used to interact with the user
        articlePosted : True if the article was correctly sent
        '''
        message,connectionIsUp=self._tryConnection()
        articlePosted=False
        if connectionIsUp:
            fileArticle=StringIO.StringIO(article)
            try:
                self._addLog("POST", True)
                resp=self.serverConnection.post(fileArticle)
            except :
                message=_("Server error: %s") % (str(sys.exc_info()[1]),)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                fileArticle.close()
            else:
                fileArticle.close()
                self._addLog(resp,False)
                message=_("%s response : %s") % (self.serverAddress,resp)
                articlePosted=True
        return message,articlePosted

class SSLConnection(Connection):
    def __init__(self,serverAddress,serverPort=563,requireAuthentication=False,username="",password=""):
        '''Class constructor'''
       
        self.serverConnection = None # when there is no connection with the server this attribute
                                     # should be None
        self.serverAddress = serverAddress
        self.serverPort = int(serverPort)
        self.requireAuthentication = requireAuthentication
        self.username = username
        self.password = password
        self.groupEntered= ""
        nntplib_ssl.NNTP_SSL.my_xover=my_xover


    def reInit(self,serverAddress,serverPort=563,requireAuthentication=False,username="",password=""):
        '''Reset the class attributes.

        It is useful when you change some attributes like server name and don't want to create
        a new object
        '''
        self.closeConnection()
        self.__init__(serverAddress,serverPort,requireAuthentication,username,password)

    def _tryConnection(self):
        '''Tries to estabilish a connection with the server or check if it is still up.

        If self.serverConnection is None must set-up a new connection, else the connection
        could be still up, test it, and if it is down try to estabilish a new connection.

        Return: 
        message : you can use it to interact with the user.
        isUp : a boolean indicating the state of the connection
        '''
        if self.serverConnection==None:
            #we must set-up a new connection
            self.groupEntered=""
            try:
                if self.requireAuthentication=="True":
                    self._addLog("AUTHINFO USER "+self.username,True)
                    self._addLog("AUTHINFO PASS "+"".join(["*" for i in self.password]),True)
                self._addLog("MODE READER",True)
                self.serverConnection=nntplib_ssl.NNTP_SSL(self.serverAddress,port=self.serverPort,user=self.username,password=self.password,readermode=True)
            except :
                message=_("No connection with server : %s. Configure NNTP Server Address or try later.") % (self.serverAddress,)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                self.serverConnection=None
            else:
                message=_("Connection estabilished with server: %s") % (self.serverAddress,)
                self._addLog(self.serverConnection.getwelcome(),False)
            return message, self._isUp()
        else:
            #the connection probably is still up, let's test it
            try:
                # I use stat only to test if the connection is still up
                #self.serverConnection.stat("<>") # this stat seems to cause some problems to Hamster.
                self.serverConnection.stat("")
            except nntplib.NNTPPermanentError:
                # the connection is broken, I try to estabilish a new connection
                self.serverConnection=None
                message,isUp=self._tryConnection()
                return message,isUp
            except nntplib.NNTPTemporaryError:
                # This exception is raised because the article <> doesn't exist
                # I haven't to do anything
                return "",True 
            except :
                #This is another type of exception, however we have problems with server
                message=_("No connection with server : %s. Configure NNTP Server Address or try later.") % (self.serverAddress,)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                self.serverConnection=None
                message,isUp=self._tryConnection()
                return message,isUp
            else:
                #This is only a fallback this leaf shouldn't never be reached
                return "",True


class SMTPConnection:
    '''This class wraps an SMTP Connection'''
    def __init__(self,serverAddress,serverPort=25,requireAuthentication=False,username="",password=""):
        self.serverConnection = None # when there is no connection with the server this attribute
                                     # should be None
        self.serverAddress = serverAddress
        self.serverPort = int(serverPort)
        self.requireAuthentication = requireAuthentication
        self.username = username
        self.password = password

    def reInit(self,serverAddress,serverPort=25,requireAuthentication=False,username="",password=""):
        '''Reset the class attributes.

        It is useful when you change some attributes like server name and don't want to create
        a new object
        '''
        self.closeConnection()
        self.__init__(serverAddress,serverPort,requireAuthentication,username,password)
    
    def _isUp(self):
        '''Return the state of the connection.'''
        return self.serverConnection!=None
        
    def closeConnection(self):
        ''' Close connection and add a log of the operation.'''
        if self._isUp():
            self._addLog("QUIT",True)
            try:
                self.serverConnection.quit()
            except :
                message=str(sys.exc_info()[0])+","+str(sys.exc_info()[1])
            else:
                message=_("Connection closed")
            self.serverConnection=None
            self._addLog(message,False)
                
         
    def _addLog(self,message,is_command):
        ''' Adds an entry in server_logs.dat.

        Arguments:
        message    : is the entry to add
        is_command : if it is True we are adding a message sent to the server, else
                     we are adding a message received from the server
        '''
        
        try:
            f=open(os.path.join(get_wdir(),"server_logs.dat"),"a")
        except IOError:
            pass
        else:
            if is_command:
                f.write(time.ctime(time.time())+" ::[SMTP] >> "+message+"\n")
            else:
                f.write(time.ctime(time.time())+" ::[SMTP] << "+message+"\n")
            f.close()

    def _tryConnection(self):
        '''Tries to estabilish a connection with the server or check if it is still up.

        If self.serverConnection is None must set-up a new connection, else the connection
        could be still up, test it, and if it is down try to estabilish a new connection.

        Return: 
        message : you can use it to interact with the user.
        isUp : a boolean indicating the state of the connection'''
        message=""
        if self.serverConnection==None:
            try:
                self.serverConnection = smtplib.SMTP(self.serverAddress,self.serverPort)
                if self.requireAuthentication=="True":
                    self._addLog("LOGIN "+self.username+" "+"".join(["*" for i in self.password]),True)
                    self.serverConnection.login(self.username,self.password)
            except:
                message=_("No connection with server : %s. Configure SMTP Server Address or try later.") % (self.serverAddress,)
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
                self.serverConnection=None
            else:
                message=_("Connection estabilished with: %s")  % (self.serverAddress,)
                self._addLog(message,False)
        return message,self._isUp()

    def sendMail(self,from_name,to_name,mail):
        ''' Send a well formed Email.

        Arguments:
        from_name: sender address
        to_name  : destination address
        mail     : a well formed e-mail

        Return:
        message  : you can use it to interact with the user.
        mailSent : True if the mail was correctly sent'''
        
        message,connectionIsUp=self._tryConnection()
        mailSent=False
        if connectionIsUp:
            try:
                self._addLog("SENDMAIL",True)
                self.serverConnection.sendmail(from_name,to_name,mail)
            except:
                message=_("Unable to send the message. Control Server Logs.")
                self._addLog(str(sys.exc_info()[0])+","+str(sys.exc_info()[1]),False)
            else:
                message=_("Email Sent")
                self._addLog(message,False)
                mailSent=True
        return message,mailSent
