import gtk
import gobject 
import cPickle
import os
from xpn_src.UserDir import get_wdir
from xpn_src.Dialogs import Shortcut_Dialog, Shortcut_Error_Warning_Dialog, Dialog_OK

def escape(data):
    """Escape &, <, and > in a string of data.
    """

    # must do ampersand first
    data = data.replace("&", "&amp;")
    data = data.replace(">", "&gt;")
    data = data.replace("<", "&lt;")
    return data

def load_actions():
    main_actions=[
        ("File",_("File")),
        ("groups",_("Groups List..."),None),
        ("rules",_("Scoring and Action Rules..."),None),
        ("logs",_("Server Logs..."),None),
        ("exp_newsrc",_("Export Newsrc..."),None),
        ("imp_newsrc",_("Import Newsrc..."),None),
        ("accelerator",_("Modify Keyboard Shortcuts..."),None),
        ("conf",_("Preferences..."),None),
        ("exit",_("Exit"),"<Control>E"),
        ("Search",_("Search")),
        ("find",_("Find Article..."),"<Control>F"),
        ("filter",_("Filter Articles..."),"KP_Divide"),
        ("global",_("Global Search ..."),"<Control><Shift>G"),
        ("search",_("Search in the Body..."),"<Control>S"),
        ("View",_("View")),
        ("view_articles_opts",_("Articles View Options")),
        ("raw",_("View Raw Article"),"H"),
        ("spoiler",_("Show Spoilered Text"),"<Control>L"),
        ("show_quote",_("Show Quoted Text"),"<Shift>Q"),
        ("show_sign",_("Show Signatures"),"<Shift>S"),
        ("fixed",_("Fixed Pitch Font"),"<Shift>F"),      
        ("show_hide_headers",_("Show/Hide Headers"),"<Shift>H"),
        ("rot13",_("ROT13 Selected Text"),"<Control>R"),
        ("view_group_opts",_("Groups View Options")),
        ("show_threads",_("Show Threads"),None),
        ("show_all_read_threads",_("Show All Read Threads"),None),
        ("show_threads_without_watched",_("Show Threads Without Watched Articles"),None),
        ("show_read_articles",_("Show Read Articles"),None),
        ("show_unread_articles",_("Show UnRead Articles"),None),
        ("show_kept_articles",_("Show Kept Articles"),None),
        ("show_unkept_articles",_("Show UnKept Articles"),None),
        ("show_watched_articles",_("Show Watched Articles"),None),
        ("show_ignored_articles",_("Show Ignored Articles"),None),
        ("show_unwatchedignored_articles",_("Show UnWatched/UnIgnored Articles"),None),
        ("show_score_neg_articles",_("Show Articles with Score<0"),None),
        ("show_score_zero_articles",_("Show Articles with Score=0"),None),
        ("show_score_pos_articles",_("Show Articles with Score>0"),None),
        ("Navigate",_("Navigate")),
        ("group",_("View Next Group"),"G"),
        ("previous",_("Read Previous Article"),"B"),
        ("next",_("Read Next Article"),"<Shift>N"),
        ("next_unread",_("Read Next Unread Article"),"N"),
        ("parent",_("Read Parent Article"),"U"),
        ("one_key",_("One-Key Reading"),"space"),
        ("move_up",_("One-Key Scroll Up"),"<Control>space"),
        ("focus_article",_("Focus to Article Pane"),"3"),
        ("focus_groups",_("Focus to groups Pane"),"1"),
        ("focus_threads",_("Focus to Threads Pane"),"2"),
        ("zoom_article",_("Zoom Article Pane"),"<Control>3"),
        ("zoom_groups",_("Zoom groups Pane"),"<Control>1"),
        ("zoom_threads",_("Zoom Threads Pane"),"<Control>2"),
        ("Subscribed",_("Subscribed Groups")),
        ("gethdrs",_("Get New Headers in Subscribed Groups"),"<Control>H"),
        ("gethdrssel",_("Get New Headers in Selected Groups"),"<Control><Shift>H"),
        ("getbodies",_("Get Marked Article Bodies in Subscribed Groups"),"<Control>B"),
        ("getbodiessel",_("Get Marked Article Bodies in Selected Groups"),"<Control><Shift>B"),
        ("expand",_("Expand All Threads"),None),
        ("collapse",_("Collapse All Threads"),None),
        ("expand_row",_("Expand Selected SubThread"),None),
        ("collapse_row",_("Collapse Selected SubThread"),None),
        ("mark_group",_("Mark Group ...")),
        ("mark",_("Mark Selected Groups as Read"),None),
        ("mark_unread_group",_("Mark Selected Groups as Unread"),None),
        ("mark_download_group",_("Mark Group for Retrieving"),None),
        ("keepall",_("Keep Articles in Selected Groups"),None),
        ("markall",_("Mark All Groups as Read"),None),
        ("markall_unread",_("Mark All Groups as Unread"),None),
        ("apply_score",_("Apply Scoring and Action Rules"),None),
        ("groups_vs_id",_("Assign Identities to Groups"),None),
        ("Articles",_("Articles")),
        ("post",_("Post New Article..."),"P"),
        ("followup",_("Follow-Up To Newsgroup..."),"F"),
        ("reply",_("Reply By Mail..."),"<Shift>M"),
        ("outbox_manager",_("Open Outbox Manager"),None),
        ("cancel",_("Cancel Article..."),None),
        ("supersede",_("Supersede Article..."),None),
        ("flags",_("Flags & Score")),
        ("mark_read",_("Mark Article as Read"),"<Shift>R"),
        ("mark_unread",_("Mark Article as UnRead"),"<Shift>U"),
        ("mark_download",_("Mark Article for Retrieving"),"M"),
        ("keep",_("Keep Article"),"<Shift>K"),
        ("delete",_("Delete Article"),"<Control><Shift>D"),
        ("mark_unread_sub",_("Mark SubThread as UnRead"),None),
        ("mark_read_sub",_("Mark SubThread as Read"),None),
        ("mark_download_sub",_("Mark SubThread for Retrieving"),None),
        ("keep_sub",_("Keep SubThread"),None),
        ("watch",_("Watch SubThread"),"<Shift>W"),
        ("ignore",_("Ignore SubThread"),"<Shift>I"),
        ("raise_score",_("Raise Author Score"),None),
        ("lower_score",_("Lower Author Score"),None),
        ("set_score",_("Set Author Score"),None),
        ("Help",_("Help")),
        ("about",_("About..."),None)]

    edit_actions=[
        ("Article",_("Article")),
        ("send",_("Send Article"),"<Control>S"),
        ("send_later",_("Send Article Later"),"<Control><Shift>S"),
        ("save_draft",_("Save Article as Draft"),"<Alt>D"),
        ("discard",_("Discard Article"),"<Control>D"),
        ("rot13",_("ROT13 Selected Text"),"<Control>R"),
        ("editor",_("Launch External Editor"),"<Alt>E"),
        ("spoiler",_("Insert Spoiler Char"),"<Control>L")]

    outbox_actions=[
        ("Outbox",_("Outbox")),
        ("send_article",_("Send Queued Articles"),"<Control>S"),
        ("send_mail",_("Send Queued Mails"),"<Control><Shift>S"),
        ("edit",_("Edit Article/Mail"),"E"),
        ("delete",_("Delete Article/Mail"),"Delete"),
        ("exit",_("Exit"),"<Control>E")]

    return main_actions,edit_actions,outbox_actions

def load_shortcuts(win):
    main_actions,edit_actions,outbox_actions=load_actions()
    main_shortcuts=dict()
    edit_shortcuts=dict()
    outbox_shortcuts=dict()
    try:
        f=open(os.path.join(get_wdir(),"dats/shortcuts.dat"),"rb")
    except IOError:
        file_found=False
    else:
        file_found=True
        shortcuts=cPickle.load(f)
        f.close()
        if not shortcuts:
            file_found=False

    if win=="main":
        for action in main_actions:
            if len(action)>2:
                if file_found:
                    try:
                        main_shortcuts[action[0]]=shortcuts["main"][action[0]]
                    except:
                        main_shortcuts[action[0]]=action[2]
                else:
                    main_shortcuts[action[0]]=action[2]
        return main_shortcuts

    if win=="edit":
        for action in edit_actions:
            if len(action)>2:
                if file_found:
                    try:
                        edit_shortcuts[action[0]]=shortcuts["edit"][action[0]]
                    except:
                        edit_shortcuts[action[0]]=action[2] 
                else:
                    edit_shortcuts[action[0]]=action[2] 
        return edit_shortcuts
    
    if win=="outbox":
        for action in outbox_actions:
            if len(action)>2:
                if file_found:
                    try:
                        outbox_shortcuts[action[0]]=shortcuts["outbox"][action[0]]
                    except:
                        edit_shortcuts[action[0]]=action[2] 
                else:
                    outbox_shortcuts[action[0]]=action[2]
        return outbox_shortcuts
    else:
        return dict()
    

class KeyBindings:

    def delete_event(self,widget,event,data=None):
        return False  

    def destroy(self,widget):
        self.window.destroy()
        if __name__=="__main__":
            gtk.main_quit()

    def close_ok(self,obj): 
        self.dump_tree()
        #self.main_win.create_ui()
        self.destroy(None)
    
    def close_cancel(self,obj):
        self.destroy(None)

    def get_shortcuts_from_tree(self):
        #0:Short Name 1:Long Name 2:Accelerator 3:Dump
        model=self.treeview.get_model()
        iter_current=model.get_iter_first()
        shortcuts=dict()
        shortcuts["main"]=dict()
        shortcuts["edit"]=dict()
        shortcuts["outbox"]=dict()
        while iter_current:
            sname=model.get_value(iter_current,0)
            accel=model.get_value(iter_current,2)
            to_dump=model.get_value(iter_current,3)
            if to_dump:
                parent_path=tuple([model.get_path(iter_current)[0],])
                parent_iter=model.get_iter(parent_path)
                win=model.get_value(parent_iter,0)
                shortcuts[win][sname]=accel

            #let's cycle the tree
            if model.iter_has_child(iter_current):
                iter_current=model.iter_children(iter_current)
            else:
                iter_next=model.iter_next(iter_current)
                while not iter_next:
                    prev_iter=model.iter_parent(iter_current)
                    iter_current=prev_iter
                    if not prev_iter:
                        break
                    iter_next=model.iter_next(iter_current)
                iter_current=iter_next
        return shortcuts

    def dump_tree(self):
        shortcuts=self.get_shortcuts_from_tree()
        f=open(os.path.join(get_wdir(),"dats/shortcuts.dat"),"wb")
        cPickle.dump(shortcuts,f,1)
        f.close()

    def change_shortcut(self,obj):
        model,iter_selected=self.treeview.get_selection().get_selected()
        if iter_selected:
            to_dump=model.get_value(iter_selected,3)
            if to_dump:
                dialog=Shortcut_Dialog()
                if dialog.resp==gtk.RESPONSE_OK:
                    model.set_value(iter_selected,2,dialog.shortcut)


    def check_duplicates_warnings(self,obj):
        shortcuts=self.get_shortcuts_from_tree()
        main_values=shortcuts["main"].values()
        edit_values=shortcuts["edit"].values()
        outbox_values=shortcuts["outbox"].values()
        main_actions,edit_actions,outbox_actions=load_actions()

        def get_desc(value_to_find,win):
            dic=shortcuts[win]
            if win=="main":
                actions=main_actions
            elif win=="edit":
                actions=edit_actions
            else:
                actions=outbox_actions
            for key,value in dic.iteritems():
                if value_to_find==value:
                    for action in actions:
                        if action[0]==key:
                            return action[1]
            return "" 
        
        warnings=[]
        main_actions,edit_actions,outbox_actions=load_actions()
        for value in edit_values:
            if value in main_values:
                warnings.append([_("Edit Window"),value,get_desc(value,"edit")])
                warnings.append([_("Main Window"),value,get_desc(value,"main")])
                warnings.append(["","",""])

        for value in edit_values:
            if value in outbox_values:
                warnings.append([_("Edit Window"),value,get_desc(value,"edit")])
                warnings.append([_("Outbox Window"),value,get_desc(value,"outbox")])
                warnings.append(["","",""])


        for value in outbox_values:
            if value in main_values:
                warnings.append([_("Outbox Window"),value,get_desc(value,"outbox")])
                warnings.append([_("Main Window"),value,get_desc(value,"main")])
                warnings.append(["","",""])

        if len(warnings)>0:
            self.dialog3=Shortcut_Error_Warning_Dialog(True,warnings,"<b>"+_("Found duplicated shortcuts on different windows")+"</b>\n"+_("That's not a problem, the shortcut will work only on the active window "))
        else:
            self.dialog3=Dialog_OK(_("No Errors"))
            

    def check_duplicates_errors(self,obj):
        shortcuts=self.get_shortcuts_from_tree()
        main_values=[value.lower() for value in shortcuts["main"].values() if value]
        edit_values=[value.lower() for value in shortcuts["edit"].values() if value]
        outbox_values=[value.lower() for value in shortcuts["outbox"].values() if value]
        main_actions,edit_actions,outbox_actions=load_actions()
        
        def get_desc(value_to_find,win):
            dic=shortcuts[win]
            if win=="main":
                actions=main_actions
            elif win=="edit":
                actions=edit_actions
            else:
                actions=outbox_actions
            for key,value in dic.iteritems():
                if value:
                    if value_to_find.lower()==value.lower():
                        for action in actions:
                            if action[0]==key:
                                dic.pop(action[0])
                                return action[1]
            return "" 
        
        errors=[]
        main_actions,edit_actions,outbox_actions=load_actions()
        main_values_shown=[]
        edit_values_shown=[]
        outbox_values_shown=[]

        for value in main_values:
            count=main_values.count(value)
            if count>1:
                if value and not (value in main_values_shown):
                    main_values_shown.append(value)
                    for i in range(count):
                        errors.append([_("Main Window"),value,get_desc(value,"main")])



        for value in edit_values:
            count=edit_values.count(value)
            if count>1:
                if value and not (value in edit_values_shown):
                    edit_values_shown.append(value)
                    for i in range(count):
                        errors.append([_("Edit Window"),value,get_desc(value,"edit")])


        for value in outbox_values:
            count=outbox_values.count(value)
            if count>1:
                if value and not (value in outbox_values_shown):
                    outbox_values_shown.append(value)
                    for i in range(count):
                        errors.append([_("Outbox Window"),value,get_desc(value,"outbox")])
        if len(errors)>0:
            self.dialog3=Shortcut_Error_Warning_Dialog(False,errors,"<b>"+_("Found duplicated shortcuts on the same windows")+"</b>")
        else:
            self.dialog3=Dialog_OK(_("No Errors"))
            
        

    def load_list(self):
        self.model.clear()
        main_actions,edit_actions,outbox_actions=load_actions()
        main_shortcuts=load_shortcuts("main")
        edit_shortcuts=load_shortcuts("edit")
        outbox_shortcuts=load_shortcuts("outbox")
        #0:Short Name 1:Long Name 2:Accelerator 3:Dump

        iter_root_mainwin=self.model.append(None,["main",_("Main Window"),"",False])
        for action in main_actions:
            if len(action) == 2:
                iter_root_menu=self.model.append(iter_root_mainwin,[action[0],action[1],"",False])
            else:
                self.model.append(iter_root_menu,[action[0],action[1],main_shortcuts[action[0]],True])

        iter_root_editwin=self.model.append(None,["edit",_("Edit Window"),"",False])
        for action in edit_actions:
            if len(action) == 2:
                iter_root_menu=self.model.append(iter_root_editwin,[action[0],action[1],"",False])
            else:                
                self.model.append(iter_root_menu,[action[0],action[1],edit_shortcuts[action[0]],True])

        iter_root_outboxwin=self.model.append(None,["outbox",_("Outbox Window"),"",False])
        for action in outbox_actions:
            if len(action) == 2:
                iter_root_menu=self.model.append(iter_root_outboxwin,[action[0],action[1],"",False])
            else:                
                self.model.append(iter_root_menu,[action[0],action[1],outbox_shortcuts[action[0]],True])
    
    def reset_defaults(self,obj):
        try: os.remove(os.path.join(get_wdir(),"dats/shortcuts.dat"))
        except: pass
        self.load_list()
        
    def clear_shortcuts(self,obj):
        iter_current=self.model.get_iter_first()
        while iter_current:
            to_dump=self.model.get_value(iter_current,3)
            if to_dump:
                self.model.set_value(iter_current,2,"")

            #let's cycle the tree
            if self.model.iter_has_child(iter_current):
                iter_current=self.model.iter_children(iter_current)
            else:
                iter_next=self.model.iter_next(iter_current)
                while not iter_next:
                    prev_iter=self.model.iter_parent(iter_current)
                    iter_current=prev_iter
                    if not prev_iter:
                        break
                    iter_next=self.model.iter_next(iter_current)
                iter_current=iter_next
                
    def __init__(self,main_win):
        self.main_win=main_win
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title(_("Keyboard Shortcuts"))
        self.window.set_position(gtk.WIN_POS_CENTER)
        vbox=gtk.VBox()
        vbox.set_border_width(4)
        self.window.set_size_request(500,400)
        scrolledwin=gtk.ScrolledWindow()
        scrolledwin.set_border_width(4)
        scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.treeview=gtk.TreeView() 
        self.treeview.set_border_width(4)
        #0:Short Name 1:Long Name 2:Accelerator 3:Dump
        self.model=gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
        scrolledwin.add(self.treeview)
        self.treeview.set_model(self.model)
        text_renderer=gtk.CellRendererText()
        column1=gtk.TreeViewColumn(_("Action"),text_renderer,text=1)
        column2=gtk.TreeViewColumn(_("Shortcut"),text_renderer,text=2)
        self.treeview.append_column(column1)
        self.treeview.append_column(column2)
        self.treeview.set_rules_hint(True)
        
        self.button_change=gtk.Button(_("Change Shortcut"))
        self.button_change.connect("clicked",self.change_shortcut)

        self.button_default=gtk.Button(_("Default Shortcuts"))
        self.button_default.connect("clicked",self.reset_defaults)
        
        self.button_clear_shortcuts=gtk.Button(_("Clear Shortcuts"))
        self.button_clear_shortcuts.connect("clicked",self.clear_shortcuts)
        
        self.button_duplicates_warnings=gtk.Button(_("Duplicates Warnings"))
        self.button_duplicates_warnings.connect("clicked",self.check_duplicates_warnings)

        self.button_duplicates_errors=gtk.Button(_("Duplicates Errors"))
        self.button_duplicates_errors.connect("clicked",self.check_duplicates_errors)
        
        button_table=gtk.Table(4,2,False)
        vbox.pack_start(scrolledwin,True,True,4)
        
        sep=gtk.HSeparator()
        button_table.attach(self.button_change,0,2,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL,4,4)
        button_table.attach(self.button_clear_shortcuts,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,4,4)
        button_table.attach(self.button_default,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL,4,4)
        button_table.attach(self.button_duplicates_warnings,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,4,4)
        button_table.attach(self.button_duplicates_errors,1,2,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,4,4)
        button_table.attach(sep,0,2,3,4,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL,4,4)
        vbox.pack_start(button_table,False,True,4)
        
        hbox=gtk.HBox()
        self.ok_button=gtk.Button(None,gtk.STOCK_OK)
        self.ok_button.connect("clicked",self.close_ok)
        self.cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        self.cancel_button.connect("clicked",self.close_cancel)
        hbox.pack_start(self.cancel_button,True,True,2)
        hbox.pack_start(self.ok_button,True,True,2)
        vbox.pack_start(hbox,False,True,6)
        self.load_list()
        self.window.add(vbox)
        self.window.show_all()
