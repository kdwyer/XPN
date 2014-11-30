import gtk, gobject
import pango
import webbrowser
from os import remove as remove_file
from urllib import quote as url_quote
from xml.sax.saxutils import escape
from xpn_src.XFace import XFaceToBuffer,XFaceToBMP
from xpn_src.Headers_List import load_headers_list
import StringIO
import base64

class Article_Pane:
    def show(self):
        self.vbox.show()

    def hide(self):
        self.vbox.hide()

    def unparent(self):
        self.vbox.unparent()

    def get_widget(self):
        return self.vbox

    def update_expander_label(self):
        if not self.frame_shown:
            val="<b>"+_("Subject: ")+"</b>"+escape(self.subj)
            val=val+"    <b>"+_("From: ")+"</b>"+escape(self.nick)
            val=val+"    <b>"+_("Date: ")+"</b>"+escape(self.date_parsed)
            if not self.subj and not self.nick and not self.date_parsed:
                val="<b>"+_("Expand Headers Row")+"</b>"
            self.expander.get_label_widget().set_label(val)

    def show_hide_headers(self,button,signal):
        if not self.frame_shown:
            self.expander_tooltip.set_tip(self.expander,_("Hide Headers"))
            self.expander.get_label_widget().set_label("")
            self.frame_shown=True
        else:
            self.expander_tooltip.set_tip(self.expander,_("Expand Headers Row"))
            self.frame_shown=False
            self.update_expander_label()

    def add_parts_buttons(self,buttons_list):
        self.multiparts_buttons=[]
        for name,body in buttons_list:
            if len(self.multiparts_buttons)>0: group=self.multiparts_buttons[0]
            else: group=None
            button=gtk.RadioButton(group)
            button.set_mode(False)
            image=gtk.Image()
            image.set_from_file("pixmaps/part.xpm")
            label=gtk.Label(name)
            hbox=gtk.HBox()
            hbox.pack_start(image,False,True,2)
            hbox.pack_start(label,True,True,2)
            hbox.show_all()
            button.add(hbox)
            self.multiparts_hbox.pack_start(button,True,True,2)
            button.show()
            self.multiparts_buttons.append(button)
        self.multiparts_hbox.show()

    def clear_multiparts_area(self):
        try: self.multiparts_buttons
        except: self.multiparts_buttons=[]
        for button in self.multiparts_buttons:
            self.multiparts_hbox.remove(button)
        self.multiparts_buttons=[]
        self.multiparts_hbox.hide()

    def clear(self):
        self.update_headers_labels(None)
        self.delete_all()
        self.clear_multiparts_area()
        self.hide_faces()
    
    def update_headers_labels(self,article):
        if article:
            self.nick=article.nick
            self.subj=article.subj
            self.date_parsed=article.date_parsed
        else:
            self.nick=""
            self.subj=""
            self.date_parsed=""

        for header,(label_name,label_value) in self.values.iteritems():
            if article: value=article.get_hdr(header)
            else: value=""
            if value:
                label_name.show()
                label_value.show()
                label_value.set_text(value.encode("utf-8"))
            else:
                label_name.hide()
                label_value.hide()
                label_value.set_text("")
        self.update_expander_label()

    def delete_all(self):
        start,end=self.buffer.get_bounds()
        self.buffer.delete(start,end)

    def insert(self,string):
        mark=self.buffer.get_insert()
        iter=self.buffer.get_iter_at_mark(mark)
        self.buffer.insert(iter,string.encode("utf-8"))

    def insert_with_tags(self,string,tag):
        self.buffer.insert_with_tags_by_name(self.buffer.get_end_iter(),string.encode("utf-8"),tag)

    def insert_with_tags_at_iter(self,iter,string,tag):
        self.buffer.insert_with_tags_by_name(iter,string.encode("utf-8"),tag)

    def set_url_color(self,color):
        url_color=gtk.gdk.color_parse(color)
        self.tag_table=self.buffer.get_tag_table()
        if not self.tag_url:
            self.tag_url=gtk.TextTag("url")
            self.tag_table.add(self.tag_url)
            self.tag_url.set_property("underline",pango.UNDERLINE_SINGLE)
            self.tag_mid=gtk.TextTag("mid")
            self.tag_table.add(self.tag_mid)
            self.tag_mid.set_property("underline",pango.UNDERLINE_SINGLE)
        self.tag_url.set_property("foreground-gdk",url_color)
        self.tag_mid.set_property("foreground-gdk",url_color)

    def set_spoiler_color(self):
        spoiler_color=gtk.gdk.color_parse("#FF0000")
        self.tag_table=self.buffer.get_tag_table()
        if not self.tag_spoiler:
            self.tag_spoiler=gtk.TextTag("spoiler")
            self.tag_table.add(self.tag_spoiler)
        self.tag_spoiler.set_property("foreground-gdk",spoiler_color)
        self.tag_spoiler.set_property("background-gdk",spoiler_color)


    def set_text_color(self,color):
        text_color=gtk.gdk.color_parse(color)
        self.tag_table=self.buffer.get_tag_table()
        if not self.text_tag:
            self.text_tag=gtk.TextTag("text")
            self.tag_table.add(self.text_tag)
        self.text_tag.set_property("foreground-gdk",text_color)
        if not self.text_tag_bold:
            self.text_tag_bold=gtk.TextTag("text_bold")
            self.tag_table.add(self.text_tag_bold)
            self.text_tag_bold.set_property("weight",800)
        self.text_tag_bold.set_property("foreground-gdk",text_color)
        if not self.text_tag_italic:
            self.text_tag_italic=gtk.TextTag("text_italic")
            self.tag_table.add(self.text_tag_italic)
            self.text_tag_italic.set_property("style",pango.STYLE_ITALIC)
        self.text_tag_italic.set_property("foreground-gdk",text_color)
        if not self.text_tag_underline:
            self.text_tag_underline=gtk.TextTag("text_underline")
            self.tag_table.add(self.text_tag_underline)
            self.text_tag_underline.set_property("underline",pango.UNDERLINE_SINGLE)
        self.text_tag_underline.set_property("foreground-gdk",text_color)


    def set_quote_color(self,color,level):
        if level==1:
            quote1_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote1_tag:
                self.quote1_tag=gtk.TextTag("quote1")
                self.tag_table.add(self.quote1_tag)
            self.quote1_tag.set_property("foreground-gdk",quote1_color)
            if not self.quote1_tag_bold:
                self.quote1_tag_bold=gtk.TextTag("quote1_bold")
                self.tag_table.add(self.quote1_tag_bold)
            self.quote1_tag_bold.set_property("weight",1000)
            self.quote1_tag_bold.set_property("foreground-gdk",quote1_color)
            if not self.quote1_tag_italic:
                self.quote1_tag_italic=gtk.TextTag("quote1_italic")
                self.tag_table.add(self.quote1_tag_italic)
            self.quote1_tag_italic.set_property("style",pango.STYLE_ITALIC)
            self.quote1_tag_italic.set_property("foreground-gdk",quote1_color)
            if not self.quote1_tag_underline:
                self.quote1_tag_underline=gtk.TextTag("quote1_underline")
                self.tag_table.add(self.quote1_tag_underline)
            self.quote1_tag_underline.set_property("underline",pango.UNDERLINE_SINGLE)
            self.quote1_tag_underline.set_property("foreground-gdk",quote1_color)

            
        elif level==2: 
            quote2_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote2_tag:
                self.quote2_tag=gtk.TextTag("quote2")
                self.tag_table.add(self.quote2_tag)
            self.quote2_tag.set_property("foreground-gdk",quote2_color)
            if not self.quote2_tag_bold:
                self.quote2_tag_bold=gtk.TextTag("quote2_bold")
                self.tag_table.add(self.quote2_tag_bold)
            self.quote2_tag_bold.set_property("weight",1000)
            self.quote2_tag_bold.set_property("foreground-gdk",quote2_color)
            if not self.quote2_tag_italic:
                self.quote2_tag_italic=gtk.TextTag("quote2_italic")
                self.tag_table.add(self.quote2_tag_italic)
            self.quote2_tag_italic.set_property("style",pango.STYLE_ITALIC)
            self.quote2_tag_italic.set_property("foreground-gdk",quote2_color)
            if not self.quote2_tag_underline:
                self.quote2_tag_underline=gtk.TextTag("quote2_underline")
                self.tag_table.add(self.quote2_tag_underline)
            self.quote2_tag_underline.set_property("underline",pango.UNDERLINE_SINGLE)
            self.quote2_tag_underline.set_property("foreground-gdk",quote2_color)
            
        else:    
            quote3_color=gtk.gdk.color_parse(color)
            self.tag_table=self.buffer.get_tag_table()
            if not self.quote3_tag:
                self.quote3_tag=gtk.TextTag("quote3")
                self.tag_table.add(self.quote3_tag)
            self.quote3_tag.set_property("foreground-gdk",quote3_color)
            if not self.quote3_tag_bold:
                self.quote3_tag_bold=gtk.TextTag("quote3_bold")
                self.tag_table.add(self.quote3_tag_bold)
            self.quote3_tag_bold.set_property("weight",1000)
            self.quote3_tag_bold.set_property("foreground-gdk",quote3_color)
            if not self.quote3_tag_italic:
                self.quote3_tag_italic=gtk.TextTag("quote3_italic")
                self.tag_table.add(self.quote3_tag_italic)
            self.quote3_tag_italic.set_property("style",pango.STYLE_ITALIC)
            self.quote3_tag_italic.set_property("foreground-gdk",quote3_color)
            if not self.quote3_tag_underline:
                self.quote3_tag_underline=gtk.TextTag("quote3_underline")
                self.tag_table.add(self.quote3_tag_underline)
            self.quote3_tag_underline.set_property("underline",pango.UNDERLINE_SINGLE)
            self.quote3_tag_underline.set_property("foreground-gdk",quote3_color)
            

    def set_sign_color(self,color):
        sign_color=gtk.gdk.color_parse(color)
        self.tag_table=self.buffer.get_tag_table()
        if not self.sign_tag:
            self.sign_tag=gtk.TextTag("sign")
            self.tag_table.add(self.sign_tag)
        self.sign_tag.set_property("foreground-gdk",sign_color)
        if not self.sign_tag_bold:
            self.sign_tag_bold=gtk.TextTag("sign_bold")
            self.tag_table.add(self.sign_tag_bold)
            self.sign_tag_bold.set_property("weight",800)
        self.sign_tag_bold.set_property("foreground-gdk",sign_color)
        if not self.sign_tag_italic:
            self.sign_tag_italic=gtk.TextTag("sign_italic")
            self.tag_table.add(self.sign_tag_italic)
            self.sign_tag_italic.set_property("style",pango.STYLE_ITALIC)
        self.sign_tag_italic.set_property("foreground-gdk",sign_color)
        if not self.sign_tag_underline:
            self.sign_tag_underline=gtk.TextTag("sign_underline")
            self.tag_table.add(self.sign_tag_underline)
            self.sign_tag_underline.set_property("underline",pango.UNDERLINE_SINGLE)
        self.sign_tag_underline.set_property("foreground-gdk",sign_color)

    def set_background(self,color):
        color=gtk.gdk.color_parse(color)
        self.textview.modify_base(gtk.STATE_NORMAL,color)
        self.textview.modify_text(gtk.STATE_NORMAL,gtk.gdk.color_parse("#FFFFFF"))

    def get_url_at_coords(self,old_x,old_y):
        x,y=self.textview.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT,int(old_x),int(old_y))
        iter=self.textview.get_iter_at_location(x,y)
        is_url=iter.has_tag(self.tag_url)
        is_mid=iter.has_tag(self.tag_mid)
        url=""
        if is_url:
            #let's get the url
            start=iter.copy()
            stop=iter.copy()
            start.backward_to_tag_toggle(self.tag_url)
            stop.forward_to_tag_toggle(self.tag_url)
            url=self.buffer.get_text(start,stop,True)
        if is_mid:
            #let's get the url
            start=iter.copy()
            stop=iter.copy()
            start.backward_to_tag_toggle(self.tag_mid)
            stop.forward_to_tag_toggle(self.tag_mid)
            url=self.buffer.get_text(start,stop,True)
        return url,is_url

    def mouse_move(self,obj,event):
        cursor_std=gtk.gdk.Cursor(gtk.gdk.XTERM)
        cursor_url=gtk.gdk.Cursor(gtk.gdk.HAND2)
        if event.is_hint:
            x,y,state=event.window.get_pointer()
        else:
            x,y=event.get_coords()
        url,is_url=self.get_url_at_coords(x,y)
        if url!="":
            event.window.set_cursor(cursor_url)
        else:
            event.window.set_cursor(cursor_std)

    def button_press(self,obj,event):
        if (event.button==1):
            url,is_url=self.get_url_at_coords(event.x,event.y)
            if url!="":
                if is_url:
                    if self.use_custom_browser:
                        launcher=webbrowser.get("xpn_launcher")
                        launcher.open(url)
                    else:
                        webbrowser.open(url)
                else:
                    if url.startswith("news:"): url=url.replace("news:","")
                    self.vbox.emit("mid_clicked",url)

 
    def set_face_x_face(self,face,x_face):
        if face:
            self.set_face(face)
        elif x_face:
            self.set_x_face(x_face)
        else:
            self.hide_faces()

    def set_x_face(self,x_face):
        buff=XFaceToBMP(x_face)
        f1=StringIO.StringIO(buff)
        f1.seek(0)
        x_face_decoded=f1.read()
        f1.close()
        pixbuf_loader=gtk.gdk.PixbufLoader()
        pixbuf_loader.set_size(48,48)
        pixbuf_loader.write(x_face_decoded)
        pixbuf_loader.close()
        pixbuf=pixbuf_loader.get_pixbuf()
        self.x_face_image.set_from_pixbuf(pixbuf)
        self.face_image.hide()
        self.x_face_image.show()
        self.face_frame.show()

    def set_face(self,face):
        f1=StringIO.StringIO(face)
        f2=StringIO.StringIO()
        try:
            base64.decode(f1,f2)
        except:
            f1.close()
            f2.close()
        else:
            f1.close()
            f2.seek(0)
            face_decoded=f2.read()
            f2.close()
            pixbuf_loader=gtk.gdk.PixbufLoader()
            pixbuf_loader.set_size(48,48)
            pixbuf_loader.write(face_decoded)
            pixbuf_loader.close()
            pixbuf=pixbuf_loader.get_pixbuf()
            self.face_image.set_from_pixbuf(pixbuf)
            self.face_image.show()
            self.x_face_image.hide()
            self.face_frame.show()


    def hide_faces(self):
        self.face_frame.hide()
        self.x_face_image.hide()
        self.face_image.hide()

    def set_headers_colors(self,bg,fg):
        bgcolor=gtk.gdk.color_parse(bg)
        fgcolor=gtk.gdk.color_parse(fg)
        self.evbox.modify_bg( gtk.STATE_NORMAL, bgcolor )
        #self.evbox.modify_fg( gtk.STATE_NORMAL, fgcolor )
        label=self.expander.get_label_widget()
        label.modify_fg( gtk.STATE_NORMAL, fgcolor )
        for child in self.headers_table.get_children():
            child.modify_fg( gtk.STATE_NORMAL, fgcolor )

    def repopulate_headers(self):
        self.values=dict()
        hlist=load_headers_list()
        for child in self.headers_table.get_children():
            self.headers_table.remove(child)
        i=0
        for header in hlist:
                label=gtk.Label("<b>"+header+":"+"</b>")
                label.set_use_markup(True)
                label.set_alignment(1,0.5)
                value=gtk.Label("")
                value.set_alignment(0,0.5)
                value.set_padding(5,1)
                self.values[header]=(label,value)
                self.headers_table.attach(label,0,1,i,i+1,gtk.FILL,gtk.FILL)
                self.headers_table.attach(value,1,2,i,i+1)
                i=i+1
                label.show()
                value.show()


    def __init__(self,show_headers,configs):
        #VBox
        self.vbox=gtk.VBox()
        gobject.signal_new("mid_clicked",gtk.VBox,gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_STRING,))
  
        self.expander=gtk.Expander()
        self.evbox=gtk.EventBox()

      
        self.evbox.add(self.expander)
        self.evbox.show_all()
        self.vbox.pack_start(self.evbox,False,True,0)
        
        self.expander_tooltip=gtk.Tooltips()
        if show_headers==True:
            self.expander.set_expanded(True)
            self.expander_tooltip.set_tip(self.expander,_("Hide Headers"))
            exp_label=gtk.Label("")
            self.frame_shown=True
        else:
            self.expander.set_expanded(False)
            self.expander_tooltip.set_tip(self.expander,_("Expand Headers Row"))
            exp_label=gtk.Label("<b>"+_("Expand Headers Row")+"</b>")
            self.frame_shown=False
        exp_label.set_use_markup(True)
        exp_label.show()
        self.expander.set_label_widget(exp_label)
        self.expander.connect("notify::expanded",self.show_hide_headers)
        

        self.multiparts_hbox=gtk.HBox()
        self.vbox.pack_start(self.multiparts_hbox,False,True,2)
        self.multiparts_hbox.hide()

        self.headers_table=gtk.Table(6,2,False)
        self.headers_table.set_border_width(2)
        headers_hbox=gtk.HBox()
        headers_hbox.pack_start(self.headers_table,True,True,4)
        headers_hbox.set_border_width(2)
        

        self.x_face_image=gtk.Image()
        self.x_face_image.set_size_request(48,48)

        self.face_image=gtk.Image()
        self.face_image.set_size_request(48,48)
        
        faces_hbox=gtk.HBox()
        fake_label=gtk.Label()
        faces_vbox=gtk.VBox()
        self.face_frame=gtk.Frame()
        #self.face_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        faces_hbox.set_size_request(48,48)
        faces_hbox.pack_start(self.face_image,False,False)        
        faces_hbox.pack_start(self.x_face_image,False,False)
        faces_vbox.pack_start(self.face_frame,False,False)
        faces_vbox.pack_start(fake_label,True,True)
        self.face_frame.add(faces_hbox)
        headers_hbox.pack_start(faces_vbox,False,False)
        self.expander.add(headers_hbox)
        headers_hbox.show_all()
        self.x_face_image.hide()
        self.face_image.hide()
        self.face_frame.hide()

        self.repopulate_headers()

        #TextScrolledWindow
        self.text_scrolledwin=gtk.ScrolledWindow()
        self.text_scrolledwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.text_scrolledwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.vbox.pack_start(self.text_scrolledwin,True,True,0)
        self.text_scrolledwin.show()

        #TextBuffer
        self.buffer=gtk.TextBuffer()

        #TextView
        self.textview=gtk.TextView(self.buffer)
        self.text_scrolledwin.add(self.textview)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.show()
        self.textview.add_events(gtk.gdk.POINTER_MOTION_MASK|gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.textview.connect("motion-notify-event",self.mouse_move)
        self.textview.connect("button-release-event",self.button_press)

        self.quote1_tag=None
        self.quote1_tag_bold=None
        self.quote1_tag_italic=None
        self.quote1_tag_underline=None
        self.quote2_tag=None
        self.quote2_tag_bold=None
        self.quote2_tag_italic=None
        self.quote2_tag_underline=None
        self.quote3_tag=None
        self.quote3_tag_bold=None
        self.quote3_tag_italic=None
        self.quote3_tag_underline=None
        self.sign_tag=None
        self.sign_tag_bold=None
        self.sign_tag_italic=None
        self.sign_tag_underline=None
        self.text_tag=None
        self.text_tag_bold=None
        self.text_tag_italic=None
        self.text_tag_underline=None
        self.tag_url=None
        self.tag_mid=None
        self.tag_spoiler=None

        color=configs["text_color"]
        self.set_text_color(color)
        color=configs["quote1_color"]
        self.set_quote_color(color,1)
        color=configs["quote2_color"]
        self.set_quote_color(color,2)
        color=configs["quote3_color"]
        self.set_quote_color(color,3)
        color=configs["sign_color"]
        self.set_sign_color(color)
        color=configs["background_color"]
        self.set_background(color)
        color=configs["url_color"]
        self.set_url_color(color)
        self.set_spoiler_color()

        self.set_headers_colors(configs["headers_bg_color"],configs["headers_fg_color"])

        if configs["custom_browser"]=="True":
            self.use_custom_browser=True
            webbrowser.register("xpn_launcher",None,webbrowser.GenericBrowser(configs["browser_launcher"]))
        else:
            self.use_custom_browser=False
