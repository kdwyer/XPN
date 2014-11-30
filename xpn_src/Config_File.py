import gtk
import os
from xpn_src.UserDir import get_wdir


class Config_File:
    def get_configs(self):
        return self.configs

    def write_configs(self):
        f=open(os.path.join(get_wdir(),"config.txt"),"w")
        for key in self.configs.keys():
            f.write(key+"="+self.configs[key].encode("utf-8")+"\n")
        f.close()


    def __init__(self):
        self.configs={}
        self.configs["server"]=""
        self.configs["port"]="119"
        self.configs["auth"]="False"
        self.configs["username"]=""
        self.configs["password"]=""
        self.configs["nntp_use_ssl"]="False"
        self.configs["smtp_server"]=""
        self.configs["smtp_port"]="25"
        self.configs["smtp_auth"]="False"
        self.configs["smtp_username"]=""
        self.configs["smtp_password"]=""
        self.configs["use_mail_from"]="False"
        self.configs["quote1_color"]="#0000FF"
        self.configs["quote2_color"]="#00AAFF"
        self.configs["quote3_color"]="#AAAAFF"       
        self.configs["sign_color"]="#FF0000"
        self.configs["text_color"]="#000000"
        self.configs["background_color"]="#FFFFFF"
        self.configs["url_color"]="#1D921C"
        self.configs["headers_bg_color"]="#F7EDB5"
        self.configs["headers_fg_color"]="#000000"
        self.configs["font_name"]="Sans 9"
        self.configs["font_threads_name"]="Sans 9"
        self.configs["font_groups_name"]="Sans 9"
        self.configs["use_system_fonts"]="True"
        self.configs["fixed"]="False"
        self.configs["layout"]="1"
        self.configs["show_headers"]="True"
        self.configs["oneclick"]="False"
        self.configs["oneclick_article"]="False"
        self.configs["expand_group"]="False"
        self.configs["charset"]="ISO-8859-1"
        self.configs["fallback_charset"]="ISO-8859-1"
        self.configs["custom_browser"]="False"
        self.configs["browser_launcher"]=""
        self.configs["purge_read"]="5"
        self.configs["purge_unread"]="10"
        self.configs["limit_articles"]="False"
        self.configs["limit_articles_number"]="500"
        self.configs["download_timeout"]="30"
        self.configs["automatic_download"]="False"
        self.configs["threading_method"]="2"
        self.configs["external_editor"]="False"
        self.configs["editor_launcher"]=""
        self.configs["show_read_articles"]="True"
        self.configs["show_unread_articles"]="True"
        self.configs["show_threads_without_watched"]="True"
        self.configs["show_all_read_threads"]="True"        
        self.configs["show_unkept_articles"]="True"
        self.configs["show_kept_articles"]="True"
        self.configs["show_watched_articles"]="True"
        self.configs["show_ignored_articles"]="True"
        self.configs["show_unwatchedignored_articles"]="True"
        self.configs["show_score_neg_articles"]="True"
        self.configs["show_score_zero_articles"]="True"
        self.configs["show_score_pos_articles"]="True"
        self.configs["raw"]="False"
        self.configs["show_quote"]="True"
        self.configs["show_sign"]="True"
        self.configs["show_spoiler"]="False"
        self.configs["download_bodies"]="False"
        self.configs["scroll_fraction"]="50"
        self.configs["lang"]="en"
        self.configs["ascend_order"]="True"
        self.configs["sort_col"]="Date"
        self.configs["show_threads"]="True"
        self.configs["advance_on_mark"]="False"
        self.configs["exp_column"]="Subject"
        
        try:
            f=open(os.path.join(get_wdir(),"config.txt"),"r")
        except IOError:
            self.found_config_file=False
        else:
            #parsing config file to a dict
            self.found_config_file=True
            lista=f.readlines()
            for i in range(len(lista)):
                ind=lista[i].find("=")
                if ind>0:
                    left=lista[i][0:ind].strip()
                    right=lista[i].strip("\r\n")[ind+1:].strip(" ")
                    self.configs[left]=right.decode("utf-8")
