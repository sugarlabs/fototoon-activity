# -*- coding: UTF_8 -*-


import os
import math
import gtk
import gobject
import cairo
import pango

import sugar.env
from sugar.activity import activity

ANCHO_LINEAS_CONTROLES = 2
    
class Globo:
	
	def __init__(self, x, y, ancho=50, alto=30,modo="normal",direccion="abajo"):
		
		self.radio = 30			#determina tamaño minimo
		
		self.ancho = ancho		#dimensiones de la elipse
		self.alto = alto
		
		self.punto=[5,10]
		self.selec=False		#determina si esta seleccionado
		
		self.direccion=direccion 		#direccion ="abajo","arriba","der","izq"
		
		self.modo=modo	#2 tipos de globos: "normal" o "despacio"
		
		self.x= x*self.ancho/(self.radio*1.0)	#Centro de la elipse
		self.y= y*self.alto/(self.radio*1.0)
		
		ancho_text,alto_text=self.calc_area_texto()
		self.texto = CuadroTexto(self.x,self.y,ancho_text,alto_text)	#es el contenedor del texto
		

	def imprimir(self,context):
		
		#dibujo al globo de dialogo
		
		context.save()
		#context.translate(0.5, 0.5)
		#context.set_line_width(max(context.device_to_user_distance(1, 1)))
		#context.set_line_width(min(2*self.radio/(self.ancho*1.0),2*self.radio/(self.alto*1.0)))
		
		context.set_line_width(2)
		context.scale(self.ancho/(self.radio*1.0),self.alto/(self.radio*1.0))
		
		x=self.x*self.radio/(self.ancho*1.0)
		y=self.y*self.radio/(self.alto*1.0)
		
		if self.direccion=="abajo":
			
			context.arc(x, y, self.radio, 100/(180*1.0) * math.pi,80/(180*1.0)* math.pi)
			context.line_to(x+self.punto[0]*self.radio/(self.ancho*1.0),\
				y+self.radio+self.punto[1]*self.radio/(self.alto*1.0))
				
		elif self.direccion=="der":
			
			context.arc(x, y, self.radio, 10/(180*1.0) * math.pi,350/(180*1.0)* math.pi)
			context.line_to(x+self.radio+self.punto[0]*self.radio/(self.ancho*1.0),\
				y+self.punto[1]*self.radio/(self.alto*1.0))
				
		elif self.direccion=="izq":
			
			context.arc(x, y, self.radio, 190/(180*1.0) * math.pi,530/(180*1.0)* math.pi)
			context.line_to(x-self.radio-self.punto[0]*self.radio/(self.ancho*1.0),\
				y+self.punto[1]*self.radio/(self.alto*1.0))
		
		else: #arriba
			
			context.arc(x, y, self.radio,280/(180*1.0) * math.pi,620/(180*1.0)* math.pi)
			context.line_to(x+self.punto[0]*self.radio/(self.ancho*1.0),\
				y-self.radio-self.punto[1]*self.radio/(self.alto*1.0))


		context.close_path()
		context.set_source_rgb(1, 1, 1)
		context.fill_preserve()
		context.set_source_rgb(0, 0, 0)
		if self.modo<>"normal":
			context.set_dash([2])
		context.stroke()
		context.restore()
		
		# se dibuja el correspondiente texto
		self.texto.imprimir(context)
		self.dibujar_controles(context)

	def dibujar_controles(self,context):

		# si esta seleccionado se dibujan los controles
		if self.selec:
			context.set_line_width(ANCHO_LINEAS_CONTROLES)

			x=self.x*self.radio/(self.ancho*1.0)
			y=self.y*self.radio/(self.alto*1.0)

			# rectangulo alrededor del globo
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho,self.y-self.alto,2*self.ancho,2*self.alto)
			context.stroke()
			
			ancho_marcador = 15

			# cuadrado esquina superior izq
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho-(ancho_marcador/2),self.y-self.alto-(ancho_marcador/2),ancho_marcador,ancho_marcador)
			context.stroke()

			# circulo en la punta del globo
			context.set_source_rgb(1, 1, 1)
			
			if self.direccion=="abajo":
				context.arc(self.x+self.punto[0],self.y+self.alto+self.punto[1],(ancho_marcador/2), 0,x*math.pi)
					
			elif self.direccion=="der":
				context.arc(self.x+self.ancho+self.punto[0],self.y+self.punto[1],(ancho_marcador/2), 0,x*math.pi)
					
			elif self.direccion=="izq":
				context.arc(self.x-self.ancho-self.punto[0],self.y+self.punto[1],(ancho_marcador/2), 0,x*math.pi)
			
			else: #arriba
				context.arc(self.x+self.punto[0],self.y-self.alto-self.punto[1],(ancho_marcador/2), 0,x*math.pi)
					
			context.stroke()


	def set_texto(self,key,keyval,context,rect):
		self.texto.insertar_texto(key,keyval,context)
		self.calc_area(self.texto.ancho,self.texto.alto)
		if self.y-self.alto<=0 or self.y+self.alto>=rect.height:
			#si se redimensiono significa que crecio en un renglon 
			#y verifica si entra en cuadro si no es asi deshace la accion
			self.texto.deshacer(context)
			self.calc_area(self.texto.ancho,self.texto.alto)
			
	def mover_a(self,x,y,rect):
		if self.dx+x>(self.ancho):
			if self.dx+x<(rect.width-self.ancho): self.x=self.dx+x
			else: self.x=rect.width-self.ancho
		else: self.x=self.ancho
			
		if self.dy+y>(self.alto):
			if self.dy+y<(rect.height-self.alto): self.y=self.dy+y
			else: self.y=rect.height-self.alto
		else: self.y=self.alto
		
		self.texto.mover_a(self.x,self.y)
			
			

	def is_selec(self,x,y):
		#devuelve True si es seleccionado
		if (self.x-self.ancho)<x<(self.x+self.ancho) and (self.y-self.alto)<y<(self.y+self.alto):
			
			self.selec=True
			self.texto.mostrar_cursor=True
			
			self.dx=self.x-x	#Obtiene la posicion donde se selecciono con el mouse
			self.dy=self.y-y	#
			return True
		else:
			#self.selec=False
			return False
			
	def no_selec(self):
		self.selec=False
		self.texto.mostrar_cursor=False
		
	def is_selec_tam(self,x,y):
		if self.x-self.ancho-5 < x < self.x-self.ancho+5 and \
			self.y-self.alto-5 < y < self.y-self.alto+5:
			return True
		else: return False

	def is_selec_punto(self,x,y):
		if self.direccion=="abajo":
			if self.x+self.punto[0]-5 < x < self.x+self.punto[0]+5 and \
				self.y+self.alto+self.punto[1]-5 < y < self.y+self.alto+self.punto[1]+5:
				return True
			else: return False
		
		elif self.direccion=="der":
			if self.x+self.ancho+self.punto[0]-5 < x < self.x+self.ancho+self.punto[0]+5 and \
				self.y+self.punto[1]-5 < y < self.y+self.punto[1]+5:
				return True
			else: return False
		
		elif self.direccion=="izq":
			if self.x-self.ancho-self.punto[0]-5 < x < self.x-self.ancho-self.punto[0]+5 and \
				self.y+self.punto[1]-5 < y < self.y+self.punto[1]+5:
				return True
			else: return False
				
		else:
			if self.x+self.punto[0]-5 < x < self.x+self.punto[0]+5 and \
				self.y-self.alto-self.punto[1]-5 < y < self.y-self.alto-self.punto[1]+5:
				return True
			else: return False

	def mover_punto(self,x,y,rect):
		
		if self.direccion=="abajo":
			if 0<x<rect.width: self.punto[0]=x-self.x
			elif x<=0: self.punto[0]=-self.x
			else: self.punto[0]=rect.width-self.x

			if self.y+self.alto<y<rect.height: self.punto[1]=y-(self.y+self.alto)
			elif self.y+self.alto>=y: self.punto[1]=0
			else: self.punto[1]=rect.height-(self.y+self.alto)
				
				
		elif self.direccion=="der":
			if self.x+self.ancho<x<rect.width: self.punto[0]=x-(self.x+self.ancho)
			elif self.x+self.ancho>=x: self.punto[0]=0
			else: self.punto[0]=rect.width-(self.x+self.ancho)

			if 0<y<rect.height: self.punto[1]=y-self.y
			elif self.y+self.alto>=y: self.punto[1]=-self.y
			else: self.punto[1]=rect.height-self.y
				
		elif self.direccion=="izq":
			if 0<x<self.x-self.ancho: self.punto[0]=(self.x-self.ancho)-x
			elif self.x-self.ancho<=x: self.punto[0]=0
			else: self.punto[0]=self.x-self.ancho

			if 0<y<rect.height: self.punto[1]=y-self.y
			elif self.y+self.alto>=y: self.punto[1]=-self.y
			else: self.punto[1]=rect.height-self.y
				
		else :
			if 0<x<rect.width: self.punto[0]=x-self.x
			elif x<=0: self.punto[0]=-self.x
			else: self.punto[0]=rect.width-self.x

			if 0<y<self.y-self.alto: self.punto[1]=(self.y-self.alto)-y
			elif self.y-self.alto<=y: self.punto[1]=0
			else: self.punto[1]=(self.y-self.alto)
	

	def set_dimension(self,x,y,rect,context):
		alto_ant=self.alto
		ancho_ant=self.ancho
		if (2*self.x-x)<rect.width:
			
			if 0<x<(self.x-self.radio): self.ancho=self.x-x
			elif x<=0: self.ancho=self.x
			else: self.ancho=self.radio
		
		elif self.x-self.ancho <> 0: self.ancho=rect.width-self.x

		if (2*self.y-y)<rect.height:
			if 0<y<(self.y-self.radio): self.alto=self.y-y
			elif y<=0: self.alto=self.y
			else: self.alto=self.radio
		elif self.y-self.alto <> 0: self.alto=rect.height-self.y
	
		ancho_text,alto_text=self.calc_area_texto()
		
		self.texto.set_dimension(ancho_text,alto_text)
		self.texto.redimensionar(context)
		self.calc_area(self.texto.ancho,self.texto.alto)
		
		#aca se tiene que ver si entra el texto en la pantalla si no es asi deshace la accion
		
		if self.alto+self.y>rect.height or self.y-self.alto<0 :
			self.alto=alto_ant
			self.ancho=ancho_ant
			ancho_text,alto_text=self.calc_area_texto()
			self.texto.set_dimension(ancho_text,alto_text)
			self.texto.redimensionar(context)
		
	def calc_area_texto(self):
		ancho_text=self.ancho-12*self.ancho/(self.radio*1.0)
		alto_text=self.alto-12*self.alto/(self.radio*1.0)
		return (ancho_text, alto_text)
		
	def calc_area(self,ancho_text,alto_text):
		self.ancho=self.texto.ancho/(1-12/(self.radio*1.0))
		self.alto=self.texto.alto/(1-12/(self.radio*1.0))


		
class Rectangulo(Globo):
	
	def __init__(self, x, y, ancho=50, alto=15):
		
		self.radio = 15		#determina tamaño minimo
		
		self.ancho = ancho		#dimensiones del rectangulo
		self.alto = alto
		
		#self.punto=[5,10]
		self.selec=False		#determina si esta seleccionado
		
		self.x= x*self.ancho/(self.radio*1.0)	#Centro del rectangulo
		self.y= y*self.alto/(self.radio*1.0)
		
		ancho_text,alto_text=self.calc_area_texto()
		self.texto = CuadroTexto(self.x,self.y,ancho_text,alto_text)	#es el contenedor del texto
		

	def imprimir(self,context):
		#imprimimos el rectangulo
		context.set_line_width(3)
		context.rectangle(self.x-self.ancho,self.y-self.alto,2*self.ancho,2*self.alto)
		context.set_source_rgb(129*1.0/255,192*1.0/255, 1)
		context.fill_preserve()
		context.set_source_rgb(0, 0, 0)
		context.stroke()
		
		
		# se dibuja el correspondiente texto
		self.texto.imprimir(context)
		self.dibujar_controles(context)		

	def dibujar_controles(self,context):
		# Si esta seleccionado pintamos un recuadro alrededor del globo
		# y un par de controles
		if self.selec:
			context.set_line_width(ANCHO_LINEAS_CONTROLES)
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho-2,self.y-self.alto-2,2*self.ancho+4,2*self.alto+4)
			context.stroke()
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho-5,self.y-self.alto-5,10,10)
			context.stroke()

	def mover_punto(self,x,y,rect):
		pass
		
	def is_selec_punto(self,x,y):
		return False
	
	def calc_area_texto(self):
		ancho_text=self.ancho-5
		alto_text=self.alto-5
		return (ancho_text, alto_text)
		
	def calc_area(self,ancho_text,alto_text):
		self.ancho=self.texto.ancho+5
		self.alto=self.texto.alto+5


class Nube(Globo):

	def __init__(self, x, y, ancho=50, alto=30,direccion="abajo"):
		
		self.radio = 30
		
		self.ancho = ancho		#dimensiones de la elipse
		self.alto = alto
		
		self.punto=[5,10]
		self.selec=False		#determina si esta seleccionado
		
		self.direccion=direccion
		
		self.x= x#*self.ancho/(self.radio*1.0)	#Centro de la elipse
		self.y= y#*self.alto/(self.radio*1.0)
		
		appdir = os.path.join(activity.get_bundle_path())
		
		self.pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(appdir,'old/nube.png'))
	
		#determina tamaño minimo
		#self.ancho=self.pixbuf.get_width()/2
		#self.alto = self.pixbuf.get_height()/2
		ancho_text,alto_text=self.calc_area_texto()
		self.texto=CuadroTexto(self.x,self.y,ancho_text,alto_text)	#es el contenedor del texto
		

	def imprimir(self,context):
		
		#context.paint()     

		context.save()
		
		context.scale(self.ancho/(self.pixbuf.get_width()*0.5),self.alto/(self.pixbuf.get_height()*0.5))

		x=self.x*self.pixbuf.get_width()/(self.ancho*2.0)
		y=self.y*self.pixbuf.get_height()/(self.alto*2.0)
		context.set_source_pixbuf(self.pixbuf,x-self.pixbuf.get_width()/2, y-self.pixbuf.get_height()/2)
		context.paint()     
		
		
		context.restore()
		
		#dibuja punto
		context.set_line_width(5*self.ancho/(self.pixbuf.get_width()*0.5))
		
		
		if self.direccion=="abajo":
			context.arc(self.x+self.punto[0]/2,self.y+self.alto+self.punto[1]/2,7, 0,2*math.pi)
			context.set_source_rgb(1, 1, 1)
			context.fill_preserve()
			context.set_source_rgb(0, 0, 0)
			context.stroke()
			context.arc(self.x+self.punto[0],self.y+self.alto+self.punto[1],5, 0,2*math.pi)
	
		elif self.direccion=="der":
			context.arc(self.x+self.ancho+self.punto[0]/2,self.y+self.punto[1]/2,7, 0,2*math.pi)
			context.set_source_rgb(1, 1, 1)
			context.fill_preserve()
			context.set_source_rgb(0, 0, 0)
			context.stroke()
			context.arc(self.x+self.ancho+self.punto[0],self.y+self.punto[1],5, 0,2*math.pi)
					
		elif self.direccion=="izq":
			context.arc(self.x-self.ancho-self.punto[0]/2,self.y+self.punto[1]/2,7, 0,2*math.pi)
			context.set_source_rgb(1, 1, 1)
			context.fill_preserve()
			context.set_source_rgb(0, 0, 0)
			context.stroke()
			context.arc(self.x-self.ancho-self.punto[0],self.y+self.punto[1],5, 0,2*math.pi)
			
		else: #arriba
			context.arc(self.x+self.punto[0]/2,self.y-self.alto-self.punto[1]/2,7, 0,2*math.pi)
			context.set_source_rgb(1, 1, 1)
			context.fill_preserve()
			context.set_source_rgb(0, 0, 0)
			context.stroke()
			context.arc(self.x+self.punto[0],self.y-self.alto-self.punto[1],5, 0,2*math.pi)
		
		context.set_source_rgb(1, 1, 1)
		context.fill_preserve()
		context.set_source_rgb(0, 0, 0)
		context.stroke()
		
		# se dibuja el correspondiente texto
		self.texto.imprimir(context)
		
		self.dibujar_controles(context)		

	def calc_area_texto(self):
		ancho_text=self.ancho-12*self.ancho/(self.radio*1.0)
		alto_text=self.alto-12*self.alto/(self.radio*1.0)
		return (ancho_text, alto_text)
		
	def calc_area(self,ancho_text,alto_text):
		self.ancho=self.texto.ancho/(1-12/(self.radio*1.0))
		self.alto=self.texto.alto/(1-12/(self.radio*1.0))

class Grito(Globo):

	def __init__(self, x, y, ancho=50, alto=30,direccion="abajo"):
		
		self.radio = 30
		
		self.ancho = ancho		#dimensiones de la elipse
		self.alto = alto
		
		self.punto=[5,50]
		self.selec=False		#determina si esta seleccionado
		
		self.direccion=direccion
		
		self.x= x#*self.ancho/(self.radio*1.0)	#Centro de la elipse
		self.y= y#*self.alto/(self.radio*1.0)
		
		appdir = os.path.join(activity.get_bundle_path())
		self.pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(appdir,'old/grito2.png'))

		ancho_text,alto_text=self.calc_area_texto()
		self.texto=CuadroTexto(self.x,self.y,ancho_text,alto_text)	#es el contenedor del texto
		

	def imprimir(self,context):
		
		#context.paint()     

		context.save()
		
		sx=self.pixbuf.get_width()/(self.ancho*2.0)
		sy=self.pixbuf.get_height()/(self.alto*2.0)
		
		context.scale(1/sx,1/sy)
		
		x=self.x*sx
		y=self.y*sy

	
		context.set_source_pixbuf(self.pixbuf,x-self.pixbuf.get_width()/2, y-self.pixbuf.get_height()/2)
		
		context.paint()    
		
		context.set_line_width(5)
		context.move_to(x ,y+self.alto*sy-21)
		context.rel_line_to(self.punto[0]*sx,self.punto[1]*sy+21)
		context.rel_line_to(30-self.punto[0]*sx, -self.punto[1]*sy-21)
		#context.close_path()
		context.set_source_rgb(1, 1, 1)
		context.fill_preserve()
		context.set_source_rgb(0, 0, 0)
		context.stroke()
		context.restore()
		
		# se dibuja el correspondiente texto
		self.texto.imprimir(context)

		self.dibujar_controles(context)		
	
	def calc_area_texto(self):
		ancho_text=self.ancho-12*self.ancho/(self.radio*1.0)
		alto_text=self.alto-12*self.alto/(self.radio*1.0)
		return (ancho_text, alto_text)
		
	def calc_area(self,ancho_text,alto_text):
		self.ancho=self.texto.ancho/(1-12/(self.radio*1.0))
		self.alto=self.texto.alto/(1-12/(self.radio*1.0))

class Imagen(Globo):

	def __init__(self, x, y, ancho=50, alto=30):
		
		self.radio = 30
		
		self.ancho = ancho		#dimensiones de la elipse
		self.alto = alto
		
		self.selec=False		#determina si esta seleccionado
		
		self.x= x#*self.ancho/(self.radio*1.0)	#Centro de la elipse
		self.y= y#*self.alto/(self.radio*1.0)
		
		appdir = os.path.join(activity.get_bundle_path())
		self.pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(appdir,'mascota2.png'))
		
		self.texto=CuadroTexto(self.x,self.y,20,20)	#es el contenedor del texto
			

	def imprimir(self,context):
		
		#context.paint()     

		context.save()
		
		context.scale(self.ancho/(self.pixbuf.get_width()*0.5),self.alto/(self.pixbuf.get_height()*0.5))

		x=self.x*self.pixbuf.get_width()/(self.ancho*2.0)
		y=self.y*self.pixbuf.get_height()/(self.alto*2.0)
				
		
		context.set_source_pixbuf(self.pixbuf,x-self.pixbuf.get_width()/2, y-self.pixbuf.get_height()/2)
		context.paint()    


		context.restore()
		
		
		# si esta seleccionado se dibujan los controles
		if self.selec:
			context.set_line_width(ANCHO_LINEAS_CONTROLES)
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho,self.y-self.alto,2*self.ancho,2*self.alto)
			context.stroke()
			context.set_source_rgb(1, 1, 1)
			context.rectangle(self.x-self.ancho-5,self.y-self.alto-5,10,10)
			context.stroke()
			

	def calc_area_texto(self):
		return (20, 20)
	def calc_area(self,ancho_text,alto_text):
		pass
	def mover_punto(self,x,y,rect):
		pass
	def is_selec_punto(self,x,y):
		return False
	def set_texto(self,key,keyval,context,rect):
		pass

	
class CuadroTexto:

	"Es un cuadro de texto con alineacion centralizada"

	def __init__(self, x, y, ancho=50, alto=30):
		
		self.ancho = ancho		#Ancho del cuadro = 2*self.ancho
		self.alto = alto			#Alto del cuadro = 2*self.alto
		
		self.x= x				#Centro del cuadro
		self.y= y				#Centro del cuadro
		
		self.texto = None		
		self.cursor=0			#Posicion del cursor(en nro de caracteres)
		
		self.font_size=12		#Caracteristicas de la tipografia
		self.font_type="Georgia"
		
		self.alto_renglon=12	#Tamaño del renglon
		
		self.mostrar_borde=False  #Permite dibujar o no recuadro
		
		self.mostrar_cursor=False	#Dibujar o no el cursor
		
		self.renglones=[] 		#texto en cada renglon
		self.esp_reg=[] 		# 1 =el renglon i termino con un espacio 
							# 0= el renglon i no termino con espacio


	def imprimir(self,context):
		context.set_source_rgb(0, 0, 0)
		if self.mostrar_borde:
			#dibuja recuadro
			context.set_line_width(1)
			context.rectangle(self.x-self.ancho,self.y-self.alto,2*self.ancho,2*self.alto)
			context.stroke()
        

		# Insertando el texto
		context.select_font_face(self.font_type, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(self.font_size)
		
		if self.texto:
			cursor_dib=self.cursor	#dibujar cursor
	
			for i in range(len (self.renglones)):
		
				xbearing, ybearing, width, height, xadvance, yadvance =\
				context.text_extents(self.renglones[i].replace(" ","-"))
			
				context.move_to(self.x-width/2-1,self.y-self.alto+(i+1)*self.alto_renglon)
				context.set_source_rgb(0, 0, 0)
				context.show_text(self.renglones[i])
		
				if self.mostrar_cursor: 
					if cursor_dib>=len(self.renglones[i])+self.esp_reg[i]: 
						cursor_dib-=(len(self.renglones[i])+self.esp_reg[i])
					
					elif cursor_dib <> -99:
						xbearing1, ybearing1, width1, height1, xadvance1, yadvance1 =\
							context.text_extents(self.renglones[i][0:cursor_dib].replace(" ","-"))
						context.move_to(self.x-width/2-1+width1,self.y-self.alto+(i+1)*self.alto_renglon)
						context.show_text("_")
						cursor_dib=-99 # para que no lo vuelva a dibujar en otro renglon
		
		elif  self.mostrar_cursor:
			context.move_to(self.x,self.y-self.alto+self.alto_renglon)
			context.set_source_rgb(0, 0, 0)
			context.show_text("_")
		
		context.stroke()

	def insertar_texto(self,key,keyval,context):

		if self.texto:
			
			if keyval == gtk.gdk.keyval_from_name('BackSpace'):
				if self.cursor>=1: 
					self.texto=self.texto[0:self.cursor-1]+self.texto[self.cursor:len(self.texto)]
					self.cursor-=1
				self.redimensionar(context)

			
			elif keyval == gtk.gdk.keyval_from_name('Return'):
				self.texto=self.texto[0:self.cursor]+"\n"+self.texto[self.cursor:len(self.texto)]
				self.cursor+=1
				self.redimensionar(context)
			
			elif keyval == gtk.gdk.keyval_from_name('Right'):
				if self.cursor<len(self.texto): self.cursor+=1
		
			elif keyval == gtk.gdk.keyval_from_name('Left'):
				if self.cursor>0: self.cursor-=1
				
			elif keyval == gtk.gdk.keyval_from_name('Up'):
				sum_ren=0
				for i in range (len(self.renglones)): #se averigua en que renglon esta el cursor
					if sum_ren<=self.cursor<(sum_ren+len(self.renglones[i])+self.esp_reg[i]): 
						if i<>0:
							cur_ren=self.cursor-sum_ren #calculo desplazamiento dentro de un renglon
							self.cursor=min (sum_ren-len(self.renglones[i-1])-self.esp_reg[i-1]+\
							cur_ren,sum_ren-1)
						break
					else: sum_ren+=(len(self.renglones[i])+self.esp_reg[i])
					
			elif keyval == gtk.gdk.keyval_from_name('Down'):
				sum_ren=0
				for i in range (len(self.renglones)): #se averigua en que renglon esta el cursor
					if sum_ren<=self.cursor<(sum_ren+len(self.renglones[i])+self.esp_reg[i]): 
						if i<>len(self.renglones)-1:
							cur_ren=self.cursor-sum_ren #calculo desplazamiento dentro de un renglon
							self.cursor=min (sum_ren+len(self.renglones[i])+self.esp_reg[i]+cur_ren,\
										sum_ren+len(self.renglones[i])+self.esp_reg[i]+\
										len(self.renglones[i+1])+self.esp_reg[i+1]-1)
						break
					else: sum_ren+=(len(self.renglones[i])+self.esp_reg[i])
			
			
			else: 
				self.texto=self.texto[0:self.cursor]+key+self.texto[self.cursor:len(self.texto)]
				if key<>"":
					self.cursor+=1
					self.redimensionar(context)
			
		else: 
			self.texto=key
			self.cursor=1
			self.redimensionar(context)


	def redimensionar(self,context):
		"Establece el texto en cada renglon dependiendo de las dimensiones del cuadro, \
		 manteniendo fijo el ancho, y redimensionando el alto si es necesario"

		if self.texto is not None:

			texto_oracion=self.texto.split("\n")
			
			self.renglones=[] #texto en cada renglon
			self.esp_reg=[] # 1 =indica si el renglon termino con un espacio. 

			for j in range(len(texto_oracion)):
				texto_renglon=texto_oracion[j]
			

				while texto_renglon<>None:
			
					for i in range(len(texto_renglon.split(" "))):
				
						xbearing, ybearing, width, height, xadvance, yadvance =\
						context.text_extents(texto_renglon.rsplit(" ",i)[0].replace(" ","-")) 
						# es remplazado " " por "-" para que pueda calcular el ancho considerando los 
						# espacios (el caracter - tiene el mismo ancho que el espacio)
			
					
						if (width)<= self.ancho*2:
						
							self.renglones.append(texto_renglon.rsplit(" ",i)[0])
							self.esp_reg.append(1)
						
						
							if i<>0:
								texto_renglon=texto_renglon.split(" ",len(texto_renglon.split(" "))-i)\
									[len(texto_renglon.split(" "))-i]

							else: 
								texto_renglon=None
							break
					
						elif  i==(len(texto_renglon.split(" "))-1): 
							#este es el caso que no entra ni una palabra
							
							#tiene problemas de performance:se podria mejorar 
							#empezando desde la izq
							
							palabra=(texto_renglon.rsplit(" ",i)[0])
							if i<>0:
								texto_renglon=" "+texto_renglon.split(" ",len(texto_renglon.split(" "))-i)\
								[len(texto_renglon.split(" "))-i]

							else: texto_renglon=""
						
							for k in range(1,len(palabra)):
								xbearing, ybearing, width, height, xadvance, yadvance =\
								context.text_extents(palabra[:len(palabra)-k])
								if (width)<= self.ancho*2:
									self.renglones.append(palabra[:len(palabra)-k])
									self.esp_reg.append(0)
									texto_renglon=palabra[len(palabra)-k:len(palabra)]+texto_renglon
									break
						

				if len(self.renglones)*self.alto_renglon>self.alto*2:
					self.alto=len(self.renglones)*self.alto_renglon/2
	
	def mover_a(self,x,y):
		"Mueve el centro del cuadro a la posicion (x,y)"
		self.y=y
		self.x=x

	def set_dimension(self,ancho,alto):
		"Establece las dimensiones del cuadro siendo el ancho del cuadro= 2*ancho \
		y el alto del cuadro=2*alto"
		self.ancho=ancho
		self.alto=alto

	def deshacer(self,context):
		"Se utiliza para deshacer la creacion de un nuevo renglon de texto"
		self.texto=self.texto[0:self.cursor-1]+self.texto[self.cursor:len(self.texto)]
		self.cursor-=1
		self.alto-=self.alto_renglon
		self.redimensionar(context)


