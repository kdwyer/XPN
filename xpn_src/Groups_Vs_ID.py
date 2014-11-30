import gtk
import cPickle 
import os
import ConfigParser
from xpn_src.UserDir import get_wdir


class Groups_Vs_ID:
    def show(self):
        self.win.show_all()
    
    def delete_event(self,widget,event,data=None):
        return False

    def destroy(self,obj):
        self.win.destroy()

    def save_configs(self,obj):
        subscribed=self.art_db.getSubscribed()
        new_list=[]
        subscribed_groups=[]
        for group in subscribed:
            combo=self.id_dict[group[0]]
            id_name=combo.get_active_text()
            new_group=[group[0] ,group[1], group[2], id_name]
            subscribed_groups.append([group[0], group[2], id_name])
            new_list.append(new_group)
        
        self.art_db.updateSubscribed(new_list)
        self.main_win.subscribed_groups=subscribed_groups[:]
        self.win.destroy() 

    def __init__(self,subscribed_groups,main_win):
        self.main_win=main_win
        self.art_db=main_win.art_db
        n_rows=len(subscribed_groups)
        self.win=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect("delete_event",self.delete_event)
        self.win.set_title(_("Assign Identities to Groups"))
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file("pixmaps/conf.xpm"))
        self.win.set_position(gtk.WIN_POS_CENTER)
        
        main_vbox=gtk.VBox()
        main_vbox.set_border_width(4)
        
        group_label=gtk.Label("<b>"+_("Group")+"</b>")
        group_label.set_alignment(0,0)
        group_label.set_use_markup(True)
        
        id_label=gtk.Label("<b>"+_("Identity")+"</b>")
        id_label.set_alignment(0,0)
        id_label.set_use_markup(True)
        
        groups_table=gtk.Table(n_rows,2,False)
        groups_table.set_border_width(8)

        groups_table.attach(group_label,0,1,0,1,False,False,4)
        groups_table.attach(id_label,1,2,0,1,False,False,4)
        self.entries=[]
        self.combos=[]
        cp_id=ConfigParser.ConfigParser()
        cp_id.read(os.path.join(get_wdir(),"dats","id.txt"))
        ids=cp_id.sections()
        j=0
        positions=dict()
        for id in ids: 
            positions[id.decode("utf-8")]=j
            j=j+1
        i=0
        self.id_dict=dict()
        for group in subscribed_groups:
            entry=gtk.Entry()
            entry.set_editable(False)
            entry.set_text(group[0])
            combo=gtk.combo_box_new_text()
            for id in ids: combo.append_text(id)
            combo.set_active(positions.get(group[2],0))
            self.id_dict[group[0]]=combo
            groups_table.attach(entry,0,1,i+1,i+2,gtk.EXPAND|gtk.FILL,gtk.FILL)
            groups_table.attach(combo,1,2,i+1,i+2,gtk.FILL,gtk.EXPAND|gtk.SHRINK)
            self.entries.append(entry)
            self.combos.append(combo)
            i=i+1
        
        viewport=gtk.Viewport()
        viewport.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        scrolledwin=gtk.ScrolledWindow()
        scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        #buttons hbox
        buttons_hbox=gtk.HBox()

        #cancel_button
        self.cancel_button=gtk.Button(None,gtk.STOCK_CANCEL)
        self.cancel_button_tooltip=gtk.Tooltips()
        self.cancel_button_tooltip.set_tip(self.cancel_button,_("Close window. Discard changes"))
        self.cancel_button.connect("clicked",self.destroy)
        buttons_hbox.pack_start(self.cancel_button,True,True,0)
        #ok_button
        self.ok_button=gtk.Button(None,gtk.STOCK_OK)
        self.ok_button.connect("clicked",self.save_configs)
        self.ok_button_tooltip=gtk.Tooltips()
        self.ok_button_tooltip.set_tip(self.ok_button,_("Close window and save settings"))
        buttons_hbox.pack_start(self.ok_button,True,True,0)
        self.ok_button.set_border_width(5)
        self.cancel_button.set_border_width(5)
        
        viewport.add(groups_table)
        scrolledwin.add(viewport)
        main_vbox.pack_start(scrolledwin,True,True,4)
        main_vbox.pack_start(buttons_hbox,False,False,0)
        self.win.add(main_vbox)
        #self.win.set_default_size(300,300)
        self.win.set_size_request(350,300)
