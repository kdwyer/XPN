import threading, Queue, sys, cPickle, socket, time, os
from xpn_src.UserDir import get_wdir


class ListThread(threading.Thread):
    def __init__(self, server,server_name):
        threading.Thread.__init__(self)
        self.server = server
        self.server_name=server_name
        self.groups_found = 0
        self.lock = threading.Lock()
        self.queue = Queue.Queue()
    
    def add_log(self,message,is_command):
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
            
    def run(self):
        try:
            self.add_log("LIST",True)
            resp, list = self.server.list()
            self.queue.put(["Connected",resp])
        except socket.error, e:
            self.queue.put(["Server error","Server error: "+str(e), str(e)])
        except:
            self.queue.put(["Server error","Server error: "+str(sys.exc_info()[1]),
                            str(sys.exc_info()[0])+","+str(sys.exc_info()[1])+"\n" \
                            +self.server.quit()
                                ])
        else:
            list = [[unicode(list[i][0],"iso-8859-1","replace").encode("us-ascii","replace"),list[i][3],self.server_name] for i in xrange(len(list))]
            self.queue.put(["Finished Listing"])
            self.queue.put(list)
            pass
