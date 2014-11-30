import gtk
import gobject
import cPickle
import os
from xpn_src.UserDir import get_wdir

default_list=["From","Date","Subject"]

headers_list=["From","Date","Subject","Newsgroups","Reply-To","Sender","Organization","Followup-To","Mail-Copies-To",
              "Archive","Supersedes","Approved","Content-Type","Content-Transfer-Encoding","User-Agent","Xref","Bytes",
              "Lines","Message-ID","References"]

def load_headers_list():
    try:
        f=open(os.path.join(get_wdir(),"dats/headers_list.dat"),"rb")
    except IOError:
        list=default_list
    else:
        list=cPickle.load(f)
        f.close()
        if not list:
            list=headers_list
    return list

class HeadersList:

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
        for header in headers_list:
            self.left_model.append([header])

        list=load_headers_list()
        for header in list:
            self.right_model.append([header])

    def get_headers_list(self,treeview):
        model=treeview.get_model()
        iter=model.get_iter_first()
        list=[]
        while iter:
            list.append(model.get_value(iter,0))
            iter=model.iter_next(iter)
        return list
    
    def dump_tree(self,treeview):
        list=self.get_headers_list(self.right_list)
        f=open(os.path.join(get_wdir(),"dats/headers_list.dat"),"wb")
        cPickle.dump(list,f,1)
        f.close()
        
    
    def set_default_list(self,obj):
        self.right_model.clear()
        for header in default_list:
            self.right_model.append([header])
    
    def add_manually(self,obj):
        header=self.add_manually_entry.get_text()
        if header and not (header in self.get_headers_list(self.right_list)):
            self.right_model.append([header])


    def add_ordered(self,obj):
        model_left,path_left_list=self.left_list.get_selection().get_selected_rows()
        for path in path_left_list:
            iter_left=model_left.get_iter(path) 
            header=model_left.get_value(iter_left,0)
            if not (header in self.get_headers_list(self.right_list)):
                self.right_model.append([header])

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
        self.window.set_title("Headers List")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_size_request(500,400)
        self.table=gtk.Table(3,2,False)
        self.table.set_border_width(4)
        label_left=gtk.Label("<b>"+_("Standard Headers")+"</b>")
        label_left.set_use_markup(True)
        label_right=gtk.Label("<b>"+_("Shown Headers")+"</b>")
        label_right.set_use_markup(True)
        self.left_scrolledwin=gtk.ScrolledWindow()
        self.left_scrolledwin.set_border_width(4)
        self.left_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.left_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.left_scrolledwin.set_size_request(200,-1)
        
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
        self.left_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)


        
        self.right_scrolledwin=gtk.ScrolledWindow()
        self.right_scrolledwin.set_border_width(4)
        self.right_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.right_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.right_scrolledwin.set_size_request(200,-1)
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
        self.right_list_tooltip=gtk.Tooltips()
        self.right_list_tooltip.set_tip(self.right_list,_("XPN will show these headers on the top of the Article Pane"))
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
        

        self.add_manually_entry=gtk.Entry()
        self.add_manually_button=gtk.Button(_("Add Manually"))
        add_manually_hbox=gtk.HBox()
        add_manually_hbox.add(self.add_manually_entry)
        add_manually_hbox.add(self.add_manually_button)
        self.add_manually_button.connect("clicked",self.add_manually)

        self.default_button=gtk.Button(_("Set Default List"))
        self.default_button.connect("clicked",self.set_default_list)

        self.table.attach(label_left,0,1,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL)
        self.table.attach(vbox_buttons,1,2,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND)
        self.table.attach(label_right,2,3,0,1,gtk.EXPAND|gtk.FILL,gtk.FILL)
        self.table.attach(self.left_scrolledwin,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL)
        self.table.attach(self.right_scrolledwin,2,3,1,2,gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL)
        self.table.attach(vbox_buttons2,3,4,1,2,gtk.FILL,gtk.EXPAND)
        self.table.attach(add_manually_hbox,2,3,2,3,gtk.FILL|gtk.EXPAND,gtk.FILL)        
        self.table.attach(self.default_button,2,3,3,4,gtk.FILL|gtk.EXPAND,gtk.FILL)

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
    ch_list=HeadersList()
    gtk.main()
        
