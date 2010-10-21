# -*- coding: UTF8 -*-

import os
import math
import gtk
import gobject
import cairo
import pango

import globos
import persistencia

from sugar.activity import activity
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from toolbar import TextToolbar
from toolbar import GlobesToolbar

import time
from sugar.datastore import datastore
from sugar import profile
from sugar.graphics import style
from sugar.graphics.menuitem import MenuItem
import dbus
import logging


class HistorietaActivity(activity.Activity):

    _EXPORT_FORMATS = [['image/png', _('Save as Image'), _('PNG'), ""]]


    def __init__(self, handle):
        print "INICIALIZANDO FOTOTOON"
        activity.Activity.__init__(self, handle)
        self.set_title('FotoToon')
        
        self.connect("key_press_event", self.keypress)
    
        toolbox = activity.ActivityToolbox(self)
        
        self.page = Page()

        self.globesToolbar = GlobesToolbar(self.page,self)
        toolbox.add_toolbar(_('Globes'), self.globesToolbar)

        # fonts
        self.textToolbar = TextToolbar(self.page)
        toolbox.add_toolbar(_('Text'), self.textToolbar)

        """
        # agrego boton para grabar como imagen
        toolbox._activity_toolbar
        b_exportar = ToolButton('save-as-image')
        b_exportar.connect('clicked', self.write_image)
        b_exportar.set_tooltip(_('Save as Image'))
        toolbox._activity_toolbar.insert(b_exportar, 4)
        """

        self._activity_toolbar = toolbox.get_activity_toolbar()
        self._keep_palette = self._activity_toolbar.keep.get_palette()

        # hook up the export formats to the Keep button
        for i, f in enumerate(self._EXPORT_FORMATS):
            menu_item = MenuItem(f[1])
            #menu_item.connect('activate', self.write_image, f[0], f[2], f[3])
            menu_item.connect('activate', self.write_image)
            self._keep_palette.menu.append(menu_item)
            menu_item.show()

        self._max_participants = 0
        
        self.set_toolbox(toolbox)
        toolbox.show_all()
        toolbox.set_current_toolbar(1)        


        toolbox.get_activity_toolbar().title.connect("focus-in-event", self.on_title)

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        scrolled.add_with_viewport(self.page)
        scrolled.show_all()
        self.set_canvas(scrolled)
        self.show()
        self.metadata['mime_type'] = 'application/x-fototoon-activity'
        #print "screen witdh " , SCREEN_WIDTH
        #print "page witdh " , self.page.size_request()

    def keypress(self, widget, event):
        if (self.page.get_active_box() != None):
            return self.page.get_active_box().keypress(event.string,event.keyval)
        else:    
            return False

    # quiero que al ingresar al titulo se des seleccione el globo seleccionado        
    def on_title(self, widget, event):
        print "Ingresando al titulo"
        if (self.page.get_active_box() != None):
            box = self.page.get_active_box() 
            self.page.set_active_box(None)            
            box.glob_press = False
            box.set_globo_activo(None)
            box.queue_draw()
            
            print "Fin de Ingresando al titulo"
    
#    def setWaitCursor( self ):
#        self.window.set_cursor( gtk.gdk.Cursor(gtk.gdk.WATCH) )

#    def setDefaultCursor( self ):
#        self.window.set_cursor( None )
        
    def write_file(self, file_path):
        print "write file path",file_path
        persistence = persistencia.Persistence()
        persistence.write(file_path,self.page)

    def read_file(self, file_path):
        print "read file path",file_path
        persistence = persistencia.Persistence()
        persistence.read(file_path,self.page)

    def write_image(self,button):
        # calculate image size 
        image_height, image_width = 0,0
        posi = 0
        for box in self.page.boxs:
            if posi > 0:
                try:
                    reng = int((posi + 1) / 2)
                    column = (posi + 1) - (reng * 2)
                    logging.error("reng %d column %d" % (reng,column))
                    if column == 0:
                        image_height = image_height + box.height
                except:
                    pass
            else:
                image_width = box.width
                image_height = image_height + box.height
            posi = posi + 1
        
        
        logging.error( "image_width %d image_height %d" % (image_width,image_height))
        #pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, width + 1, height + 1)
        surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, image_width + 1, image_height + 1)
        ctx = cairo.Context (surface)

        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, image_width + 1, image_height + 1)
        ctx.fill()

        posi = 0
        y_posi = 0
        for box in self.page.boxs:
            logging.error("posi %d" % (posi))

            if posi > 0:
                try:
                    reng = int((posi + 1) / 2)
                    column = (posi + 1) - (reng * 2)
                    logging.error("reng %d column %d" % (reng,column))
                    ctx.rectangle(column * box.width, y_posi, (column + 1) * box.width, y_posi + box.height)
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.stroke() 
                    ctx.translate(column * box.width, y_posi)
                    box.draw_in_context(ctx)
                    ctx.translate(- column * box.width, - y_posi)
                    if column == 1:
                        y_posi = y_posi + box.height
                except:
                    pass
            else:
                box.draw_in_context(ctx)
                y_posi = box.height
            
            posi = posi + 1


        temp_file_name = os.path.join(self.get_activity_root(), 'instance',
                                 'tmp-%i.png' % time.time())

        surface.write_to_png (temp_file_name)
        logging.error("temp file name  %s" % (temp_file_name))

        self.dl_jobject = datastore.create()

        self.dl_jobject.metadata['progress'] = '0'
        self.dl_jobject.metadata['keep'] = '0'
        self.dl_jobject.metadata['buddies'] = ''
        self.dl_jobject.metadata['icon-color'] = \
                profile.get_color().to_string()
        self.dl_jobject.metadata['mime_type'] = 'image/png'

        self.dl_jobject.metadata['title'] = self._jobject.metadata['title'] + " as image"
        self.dl_jobject.metadata['description'] = ""
        self.dl_jobject.metadata['progress'] = '100'
        self.dl_jobject.file_path = temp_file_name

        self.dl_jobject.metadata['preview'] = self._get_preview_image(temp_file_name)

        datastore.write(self.dl_jobject, transfer_ownership=True)


    def _get_preview_image(self,file_name):
        preview_width, preview_height = style.zoom(300), style.zoom(225)

        pixbuf = gtk.gdk.pixbuf_new_from_file(file_name)
        width, height = pixbuf.get_width(), pixbuf.get_height()

        scale = 1
        if (width > preview_width) or (height > preview_height):
            scale_x = preview_width / float(width)
            scale_y = preview_height / float(height)
            scale = min(scale_x, scale_y)

        pixbuf2 = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, \
                            pixbuf.get_has_alpha(), \
                            pixbuf.get_bits_per_sample(), \
                            preview_width, preview_height)
        pixbuf2.fill(style.COLOR_WHITE.get_int())

        margin_x = int((preview_width - (width * scale)) / 2)
        margin_y = int((preview_height - (height * scale)) / 2)

        pixbuf.scale(pixbuf2, margin_x, margin_y, \
                            preview_width - (margin_x * 2), \
                            preview_height - (margin_y * 2), \
                            margin_x, margin_y, scale, scale, \
                            gtk.gdk.INTERP_BILINEAR)

        preview_data = []
        def save_func(buf, data):
            data.append(buf)

        pixbuf2.save_to_callback(save_func, 'png', user_data=preview_data)
        preview_data = ''.join(preview_data)
        return dbus.ByteArray(preview_data)

DEF_SPACING = 6
DEF_WIDTH = 4

SCREEN_HEIGHT = gtk.gdk.screen_height()
SCREEN_WIDTH = gtk.gdk.screen_width()
BOX_HEIGHT = 450


class Page(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self,False,0)        
        self.set_homogeneous(False)

        self.boxs = []
        self._active_box = None

        logging.error('SCREEN WIDTH %d DEF_SPACING %d' % (SCREEN_WIDTH, DEF_SPACING))

        # Agrego cuadro titulo
        self.title_box = ComicBox(None,0)
        self.title_box.show()
        self.title_box.set_size_request(SCREEN_WIDTH, 100)
        self.title_box.width, self.title_box.height = SCREEN_WIDTH, 100        
        self.pack_start(self.title_box,False)        
        self.set_active_box(self.title_box)
        self.boxs.append(self.title_box)
        self.title_box.page = self

        # Agrego tabla para las fotos
        self.table = gtk.Table(10, 2, True)
        self.table.set_homogeneous(True)
        self.table.set_row_spacings(DEF_SPACING)
        self.table.set_col_spacings(DEF_SPACING)
        self.pack_start(self.table)        
   
    def add_box_from_journal_image(self,image_file_name):
        posi = len(self.boxs) - 1
        num_foto = posi -  (posi / 4) * 4
        box = ComicBox(image_file_name,posi)
        reng = int(posi / 2) 
        column = posi - (reng * 2)
        self.table.attach(box,column,column+1,reng,reng+1)
        self.set_active_box(box)
        self.boxs.append(box)
        box.page = self
        box.show()


    def set_active_box(self,box):
        box_anterior = None 
        if (self._active_box != None):
            box_anterior =  self._active_box
        self._active_box = box
        if (box != None):        
            box.queue_draw()
        if (box_anterior != None):
            box_anterior.queue_draw()            

    def get_active_box(self):
        return self._active_box

    def get_globo_activo(self):
        box = self.get_active_box()
        if box != None:
            if (box.get_globo_activo() != None):
                return box.get_globo_activo()
        return None


class ComicBox(gtk.DrawingArea):

    def __init__(self, image_file_name,posi):
        print ("Cuadro INIT")
        gtk.DrawingArea.__init__(self)
        #se agregan los eventos de pulsacion y movimiento del raton
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK \
                        |gtk.gdk.BUTTON1_MOTION_MASK)

        #self.globos es una lista que contiene los globos de ese cuadro
        self.globos = []
        self.posi = posi
        
        #self.pixbuf = pixbuf
        self.glob_press = False
        self.is_dimension = False
        self.is_punto = False
        self.page = None
        self.image_name = ""
        self.image = None
        self.image_saved = False
        
        self.width = (int) (SCREEN_WIDTH - DEF_SPACING) / 2
        self.height = BOX_HEIGHT
        
        if (image_file_name != None):       
            self.image_name = image_file_name

        self._globo_activo = None

        self.set_size_request(-1,BOX_HEIGHT)

        self.connect("expose_event", self.expose)
        self.connect("button_press_event", self.pressing)
        self.connect("motion_notify_event", self.moving)
        self.connect("button_release_event", self.releassing)
        self.queue_draw()

    def set_globo_activo(self,globo):
        if (globo == None):
            self._globo_activo.selec = False
        else:
            globo.selec = True
        self._globo_activo = globo
        if (globo != None):
            self.page._text_toolbar.setToolbarState(globo.texto)
        
    def get_globo_activo(self):
        return self._globo_activo
        
    def add_globo(self,xpos,ypos,gmodo="normal",gdireccion=globos.DIR_ABAJO):
        #agrega un globo al cuadro
        globo = globos.Globo(x=xpos,y=ypos,modo=gmodo,direccion=gdireccion)
        self.globos.append(globo)
        self._globo_activo = globo
        self.queue_draw()
    
    def add_rectangulo(self,xpos,ypos):
        #agrega un cuadro de texto al cuadro
        self.globos.append(globos.Rectangulo(x=xpos,y=ypos))
        self.queue_draw()
    
    def add_nube(self,xpos,ypos):
        #agrega un globo de pensamiento al cuadro
        globo = globos.Nube(x=xpos,y=ypos)
        self.globos.append(globo)
        self._globo_activo = globo
        self.queue_draw()

    def add_imagen(self,xpos,ypos):
        #agrega una imagen al cuadro
        globo = globos.Imagen(x=xpos,y=ypos)
        self.globos.append(globo)
        self._globo_activo = globo
        self.queue_draw()
    
    def add_grito(self,xpos,ypos):
        #agrega un globo de grito al cuadro
        globo = globos.Grito(x=xpos,y=ypos)
        self.globos.append(globo)
        self._globo_activo = globo
        self.queue_draw()
     
    def expose(self,widget,event):
        self.context = widget.window.cairo_create()
        self.draw(self.context, event.area,widget.window)
        return False

    def set_sink(self, sink):
        assert self.window.xid
        self.imagesink = sink
        self.imagesink.set_xwindow_id(self.window.xid)


    def draw(self, ctx, area,window):
        self.draw_in_context(ctx)

    def draw_in_context(self, ctx):
        # Dibujamos la foto
        ctx.set_line_width(DEF_WIDTH)

        self.image_height = 0
        
        
        # print "self.image_name", self.image_name
        instance_path =  os.path.join(activity.get_activity_root(), "instance")
        if (self.image == None) and (self.image_name != ""):            
            # si la imagen no tiene el path viene del archivo de historieta ya grabado,
            # si viene con path, es una imagen que se tomo del journal
            if (not self.image_name.startswith(instance_path)):
                pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(instance_path,self.image_name))
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file(self.image_name)
            width_pxb = pixbuf.get_width()
            height_pxb = pixbuf.get_height()
            scale = (self.width) / (1.0 * width_pxb)            
            # print "self.width", self.width, "width_pxb",width_pxb, "scale",scale
            self.image_height = scale * height_pxb
            self.image = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.image_height)
            if (scale != 1):
                # falta tener en cuenta el caso de una imagen que venga del journal y tenga el tamanio justo, es decir con scale = 1
                pixb_scaled = pixbuf.scale_simple(int(self.width), int(self.image_height), gtk.gdk.INTERP_BILINEAR)
                ct = cairo.Context(self.image)
                gtk_ct = gtk.gdk.CairoContext(ct)
                gtk_ct.set_source_pixbuf(pixb_scaled,0,0)
                gtk_ct.paint()
                if (not self.image_saved):
                    self.image_saved = True
                    # print instance_path
                    image_file_name = "image"+str(self.posi)+".jpg"
                    pixb_scaled.save(os.path.join(instance_path,image_file_name),"jpeg")
                    # grabamos el nombre de la imagen sin el path
                    self.image_name = image_file_name

            else:                                                
                ct = cairo.Context(self.image)
                gtk_ct = gtk.gdk.CairoContext(ct)
                gtk_ct.set_source_pixbuf(pixbuf,0,0)
                gtk_ct.paint()


        if (self.image != None):
            ctx.set_source_surface (self.image, 0, 0)
            ctx.rectangle(0,0, self.width, self.height)
            ctx.paint()


        # Dibujamos el recuadro
        ctx.rectangle(0,0, self.width, self.height)
        if (self.page.get_active_box() == self):
            ctx.set_source_rgb(1, 1, 1)
        else :
            ctx.set_source_rgb(0, 0, 0)
        ctx.stroke() 
        ctx.set_source_rgb(0, 0, 0)

        # Por ultimo dibujamos los globos
        self.draw_globos(ctx)


    def draw_globos(self, context):
        if len(self.globos) > 0:
            for g in self.globos:
                logging.error("drawing globe %s", g.texto.texto)
                g.imprimir(context)

    def keypress(self,key,keyval):
        if self.glob_press:
            self.glob_press.set_texto(key,keyval,self.context,self.get_allocation())
            self.queue_draw()
            return True
        else:    
            return False
        
    def pressing(self, widget, event):
        # si no es el cuadro seleccionado actualmente redibujo este y el anterior seleccionado
        if (self.page.get_active_box() != self):
            self.page.set_active_box(self)

        #Verifica si al pulsar el mouse se hizo sobre algun globo
        if self.glob_press:
            if self.glob_press.is_selec_tam(event.x,event.y):
                self.is_dimension=True
            elif self.glob_press.is_selec_punto(event.x,event.y):
                self.is_punto=True

        if (not self.is_dimension) and not (self.is_punto):
            if self.glob_press:
                #self.glob_press.is_selec(event.x,event.y)
                self.glob_press.no_selec()
                self.glob_press=False

            if self.globos:
                list_aux=self.globos[:]
                list_aux.reverse()
                for i in list_aux:
                    if i.is_selec(event.x,event.y):
                        # i.mover_a(event.x,event.y,self.get_allocation())
                        self.glob_press = i
                        self.set_globo_activo(i)
                        self.queue_draw()
                        break

    def releassing(self, widget, event):
        #Cuando se deja de pulsar el mouse
        #self.glob_press=False
        self.is_dimension=False
        self.is_punto=False
            
    def moving(self, widget, event):
        if self.is_dimension:
            self.glob_press.set_dimension(event.x,event.y,self.get_allocation(),self.context)
            self.queue_draw()
        elif self.is_punto:
            self.glob_press.mover_punto(event.x,event.y,self.get_allocation())
            self.queue_draw()
        elif self.glob_press:
            self.glob_press.mover_a(event.x,event.y,self.get_allocation())
            self.queue_draw()

        
    
