import gtk
import pango
import gobject
import cPickle
import os
from xpn_src.UserDir import get_wdir


class Custom_List(gtk.GenericTreeModel):
    def __init__(self,list=[]):
        gtk.GenericTreeModel.__init__(self)
        self.list=list
    
    def on_get_flags(self):
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST
        
    def on_get_n_columns(self):
        return 3
    
    def on_get_column_type(self, index):
        return gobject.TYPE_STRING
        
    def on_get_iter(self, path):
        try:
            self.list[path[0]]
            return path[0]
        except IndexError:
            return None
        return path[0]
        
    def on_get_path(self, rowref):
        return tuple([rowref])
        
    def on_get_value(self, rowref, column):
        try: 
            return self.list[rowref][column]
        except IndexError:
            return None
        
    def on_iter_next(self, rowref):
        try:
            self.list[rowref+1]
        except IndexError:
            return None
        else:
            return rowref+1

    def on_iter_children(self, parent):
        return None

    def on_iter_has_child(self, rowref):
        return False
        
    def on_iter_n_children(self, rowref):
        if rowref:
            return 0
        return len(self.list)
        
    def on_iter_nth_child(self, parent, n):
        if parent:
            return None
        try:
            self.list[n]
        except IndexError:
            return None
        else:
            return n
        
    def on_iter_parent(self, child):
        return None

class Groups_List:
    def get_widget(self):
        return self.scrolledwin

    def show(self):
        self.scrolledwin.show_all()

    def hide(self):
        self.scrolledwin.hide_all()

    def clear(self):
        self.model=Custom_List()
        self.groups_list.set_model(self.model)

    def get_selected_rows(self):
        model,path_list=self.groups_list.get_selection().get_selected_rows()
        iter_list=[]
        for path in path_list:
            iter_list.append(model.get_iter(path))
        return model,path_list,iter_list 

    def show_list(self,list):
        new_model=Custom_List(list)
        self.groups_list.set_model(new_model)
        self.model=new_model
    
    def get_sizes(self):
        try:
            f=open(os.path.join(get_wdir(),"dats/sizes.dat"),"rb")
        except IOError:
            column1_width=145
        else:
            sizes=cPickle.load(f)
            f.close()
            column1_width=int(sizes.get("groups_col1",145))
        return int(column1_width)
     
    def __init__(self,column1_name,column2_name,column3_name):
        #GroupsScrolledWin
        self.scrolledwin=gtk.ScrolledWindow()
        self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        self.model=Custom_List()

        column1_width=self.get_sizes()

        #GroupsTree
        self.groups_list=gtk.TreeView(self.model)
        text_renderer=gtk.CellRendererText()
        self.column1=gtk.TreeViewColumn(column1_name,text_renderer,text=0)
        self.column2=gtk.TreeViewColumn(column2_name,text_renderer,text=1)
        self.column3=gtk.TreeViewColumn(column3_name,text_renderer,text=2)
        
        self.column1.set_resizable(True)
        self.column1.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column1.set_fixed_width(column1_width)
        self.column2.set_resizable(True)
        self.column2.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column2.set_fixed_width(40)
        
        self.column3.set_resizable(False)
        self.column3.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.groups_list.append_column(self.column1)
        self.groups_list.append_column(self.column2)
        self.groups_list.append_column(self.column3)
        
        self.scrolledwin.add(self.groups_list)
        self.groups_list.set_property("fixed-height-mode",True)
        self.groups_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)


class Groups_Pane:
    def get_widget(self):
        return self.scrolledwin

    def unparent(self):
        self.scrolledwin.unparent()

    def show(self):
        self.scrolledwin.show_all()

    def hide(self):
        self.scrolledwin.hide_all()

    def clear(self):
        self.model.clear()

    def set_background(self,color):
        color=gtk.gdk.color_parse(color)
        self.groups_list.modify_base(gtk.STATE_NORMAL,color)

    def set_foreground(self,color):
        color=gtk.gdk.color_parse(color)
        self.groups_list.modify_text(gtk.STATE_NORMAL,color)
        self.groups_list.modify_fg(gtk.STATE_NORMAL,color)

    def get_selected_rows(self):
        model,path_list=self.groups_list.get_selection().get_selected_rows()
        iter_list=[]
        for path in path_list:
            iter_list.append(model.get_iter(path))
        return model,path_list,iter_list 
   
    def get_first_selected_row(self):
        model,path_list=self.groups_list.get_selection().get_selected_rows()
        if path_list:
            return model,path_list[0],model.get_iter(path_list[0])
        else:
            return model,tuple(),None

    def get_first_selected_group(self):
        model,path_first,iter_first=self.get_first_selected_row()
        if iter_first:
            return model.get_value(iter_first,0)
        else:
            return None
         
    def append(self,values):
        iter=self.model.append(values)
        return iter

    def show_list(self,list,apply_bold=False):
        self.clear()
        if apply_bold==True:
            for group in list:
                if int(group[1].split(" ")[0])>0:
                    self.append((group[0],group[1],pango.WEIGHT_BOLD))
                else:
                    self.append((group[0],group[1],pango.WEIGHT_NORMAL))
        else:
            for group in list:
                self.append((group[0],group[1],pango.WEIGHT_NORMAL))

    def view_next_group(self,obj):
        model,path,iter_selected=self.get_first_selected_row()
        if model:
            column=self.groups_list.get_column(0)
            self.groups_list.grab_focus()
            if not iter_selected:
                next_iter=model.get_iter_first()
            else:
                next_iter=model.iter_next(iter_selected)
                if not next_iter:
                    next_iter=model.get_iter_first()
            if next_iter:
                path=model.get_path(next_iter)
                self.groups_list.set_cursor(path,None,False)
                self.groups_list.row_activated(path,column)

    def select_row_by_path(self,path):
        column=self.groups_list.get_column(0)
        self.groups_list.set_cursor(path,None,False)
        self.groups_list.row_activated(path,column)

    def get_sizes(self):
        try:
            f=open(os.path.join(get_wdir(),"dats/sizes.dat"),"rb")
        except IOError:
            column1_width=145
        else:
            sizes=cPickle.load(f)
            f.close()
            column1_width=int(sizes.get("groups_col1",145))
        return int(column1_width)
        
    def update_read_vs_unread(self,is_read,insert=True):
        if (is_read and insert) or (not is_read and not insert):
            #if the article is read we update the unreads number
            model,path,iter_selected=self.get_first_selected_row()
            unread_vs_total_numbers=model.get_value(iter_selected,1)
            num,tot=unread_vs_total_numbers.split(" ")
            if insert: number=int(num)+1
            else:      number=int(num)-1    
            model.set_value(iter_selected,1,str(number)+" "+tot)
            if number>=1:
                model.set_value(iter_selected,2,pango.WEIGHT_BOLD)
            else:# number<1
                model.set_value(iter_selected,2,pango.WEIGHT_NORMAL)

    def removed_article(self,is_read):
        model,path,iter_selected=self.get_first_selected_row()
        unread_vs_total_numbers=model.get_value(iter_selected,1)
        num,tot=unread_vs_total_numbers.split(" ")
        tot="("+str(int(tot[1:-1])-1)+")"
        if not is_read: num=str(int(num)-1)
        model.set_value(iter_selected,1,num+" "+tot)
        if int(num)>=1:
            model.set_value(iter_selected,2,pango.WEIGHT_BOLD)
        else:# int(num)<1
            model.set_value(iter_selected,2,pango.WEIGHT_NORMAL)
        
        
    def __init__(self,column1_name,column2_name,enable_weight,configs):
        self.enable_weight=enable_weight
        #GroupsScrolledWin
        self.scrolledwin=gtk.ScrolledWindow()
        self.scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        #Model
        self.model=gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT)
        
        column1_width=self.get_sizes()

        #GroupsTree
        self.groups_list=gtk.TreeView(self.model)
        text_renderer=gtk.CellRendererText()
        self.column1=gtk.TreeViewColumn(column1_name,text_renderer,text=0,weight=2)
        self.column2=gtk.TreeViewColumn(column2_name,text_renderer,text=1,weight=2)
        self.column1.set_resizable(True)
        self.column1.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.column1.set_fixed_width(column1_width)
        self.column1.set_sort_column_id(0)
        self.column2.set_resizable(False)
        self.column2.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.groups_list.append_column(self.column1)
        self.groups_list.append_column(self.column2)
        self.scrolledwin.add(self.groups_list)
        self.groups_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.model.set_sort_column_id(0,gtk.SORT_ASCENDING)
        if enable_weight:
            color=configs["background_color"]
            self.set_background(color)
            color=configs["text_color"]
            self.set_foreground(color)
        if configs["use_system_fonts"]=="True":
            self.groups_list.modify_font(pango.FontDescription(""))
        else:
            self.groups_list.modify_font(pango.FontDescription(configs["font_groups_name"]))

        #self.groups_list.set_property("fixed-height-mode",True)

