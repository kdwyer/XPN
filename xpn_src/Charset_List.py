import gtk
import gobject
import cPickle
import os
from locale import getdefaultlocale
from xpn_src.UserDir import get_wdir

try: system_enc=getdefaultlocale()[1]
except: system_enc="US-ASCII"
guess_list=[system_enc,"US-ASCII","ISO-8859-1","ISO-8859-2","ISO-8859-3","ISO-8859-4","ISO-8859-5",
                "ISO-8859-6","ISO-8859-7","ISO-8859-8","ISO-8859-9","ISO-8859-10","ISO-8859-13",
                "ISO-8859-14","ISO-8859-15","ISO-2022-JP","ISO-2022-KR","KOI8-R","KOI8-U","GB2312","BIG5",
                "WINDOWS-1250","WINDOWS-1251","WINDOWS-1252","WINDOWS-1253","WINDOWS-1254",
                "WINDOWS-1255","WINDOWS-1256","WINDOWS-1257","WINDOWS-1258","MACCYRILLIC","MACICELAND",
                "MACLATIN2","MACROMAN","MACTURKISH","UTF-8"]
encodings_list=["US-ASCII","ISO-8859-1","ISO-8859-2","ISO-8859-3","ISO-8859-4","ISO-8859-5",
                "ISO-8859-6","ISO-8859-7","ISO-8859-8","ISO-8859-9","ISO-8859-10","ISO-8859-13",
                "ISO-8859-14","ISO-8859-15","ISO-2022-JP","ISO-2022-KR","KOI8-R","KOI8-U","GB2312","BIG5",
                "UTF-7","UTF-8","WINDOWS-1250","WINDOWS-1251","WINDOWS-1252","WINDOWS-1253","WINDOWS-1254",
                "WINDOWS-1255","WINDOWS-1256","WINDOWS-1257","WINDOWS-1258","MACCYRILLIC","MACICELAND",
                "MACLATIN2","MACROMAN","MACTURKISH"]
encodings_tip="US-ASCII (English) \
        \nISO-8859-1 (West Europe, latin1) \
        \nISO-8859-2 (Central and Eastern Europe, latin2) \
        \nISO-8859-3 (Esperanto, Maltese, latin3) \
        \nISO-8859-4 (Baltic languages, latin4) \
        \nISO-8859-5 (Cyrillic) \
        \nISO-8859-6 (Arabic) \
        \nISO-8859-7 (Greek) \
        \nISO-8859-8 (Hebrew) \
        \nISO-8859-9 (Turkish, latin5) \
        \nISO-8859-10 (Nordish languages, latin6) \
        \nISO-8859-13 (Baltic languages) \
        \nISO-8859-14 (Celtic languages, latin8) \
        \nISO-8859-15 (Western Europe) \
        \nISO-2022-JP (Japanese) \
        \nISO-2022-KR (Korean) \
        \nKOI8-R (Russian) \
        \nKOI8-U (Ukrainian) \
        \nGB-2312 (Simplified Chinese) \
        \nBIG5 (Traditional Chinese) \
        \nUTF-7 (All languages) \
        \nUTF-8 (All languages) \
        \nWINDOWS-1250 (Central and Eastern Europe, cp1250) \
        \nWINDOWS-1251 (Cyrillic, cp1251) \
        \nWINDOWS-1252 (Western Europe, cp1252) \
        \nWINDOWS-1253 (Greek, cp1253) \
        \nWINDOWS-1254 (Turkish, cp1254) \
        \nWINDOWS-1255 (Hebrew, cp1255) \
        \nWINDOWS-1256 (Arabic, cp1256) \
        \nWINDOWS-1257 (Baltic Languages, cp1257) \
        \nWINDOWS-1258 (Vietnamese, cp1258) \
        \nMACCYRILLIC (Cyrillic) \
        \nMACICELAND (Icelandic) \
        \nMACLATIN2 (Central and Eastern Europe) \
        \nMACROMAN (Western Europe) \
        \nMACTURKISH (Turkish)"
ordered_list=["US-ASCII","ISO-8859-1","ISO-8859-2","ISO-8859-3","ISO-8859-4","ISO-8859-5",
                "ISO-8859-6","ISO-8859-7","ISO-8859-8","ISO-8859-9","ISO-8859-10","ISO-8859-13",
                "ISO-8859-14","ISO-8859-15","UTF-8"]

def load_ordered_list():
    try:
        f=open(os.path.join(get_wdir(),"dats/charset_list.dat"),"rb")
    except IOError:
        list=ordered_list
    else:
        list=cPickle.load(f)
        f.close()
        if not list:
            list=ordered_list
    return list

class CharsetList:

    def delete_event(self,widget,event,data=None):
        return False  

    def destroy(self,widget):
        self.window.destroy()
        if __name__=="__main__":
            gtk.main_quit()
    
    def close_ok(self,obj): 
        self.dump_tree(self.right_list)
        self.destroy(None)
    
    def close_cancel(self,obj):
        self.destroy(None)
         
    def fill_lists(self):
        for encoding in encodings_list:
            self.left_model.append([encoding])

        list=load_ordered_list()
        for encoding in list:
            self.right_model.append([encoding])

    def get_charset_list(self,treeview):
        model=treeview.get_model()
        iter=model.get_iter_first()
        list=[]
        while iter:
            list.append(model.get_value(iter,0))
            iter=model.iter_next(iter)
        return list
    
    def dump_tree(self,treeview):
        list=self.get_charset_list(self.right_list)
        f=open(os.path.join(get_wdir(),"dats/charset_list.dat"),"wb")
        cPickle.dump(list,f,1)
        f.close()
        
    #CODICE PER IL DRAG E DROP
         
    #def data_get(self,treeview,context,selection,info,timestamp):
    #    model,iter=treeview.get_selection().get_selected()
    #    text=model.get_value(iter,0)
    #    if treeview==self.left_list:
    #        selection.set("Charset",8,text)
    #    else:
    #        selection.set("Ord",8,text)
    
    #def data_received_right(self,treeview,context,x,y,selection,info,timestamp):
    #    model=treeview.get_model()
    #    data=selection.data
    #    drop_info=treeview.get_dest_row_at_pos(x,y)
    #    if drop_info:
    #        path,position=drop_info
    #        iter=model.get_iter(path)
    #        if not (data in self.get_charset_list(treeview)) or selection.target=="Ord":
    #            if (position==gtk.TREE_VIEW_DROP_BEFORE or position== gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
    #                model.insert_before(iter,[data])
    #            else:
    #                model.insert_after(iter,[data])
    #    else:
    #        if not (data in self.get_charset_list(treeview)) or selection.target=="Ord":
    #            model.append([data])
    #    if context.action ==gtk.gdk.ACTION_MOVE:
    #        context.finish(True,True,timestamp)

    #def data_received_left(self,treeview,context,x,y,selection,info,timestamp):
    #    if context.action ==gtk.gdk.ACTION_MOVE:
    #        context.finish(True,True,timestamp)
    
    def set_default_list(self,obj):
        self.right_model.clear()
        for encoding in ordered_list:
            self.right_model.append([encoding])
    
    def add_ordered(self,obj):
        model_left,path_left_list=self.left_list.get_selection().get_selected_rows()
        for path in path_left_list:
            iter_left=model_left.get_iter(path) 
            encoding=model_left.get_value(iter_left,0)
            if not (encoding in self.get_charset_list(self.right_list)):
                self.right_model.append([encoding])

    def remove_ordered(self,obj):
        model_right,path_right_list=self.right_list.get_selection().get_selected_rows()
        for i in range(len(path_right_list)):
            path=path_right_list[i]
            if i!=0:
                path=list(path)
                path[0]=path[0]-i
                path=tuple(path)
            iter_right=model_right.get_iter(path)
            self.right_model.remove(iter_right)
        
    def move_up(self,obj):
        model,path_list=self.right_list.get_selection().get_selected_rows()
        for path in path_list:
            iter_to_move=model.get_iter(path)
            new_path=list(path)
            if new_path[0]>0:
                new_path[0]=new_path[0]-1
            new_path=tuple(new_path)
            iter_previous=model.get_iter(new_path)
            model.swap(iter_to_move,iter_previous)

    def move_down(self,obj):
        model,path_list=self.right_list.get_selection().get_selected_rows()
        path_list.reverse()
        for path in path_list:
            iter_to_move=model.get_iter(path)
            iter_next=model.iter_next(iter_to_move)
            if iter_next!=None:
                model.swap(iter_to_move,iter_next)
   
    def __init__(self):
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event",self.delete_event)
        self.window.connect("destroy",self.destroy)
        self.window.set_title("Charset List")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_size_request(400,400)
        self.table=gtk.Table(3,2,False)
        self.table.set_border_width(4)
        label_left=gtk.Label("<b>"+_("Available Charsets")+"</b>")
        label_left.set_use_markup(True)
        label_right=gtk.Label("<b>"+_("Ordered Charsets")+"</b>")
        label_right.set_use_markup(True)
        self.left_scrolledwin=gtk.ScrolledWindow()
        self.left_scrolledwin.set_border_width(4)
        self.left_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.left_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.left_list=gtk.TreeView() 
        self.left_list.set_border_width(4)
        self.left_model=gtk.ListStore(gobject.TYPE_STRING)
        self.left_scrolledwin.add(self.left_list)
        self.left_list.set_model(self.left_model)
        text_renderer=gtk.CellRendererText()
        self.left_column=gtk.TreeViewColumn(_("List"),text_renderer,text=0)
        self.left_list.append_column(self.left_column)
        self.left_list.set_rules_hint(True)
        self.left_list.set_headers_visible(False)
        #self.left_list.enable_model_drag_source(False,[("Charset",gtk.TARGET_SAME_APP,0)],gtk.gdk.ACTION_COPY)
        #self.left_list.enable_model_drag_dest([("Delete",gtk.TARGET_SAME_APP,2)],gtk.gdk.ACTION_MOVE)
        #self.left_list.connect("drag-data-get",self.data_get)
        #self.left_list.connect("drag-data-received",self.data_received_left)
        self.left_list_tooltip=gtk.Tooltips()
        self.left_list_tooltip.set_tip(self.left_list,encodings_tip)
        self.left_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)


        
        self.right_scrolledwin=gtk.ScrolledWindow()
        self.right_scrolledwin.set_border_width(4)
        self.right_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.right_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.right_list=gtk.TreeView() 
        self.right_list.set_border_width(4)
        self.right_model=gtk.ListStore(gobject.TYPE_STRING)
        self.right_scrolledwin.add(self.right_list)
        self.right_list.set_model(self.right_model)
        text_renderer=gtk.CellRendererText()
        self.right_column=gtk.TreeViewColumn(_("List"),text_renderer,text=0)
        self.right_list.append_column(self.right_column)
        self.right_list.set_rules_hint(True)
        self.right_list.set_headers_visible(False)
        #self.right_list.enable_model_drag_dest([("Charset",gtk.TARGET_SAME_APP,0),("Ord",gtk.TARGET_SAME_WIDGET,1)],gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)

        #self.right_list.enable_model_drag_source(False,[("Ord",gtk.TARGET_SAME_WIDGET,1),("Delete",gtk.TARGET_SAME_APP,2)],gtk.gdk.ACTION_MOVE)
        #self.right_list.connect("drag-data-received",self.data_received_right)
        #self.right_list.connect("drag-data-get",self.data_get)
        self.right_list_tooltip=gtk.Tooltips()
        self.right_list_tooltip.set_tip(self.right_list,_("XPN will try to encode your articles with these charsets in this order"))
        self.right_list.set_reorderable(True)
        self.right_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)


        self.to_right_button=gtk.Button()
        to_right_button_image=gtk.Image()
        to_right_button_image.set_from_stock(gtk.STOCK_GO_FORWARD,gtk.ICON_SIZE_MENU)
        
        self.to_right_button.add(to_right_button_image)
        self.to_right_button.connect("clicked",self.add_ordered)
        self.to_left_button=gtk.Button()
        to_left_button_image=gtk.Image()
        to_left_button_image.set_from_stock(gtk.STOCK_GO_BACK,gtk.ICON_SIZE_MENU)
        
        self.to_left_button.add(to_left_button_image)
        self.to_left_button.connect("clicked",self.remove_ordered)
        vbox_buttons=gtk.VBox()
        vbox_buttons.pack_start(self.to_right_button,False,True,10)
        vbox_buttons.pack_start(self.to_left_button,False,True,10)
        
        up_button_image=gtk.Image()
        up_button_image.set_from_stock(gtk.STOCK_GO_UP,gtk.ICON_SIZE_MENU)
        self.up_button=gtk.Button()
        self.up_button.add(up_button_image)
        self.up_button.connect("clicked",self.move_up)

        down_button_image=gtk.Image()
        down_button_image.set_from_stock(gtk.STOCK_GO_DOWN,gtk.ICON_SIZE_MENU)
        self.down_button=gtk.Button()
        self.down_button.add(down_button_image)
        self.down_button.connect("clicked",self.move_down)

        vbox_buttons2=gtk.VBox()
        vbox_buttons2.pack_start(self.up_button,False,False,10)
        vbox_buttons2.pack_start(self.down_button,False,False,10)
        
        self.default_button=gtk.Button(_("Set Default List"))
        self.default_button.connect("clicked",self.set_default_list)

        self.table.attach(label_left,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL)
        self.table.attach(vbox_buttons,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND)
        self.table.attach(label_right,2,3,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL)
        self.table.attach(self.left_scrolledwin,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL)
        self.table.attach(self.right_scrolledwin,2,3,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL)
        self.table.attach(vbox_buttons2,3,4,1,2,gtk.FILL,gtk.EXPAND)
        self.table.attach(self.default_button,2,3,2,3,gtk.FILL|gtk.EXPAND,gtk.FILL)

        vbox=gtk.VBox()
        hbox=gtk.HBox()
        self.ok_button=gtk.Button(None,gtk.STOCK_OK)
        self.ok_button.connect("clicked",self.close_ok)
        self.cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        self.cancel_button.connect("clicked",self.close_cancel)
        hbox.pack_start(self.cancel_button,True,True,2)
        hbox.pack_start(self.ok_button,True,True,2)
        vbox.pack_start(self.table,True,True,4)
        vbox.pack_start(hbox,False,True,2)
        self.window.add(vbox)
        self.fill_lists()
        self.window.show_all()

if __name__=="__main__":
    ch_list=CharsetList()
    gtk.main()
        
