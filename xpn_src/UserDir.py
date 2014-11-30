import sys
import os


def getHomeDir():
    ''' Try to find user's home directory, otherwise return current directory.'''
    try:
        path1=os.path.expanduser("~")
    except:
        path1=""
    try:
        path2=os.environ["HOME"]
    except:
        path2=""
    try:
        path3=os.path.join(os.environ["HOMEDRIVE"],os.environ["HOMEPATH"])
    except:
        path3=""
    try:
        path4=os.environ["USERPROFILE"]
    except:
        path4=""

    if not os.path.exists(path1):
        if not os.path.exists(path2):
            if not os.path.exists(path3):
                if not os.path.exists(path4):
                    return os.getcwd()
                else: return path4
            else: return path3
        else: return path2
    else: return path1

def get_wdir():
    return wdir

wdir=""

class UserDir:
    def __init__(self,cwd=False,userHome=False,customPath=""):
        '''Init user dir.

        Arguments:
        cwd       :if True XPN will use it's own directory
        userHome  :if True XPN will create a .xpn directory inside user's home directory.
        customPath:if True XPN will create a .xpn directry inside user's defined path.
        '''
        global wdir
        if cwd:
            self.dir=""
        elif userHome:
            self.dir=os.path.join(getHomeDir(),".xpn")
        else:
            if os.path.exists(customPath):
                self.dir=os.path.join(customPath,".xpn")
            else:
                self.dir=""
        wdir=self.dir

    def Create(self):
        if not os.path.isdir(self.dir) and self.dir:
            if not os.path.exists(self.dir):
                try:
                    os.mkdir(self.dir)
                except:
                    print "Error: Can't create \"%s\"." % self.dir
                    return 1
            else:
                print "Error: Please remove \"%s\" file." % self.dir
                return 2
            #then check write access
        try:
            f=file(os.path.join(self.dir,"write-test"),"w")
        except IOError:
            print "Error: Can't write in \"%s\"." % self.dir
            return 3
        else:
            f.write("test")
            f.close()
            os.remove(os.path.join(self.dir,"write-test"))
        return 0
