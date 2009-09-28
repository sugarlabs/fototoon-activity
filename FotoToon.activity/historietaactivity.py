# -*- coding: UTF8 -*-

import os
import math
import gtk
import gobject
import cairo
import pango

import globos

from sugar.activity import activity
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.combobox import ComboBox


class HistorietaActivity(activity.Activity):
	def __init__(self, handle):
		print "INICIALIZANDO HISTORIETA"
		activity.Activity.__init__(self, handle)
		self.set_title('Historieta')
        
		self.connect("key_press_event", self.keypress)
	
		toolbox = activity.ActivityToolbox(self)
        
		self.botonera = gtk.Toolbar()
		# agregar cuadro
		self.b_add_photo = ToolButton('add-photo')
		self.b_add_photo.connect('clicked', self.add_photo)
		self.botonera.insert(self.b_add_photo, -1)
		self.b_add_photo.show()

		# agrega globo
		self.b_agregar = ToolButton('add-globe')
		self.b_agregar.connect('clicked', self.agrega_gnormal)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()
	
		#agrega nube
		self.b_agregar = ToolButton('add-nube')
		self.b_agregar.connect('clicked', self.agrega_gpensar)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()
	
		# agrega susurro
		self.b_agregar = ToolButton('add-susurro')
		self.b_agregar.connect('clicked', self.agrega_gdespacio)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()
	
		# agrega grito
		self.b_agregar = ToolButton('add-grito')
		self.b_agregar.connect('clicked', self.agrega_ggrito)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()
	
		# agrega caja
		self.b_agregar = ToolButton('add-box')
		self.b_agregar.connect('clicked', self.agrega_grect)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()
	
		# girar
		self.b_agregar = ToolButton('turn')
		self.b_agregar.connect('clicked', self.agrega_grect)
		self.botonera.insert(self.b_agregar, -1)
		self.b_agregar.show()

		# font 



        
		toolbox.add_toolbar('Globos', self.botonera)
		self.botonera.show()
	
		self.set_toolbox(toolbox)
		toolbox.show()
		toolbox.set_current_toolbar(1)        

		scrolled = gtk.ScrolledWindow()
		self.pagina = Pagina()
		scrolled.add_with_viewport(self.pagina)
		self.pagina.show()
		scrolled.show()
		self.set_canvas(scrolled)
		self.show()

	def keypress(self, widget, event):
		self.pagina.cuadro_activo.keypress(event.string,event.keyval)

	def add_photo(self, boton):
		self.pagina.add_photo()

	def agrega_gnormal(self, boton):
		self.pagina.cuadro_activo.add_globo(40, 40)

	def agrega_gnormal(self, boton):
		#dir=self.direccion_combo_valores[self.direccion_combo.get_active()]
		#self.pagina.cuadro_activo.add_globo(40, 40,gdireccion=dir)
		self.pagina.cuadro_activo.add_globo(40, 40)
	
	def agrega_gpensar(self, boton):
		self.pagina.cuadro_activo.add_nube(40, 40)
	
	def agrega_gdespacio(self, boton):
		self.pagina.cuadro_activo.add_globo(40, 40,gmodo="despacio")
	
	def agrega_ggrito(self, boton):
		self.pagina.cuadro_activo.add_grito(40, 40)
	
	def agrega_grect(self, boton):
		self.pagina.cuadro_activo.add_rectangulo(40, 40)
	
	def agrega_imagen(self, boton):
		self.pagina.cuadro_activo.add_imagen(40, 40)
	
	def setWaitCursor( self ):
		self.window.set_cursor( gtk.gdk.Cursor(gtk.gdk.WATCH) )

	def setDefaultCursor( self ):
		self.window.set_cursor( None )
        
DEF_SPACING = 6
DEF_WIDTH = 4

class Pagina(gtk.Table):

	def __init__(self):
		gtk.Table.__init__(self, 2, 2, True)
		self.set_homogeneous(True)
		self.set_row_spacings(DEF_SPACING)
		self.set_col_spacings(DEF_SPACING)

		self.cuadros = []
		self.cuadro_activo = None


	def add_photo(self):
		appdir = activity.get_bundle_path()
		posi = len(self.cuadros)
		cuadro = Cuadro(gtk.gdk.pixbuf_new_from_file(os.path.join(appdir,'fotos/foto'+str(posi)+'.jpg')))
		cuadro.show()
		reng = int(posi / 2)
		column = posi - (reng * 2)
		self.attach(cuadro,column,column+1,reng,reng+1,)
		self.cuadro_activo = cuadro
		self.cuadros.append(cuadro)
		cuadro.pagina = self


class Cuadro(gtk.DrawingArea):

	def __init__(self, pixbuf):
		print ("Cuadro INIT")
		gtk.DrawingArea.__init__(self)
		#se agregan los eventos de pulsación y movimiento del ratón
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK \
                        |gtk.gdk.BUTTON1_MOTION_MASK)

		#self.globos es una lista que contiene los globos de ese cuadro
		self.globos = []
        
		self.pixbuf = pixbuf
		self.glob_press = False
		self.is_dimension = False
		self.is_punto = False
		self.pagina = None

		self.connect("expose_event", self.expose)
		self.connect("button_press_event", self.pressing)
		self.connect("motion_notify_event", self.moving)
		self.connect("button_release_event", self.releassing)
		self.queue_draw()

	#def get_size_request(self)
	#	return 100,100
        
	def add_globo(self,xpos,ypos,gmodo="normal",gdireccion="abajo"):
		#agrega un globo al cuadro
		self.globos.append(globos.Globo(x=xpos,y=ypos,modo=gmodo,direccion=gdireccion))
		self.queue_draw()
	
	def add_rectangulo(self,xpos,ypos):
		#agrega un cuadro de texto al cuadro
		self.globos.append(globos.Rectangulo(x=xpos,y=ypos))
		self.queue_draw()
	
	def add_nube(self,xpos,ypos):
		#agrega un globo de pensamiento al cuadro
		self.globos.append(globos.Nube(x=xpos,y=ypos))
		self.queue_draw()

	def add_imagen(self,xpos,ypos):
		#agrega una imagen al cuadro
		self.globos.append(globos.Imagen(x=xpos,y=ypos))
		self.queue_draw()
	
	def add_grito(self,xpos,ypos):
		#agrega un globo de grito al cuadro
		self.globos.append(globos.Grito(x=xpos,y=ypos))
		self.queue_draw()
     
	def expose(self,widget,event):
		print "EXPOSE"
		self.context = widget.window.cairo_create()
		self.draw(self.context, event.area)
		return False

	def set_sink(self, sink):
		assert self.window.xid
		self.imagesink = sink
		self.imagesink.set_xwindow_id(self.window.xid)


	def draw(self, context, area):
		# Dibujamos la foto
		context.set_line_width(DEF_WIDTH)
		context.set_source_pixbuf(self.pixbuf, area.x, area.y)
		context.paint()

		# Dibujamos el recuadro
		context.rectangle(area.x, area.y, area.width, area.height)
		context.set_source_rgb(0, 0, 0)
		context.stroke() 

		# Por ultimo dibujamos los globos
		self.draw_globos(context)

	def draw_globos(self, context):
		if len(self.globos) > 0:
			for g in self.globos:
				g.imprimir(context)

	def keypress(self,key,keyval):
		if self.glob_press:
			self.glob_press.set_texto(key,keyval,self.context,self.get_allocation())
			self.queue_draw()
			#print gtk.gdk.keyval_name(keyval)
		
	def pressing(self, widget, event):
		self.pagina.cuadro_activo = self
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
						self.glob_press=i
						break
					self.queue_draw()

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

        
    
