# -*- coding: UTF-8 -*-

import os
import math
import gtk
import gobject
import cairo
import pango
import logging

import sugar.env
from sugar.activity import activity
from sugar.graphics.icon import _IconBuffer

ANCHO_LINEAS_CONTROLES = 2

DIR_ABAJO = "abajo"
DIR_ARRIBA = "arriba"
DIR_IZQ = "izq"
DIR_DER = "der"


class Globo:

    def __init__(self, x, y, ancho=50, alto=30, modo="normal",
            direccion=DIR_ABAJO):

        self.globe_type = "GLOBE"
        #determina tamanio minimo
        self.radio = 30
        #dimensiones de la elipse
        self.ancho = ancho
        self.alto = alto
        self.punto = [5, 10]
        #determina si esta seleccionado
        self.selec = False
        self.direccion = direccion
        #2 tipos de globos: "normal" o "despacio"
        self.modo = modo
        #Centro de la elipse
        self.x = x * self.ancho / (self.radio * 1.0)
        self.y = y * self.alto / (self.radio * 1.0)

        ancho_text, alto_text = self.calc_area_texto()
        #es el contenedor del texto
        self.texto = CuadroTexto(self.x, self.y, ancho_text, alto_text)

    def imprimir(self, context):
        #dibujo al globo de dialogo

        context.save()

        context.set_line_width(2)
        context.scale(self.ancho / (self.radio * 1.0),
                self.alto / (self.radio * 1.0))

        x = self.x * self.radio / (self.ancho * 1.0)
        y = self.y * self.radio / (self.alto * 1.0)

        if self.direccion == DIR_ABAJO:

            context.arc(x, y, self.radio, 100 / (180.0) * math.pi,
                        80 / (180.0) * math.pi)
            context.line_to( \
                        x + self.punto[0] * self.radio / (self.ancho * 1.0),
                        y + self.radio + \
                        self.punto[1] * self.radio / (self.alto * 1.0))

        elif self.direccion == DIR_DER:
            context.arc(x, y, self.radio,
                        10 / 180.0 * math.pi, 350 / 180.0 * math.pi)
            context.line_to(x + self.radio +
                            self.punto[0] * self.radio / (self.ancho * 1.0), \
                            y + self.punto[1] * self.radio / (self.alto * 1.0))

        elif self.direccion == DIR_IZQ:
            context.arc(x, y, self.radio, 190 / 180.0 * math.pi,
                        530 / 180.0 * math.pi)
            context.line_to(x - self.radio -
                            self.punto[0] * self.radio / (self.ancho * 1.0), \
                            y + self.punto[1] * self.radio / (self.alto * 1.0))

        else:
            context.arc(x, y, self.radio,
                        280 / 180.0 * math.pi, 620 / 180.0 * math.pi)
            context.line_to( \
                        x + self.punto[0] * self.radio / (self.ancho * 1.0),\
                        y - self.radio -
                        self.punto[1] * self.radio / (self.alto * 1.0))

        context.close_path()
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        if self.modo != "normal":
            context.set_dash([2])
        context.stroke()
        context.restore()

        # se dibuja el correspondiente texto
        self.texto.imprimir(context)
        self.dibujar_controles(context)

    def dibujar_controles(self, context):

        # si esta seleccionado se dibujan los controles
        if self.selec:
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)

            x = self.x * self.radio / (self.ancho * 1.0)
            y = self.y * self.radio / (self.alto * 1.0)

            # rectangulo alrededor del globo
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho, self.y - self.alto,
                    2 * self.ancho, 2 * self.alto)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()

            ancho_marcador = 15
            context.restore()

            # cuadrado esquina superior izq
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho - (ancho_marcador / 2),
                    self.y - self.alto - (ancho_marcador / 2),
                    ancho_marcador, ancho_marcador)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

            # circulo en la punta del globo
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)

            x_circle, y_circle = self.get_circle_position()
            context.arc(x_circle, y_circle,
                        (ancho_marcador / 2), 0, x * math.pi)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

    def get_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0], self.y + self.alto + self.punto[1]
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0], self.y + self.punto[1]
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0], self.y + self.punto[1]
        else:
            return self.x + self.punto[0], self.y - self.alto - self.punto[1]

    # TODO: add a function to obtain to position (x, y)
    # where is the control circle

    def set_texto(self, key, keyval, context, rect):
        self.texto.insertar_texto(key, keyval, context)
        self.calc_area(self.texto.ancho, self.texto.alto)
        if self.y - self.alto <= 0  or self.y + self.alto >= rect.height:
            #si se redimensiono significa que crecio en un renglon
            #y verifica si entra en cuadro si no es asi deshace la accion
            self.texto.deshacer(context)
            self.calc_area(self.texto.ancho, self.texto.alto)

    def mover_a(self, x, y, rect):
        if self.dx + x > (self.ancho):
            if self.dx + x < (rect.width - self.ancho):
                self.x = self.dx + x
            else:
                self.x = rect.width - self.ancho
        else:
            self.x = self.ancho

        if self.dy + y > (self.alto):
            if self.dy + y < (rect.height - self.alto):
                self.y = self.dy + y
            else:
                self.y = rect.height - self.alto
        else:
            self.y = self.alto

        self.texto.mover_a(self.x, self.y)

    def get_over_state(self, x, y):
        """
        if (self.x - self.ancho) < x < (self.x + self.ancho) and \
                (self.y - self.alto) < y < (self.y + self.alto):
            return None
        """
        state = None
        sensibility = 2
        if abs((self.x - self.ancho) - x) < sensibility:
            state = 'LEFT_SIDE'
            if abs((self.y - self.alto) - y) < sensibility:
                state = 'TOP_LEFT_CORNER'
            if abs((self.y + self.alto) - y) < sensibility:
                state = 'BOTTOM_LEFT_CORNER'
        elif abs((self.x + self.ancho) - x) < sensibility:
            state = 'RIGHT_SIDE'
            if abs((self.y - self.alto) - y) < sensibility:
                state = 'TOP_RIGHT_CORNER'
            if abs((self.y + self.alto) - y) < sensibility:
                state = 'BOTTOM_RIGHT_CORNER'
        elif abs((self.y - self.alto) - y) < sensibility:
            state = 'TOP_SIDE'
        elif abs((self.y + self.alto) - y) < sensibility:
            state = 'BOTTOM_SIDE'
        return state

    def is_selec(self, x, y):
        #devuelve True si es seleccionado
        if (self.x - self.ancho) < x < (self.x + self.ancho) and \
                (self.y - self.alto) < y < (self.y + self.alto):

            self.selec = True
            self.texto.mostrar_cursor = True

            #Obtiene la posicion donde se selecciono con el mouse
            self.dx = self.x - x
            self.dy = self.y - y
            return True
        else:
            #self.selec=False
            return False

    def no_selec(self):
        self.selec = False
        self.texto.mostrar_cursor = False

    def is_selec_tam(self, x, y):
        if self.x - self.ancho - 5 < x < self.x - self.ancho + 5 and \
            self.y - self.alto - 5 < y < self.y - self.alto + 5:
            return True
        else:
            return False

    def is_selec_punto(self, x, y):
        x_circle, y_circle = self.get_circle_position()
        return x_circle - 5 < x < x_circle + 5 and \
                y_circle - 5 < y < y_circle + 5

    def mover_punto(self, x, y, rect):
        if self.direccion == DIR_ABAJO:
            if 0 < x < rect.width:
                self.punto[0] = x - self.x
            elif x <= 0:
                self.punto[0] = - self.x
            else:
                self.punto[0] = rect.width - self.x

            if self.y + self.alto < y < rect.height:
                self.punto[1] = y - (self.y + self.alto)
            elif self.y + self.alto >= y:
                self.punto[1] = 0
            else:
                self.punto[1] = rect.height - (self.y + self.alto)

        elif self.direccion == DIR_DER:
            if self.x + self.ancho < x < rect.width:
                self.punto[0] = x - (self.x + self.ancho)
            elif self.x + self.ancho >= x:
                self.punto[0] = 0
            else:
                self.punto[0] = rect.width - (self.x + self.ancho)

            if 0 < y < rect.height:
                self.punto[1] = y - self.y
            elif self.y + self.alto >= y:
                self.punto[1] = - self.y
            else:
                self.punto[1] = rect.height - self.y

        elif self.direccion == DIR_IZQ:
            if 0 < x < self.x - self.ancho:
                self.punto[0] = (self.x - self.ancho) - x
            elif self.x - self.ancho <= x:
                self.punto[0] = 0
            else:
                self.punto[0] = self.x - self.ancho

            if 0 < y < rect.height:
                self.punto[1] = y - self.y
            elif self.y + self.alto >= y:
                self.punto[1] = - self.y
            else:
                self.punto[1] = rect.height - self.y

        else:
            if 0 < x < rect.width:
                self.punto[0] = x - self.x
            elif x <= 0:
                self.punto[0] = - self.x
            else:
                self.punto[0] = rect.width - self.x

            if 0 < y < self.y - self.alto:
                self.punto[1] = (self.y - self.alto) - y
            elif self.y - self.alto <= y:
                self.punto[1] = 0
            else:
                self.punto[1] = (self.y - self.alto)

    def set_dimension(self, x, y, rect, context):
        alto_ant = self.alto
        ancho_ant = self.ancho

        # if I am changing the size from the right or from the bottom
        # change x / y to calculate like if changing from
        # top and left
        if x > self.x:
            x = 2 * self.x - x
        if y > self.y:
            y = 2 * self.y - y

        if (2 * self.x - x) < rect.width:
            if 0 < x < (self.x - self.radio):
                self.ancho = self.x - x
            elif x <= 0:
                self.ancho = self.x
            else:
                self.ancho = self.radio

        elif self.x - self.ancho != 0:
            self.ancho = rect.width - self.x

        if (2 * self.y - y) < rect.height:
            if 0 < y < (self.y - self.radio):
                self.alto = self.y - y
            elif y <= 0:
                self.alto = self.y
            else:
                self.alto = self.radio
        elif self.y - self.alto != 0:
            self.alto = rect.height - self.y

        ancho_text, alto_text = self.calc_area_texto()

        self.texto.set_dimension(ancho_text, alto_text)
        self.texto.redimensionar(context)
        self.calc_area(self.texto.ancho, self.texto.alto)

        # aca se tiene que ver si entra el texto en la pantalla
        # si no es asi deshace la accion

        if self.alto + self.y > rect.height or self.y - self.alto < 0:
            self.alto = alto_ant
            self.ancho = ancho_ant
            ancho_text, alto_text = self.calc_area_texto()
            self.texto.set_dimension(ancho_text, alto_text)
            self.texto.redimensionar(context)

    def calc_area_texto(self):
        ancho_text = self.ancho - 12 * self.ancho / (self.radio * 1.0)
        alto_text = self.alto - 12 * self.alto / (self.radio * 1.0)
        return (ancho_text, alto_text)

    def calc_area(self, ancho_text, alto_text):
        self.ancho = self.texto.ancho / (1 - 12 / (self.radio * 1.0))
        self.alto = self.texto.alto / (1 - 12 / (self.radio * 1.0))

    def girar(self):
        if (self.__class__ == Rectangulo):
            return False

        if (self.direccion == DIR_ABAJO):
            self.direccion = DIR_IZQ

        elif (self.direccion == DIR_IZQ):
            self.direccion = DIR_ARRIBA

        elif (self.direccion == DIR_ARRIBA):
            self.direccion = DIR_DER

        elif (self.direccion == DIR_DER):
            self.direccion = DIR_ABAJO
        self.punto[0] = self.punto[1]
        self.punto[1] = self.punto[0]

        if (self.__class__ == Imagen):
            self.ancho, self.alto = self.alto, self.ancho

        return True


class Rectangulo(Globo):

    def __init__(self, x, y, ancho=50, alto=15):

        self.globe_type = "RECTANGLE"
        #determina tamanio minimo
        self.radio = 15
        #dimensiones del rectangulo
        self.ancho = ancho
        self.alto = alto
        self.punto = None
        self.direccion = None
        self.selec = False

        #Centro del rectangulo
        self.x = x
        self.y = y

        ancho_text, alto_text = self.calc_area_texto()
        self.texto = CuadroTexto(self.x, self.y, ancho_text, alto_text)

    def imprimir(self, context):
        #imprimimos el rectangulo
        context.set_line_width(3)
        context.rectangle(self.x - self.ancho, self.y - self.alto,
                2 * self.ancho, 2 * self.alto)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        # se dibuja el correspondiente texto
        self.texto.imprimir(context)
        self.dibujar_controles(context)

    def dibujar_controles(self, context):
        # Si esta seleccionado pintamos un recuadro alrededor del globo
        # y un par de controles
        if self.selec:
            context.save()
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho - 2, self.y - self.alto - 2,
                    2 * self.ancho + 4, 2 * self.alto + 4)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()

            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho - 5,
                    self.y - self.alto - 5, 10, 10)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()
            context.restore()

    def mover_punto(self, x, y, rect):
        pass

    def is_selec_punto(self, x, y):
        return False

    def calc_area_texto(self):
        ancho_text = self.ancho - 5
        alto_text = self.alto - 5
        return (ancho_text, alto_text)

    def calc_area(self, ancho_text, alto_text):
        self.ancho = self.texto.ancho + 5
        self.alto = self.texto.alto + 5


class Nube(Globo):

    def __init__(self, x, y, ancho=50, alto=30, direccion=DIR_ABAJO):

        self.globe_type = "CLOUD"
        self.radio = 30

        #dimensiones de la elipse
        self.ancho = ancho
        self.alto = alto

        self.punto = [5, 10]
        #determina si esta seleccionado
        self.selec = False

        self.direccion = direccion

        self.x = x
        self.y = y

        appdir = os.path.join(activity.get_bundle_path())

        ancho_text, alto_text = self.calc_area_texto()
        self.texto = CuadroTexto(self.x, self.y, ancho_text, alto_text)

    def imprimir(self, context):

        self.draw(context)

        x_circle, y_circle = self.get_second_circle_position()

        context.arc(x_circle, y_circle, 7, 0, 2 * math.pi)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        x_circle, y_circle = self.get_circle_position()
        context.arc(x_circle, y_circle, 5, 0, 2 * math.pi)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(0, 0, 0)
        context.stroke()

        # se dibuja el correspondiente texto
        self.texto.imprimir(context)

        self.dibujar_controles(context)

    def draw(self, cr):

        x_cen = self.x
        y_cen = self.y

        points = []
        steps = 36

        ancho_int = self.ancho * 0.8
        alto_int = self.alto * 0.8

        x = x_cen + self.ancho
        y = y_cen
        cr.move_to(x, y)

        state = 0

        for i in range(steps):
            alpha = 2.0 * i * (math.pi / steps)
            #print "i", i, "alpha", alpha, "state", state
            sinalpha = math.sin(alpha)
            cosalpha = math.cos(alpha)

            if state == 0:
                x1 = x_cen + (1.0 * self.ancho * cosalpha)
                y1 = y_cen + (1.0 * self.alto * sinalpha)
            elif state == 1:
                x2 = x_cen + (1.0 * self.ancho * cosalpha)
                y2 = y_cen + (1.0 * self.alto * sinalpha)
            elif state == 2:
                x3 = x_cen + (1.0 * ancho_int * cosalpha)
                y3 = y_cen + (1.0 * alto_int * sinalpha)

            draw_line = False

            if state == 2:
                cr.curve_to(x1, y1, x2, y2, x3, y3)

            state += 1
            if state == 3:
                state = 0

        x1 = x_cen + (1.0 * self.ancho * cosalpha)
        y1 = y_cen + (1.0 * self.alto * sinalpha)
        x2 = x_cen + (1.0 * self.ancho)
        y2 = y_cen
        x3 = x_cen + (1.0 * self.ancho)
        y3 = y_cen
        cr.curve_to(x1, y1, x2, y2, x3, y3)

        cr.set_source_rgb(1, 1, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0, 0, 0, 1)
        cr.set_line_width(4)
        cr.stroke()

    def get_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0], self.y + self.alto + self.punto[1]
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0], self.y + self.punto[1]
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0], self.y + self.punto[1]
        else:
            return self.x + self.punto[0], self.y - self.alto - self.punto[1]

    def get_second_circle_position(self):
        if self.direccion == DIR_ABAJO:
            return self.x + self.punto[0] / 2, \
                    self.y + self.alto + self.punto[1] / 2
        elif self.direccion == DIR_DER:
            return self.x + self.ancho + self.punto[0] / 2, \
                    self.y + self.punto[1] / 2
        elif self.direccion == DIR_IZQ:
            return self.x - self.ancho - self.punto[0] / 2, \
                    self.y + self.punto[1] / 2
        else:
            return self.x + self.punto[0] / 2, \
                    self.y - self.alto - self.punto[1] / 2


class Grito(Globo):

    def __init__(self, x, y, ancho=50, alto=30, direccion=DIR_ABAJO):

        self.globe_type = "EXCLAMATION"
        self.radio = 30

        self.ancho = ancho
        self.alto = alto

        self.punto = [5, 50]
        self.selec = False

        self.direccion = direccion

        self.x = x
        self.y = y

        ancho_text, alto_text = self.calc_area_texto()
        self.texto = CuadroTexto(self.x, self.y, ancho_text, alto_text)

    def imprimir(self, context):
        context.save()
        self.draw_exclamation(context, self.x, self.y,
                self.ancho, self.alto, self.direccion, self.punto)
        # se dibuja el correspondiente texto
        self.texto.imprimir(context)
        self.dibujar_controles(context)

    def draw_exclamation(self, cr, x_cen, y_cen,
        width, height, direction, punto):

        print "x_cen", x_cen, "y_cen", y_cen, "width", width, "height", height

        points = []
        steps = 24

        width_int = width * 0.8
        height_int = height * 0.8

        x = x_cen + width
        y = y_cen
        cr.move_to(x, y)

        for i in range(steps):
            alpha = 2.0 * i * (math.pi / steps)
            #print "i", i, "alpha", alpha
            sinalpha = math.sin(alpha)
            cosalpha = math.cos(alpha)

            if i % 2 > 0:
                x = x_cen + (1.0 * width_int * cosalpha)
                y = y_cen + (1.0 * height_int * sinalpha)
            else:
                x = x_cen + (1.0 * width * cosalpha)
                y = y_cen + (1.0 * height * sinalpha)

            if (direction == DIR_ABAJO and i == 6) or \
               (direction == DIR_DER and i == 0) or \
               (direction == DIR_IZQ and i == 12) or \
               (direction == DIR_ARRIBA and i == 18):

                if direction == DIR_ABAJO:
                    x = x_cen + punto[0]
                    y = y_cen + height + punto[1]
                elif direction == DIR_DER:
                    x = x_cen + width + punto[0]
                    y = y_cen + punto[1]
                elif direction == DIR_IZQ:
                    x = x_cen - width - punto[0]
                    y = y_cen + punto[1]
                else:
                    x = x_cen + punto[0]
                    y = y_cen - height - punto[1]

            cr.line_to(x, y)
        cr.close_path()
        cr.set_source_rgb(1, 1, 1)
        cr.fill_preserve()
        cr.set_source_rgba(0, 0, 0, 1)
        cr.set_line_width(4)
        cr.stroke()

    def calc_area_texto(self):
        ancho_text = self.ancho - 12 * self.ancho / (self.radio * 1.0)
        alto_text = self.alto - 20 * self.alto / (self.radio * 1.0)
        return (ancho_text, alto_text)


class Imagen(Globo):

    def __init__(self, imagen, x, y, ancho=50, alto=30, direccion=DIR_ABAJO):

        self.globe_type = "IMAGE"
        self.radio = 30
        self.ancho = ancho
        self.alto = alto
        self.image_name = imagen

        self.selec = False

        self.x = x
        self.y = y
        self.direccion = direccion
        self.punto = [0, 0]  # fake, but needed for persistence

        appdir = os.path.join(activity.get_bundle_path())
        self.icon_buffer = _IconBuffer()
        self.icon_buffer.file_name = os.path.join(appdir, imagen)
        self.icon_buffer.stroke_color = '#000000'
        self.texto = CuadroTexto(self.x, self.y, 20, 20)

    def imprimir(self, context):

        context.save()

        if self.direccion in (DIR_ARRIBA, DIR_ABAJO):
            self.icon_buffer.width = self.ancho * 2
            self.icon_buffer.height = self.alto * 2
        else:
            self.icon_buffer.width = self.alto * 2
            self.icon_buffer.height = self.ancho * 2

        surface = self.icon_buffer.get_surface()
        x = self.x - surface.get_width() / 2
        y = self.y - surface.get_height() / 2

        context.translate(x, y)

        if self.direccion != DIR_ABAJO:
            if self.direccion == DIR_ARRIBA:
                context.rotate(3.14)  # 180 degrees
                context.translate(-self.icon_buffer.width,
                        -self.icon_buffer.height)

            elif self.direccion == DIR_IZQ:
                context.rotate(3.14 / 2.0)  # 90 degrees
                context.translate(
                    (self.icon_buffer.height - self.icon_buffer.width) / 2,
                    -(self.icon_buffer.width + self.icon_buffer.height) / 2)

            elif self.direccion == DIR_DER:
                context.rotate(3.0 * 3.14 / 2.0)  # 270 degrees
                context.translate(
                    -(self.icon_buffer.height + self.icon_buffer.width) / 2,
                    (self.icon_buffer.width - self.icon_buffer.height) / 2)

        context.set_source_surface(surface, 0, 0)

        context.paint()
        context.restore()

        # si esta seleccionado se dibujan los controles
        if self.selec:
            context.set_line_width(ANCHO_LINEAS_CONTROLES)
            context.set_source_rgb(1, 1, 1)
            context.rectangle(self.x - self.ancho, self.y - self.alto,
                    2 * self.ancho, 2 * self.alto)
            context.stroke_preserve()
            context.set_source_rgb(0, 0, 0)
            context.set_dash([2])
            context.stroke()

    def calc_area_texto(self):
        return (20, 20)

    def calc_area(self, ancho_text, alto_text):
        pass

    def mover_punto(self, x, y, rect):
        pass

    def is_selec_punto(self, x, y):
        return False

    def set_texto(self, key, keyval, context, rect):
        pass


class CuadroTexto:

    "Es un cuadro de texto con alineacion centralizada"

    def __init__(self, x, y, ancho=50, alto=30):

        #Ancho del cuadro = 2*self.ancho
        self.ancho = ancho
        #Alto del cuadro = 2*self.alto
        self.alto = alto

        #Centro del cuadro
        self.x = x
        self.y = y

        self.texto = None
        #Posicion del cursor(en nro de caracteres)
        self.cursor = 0

        #Caracteristicas de la tipografia
        self.font_size = 12
        self.font_type = "Georgia"
        self.color_r, self.color_g, self.color_b = 0, 0, 0
        self.italic = False
        self.bold = False

        #Tamanio del renglon
        self.alto_renglon = 12

        #Permite dibujar o no recuadro
        self.mostrar_borde = False

        #Dibujar o no el cursor
        self.mostrar_cursor = False

        #texto en cada renglon
        self.renglones = []
        # 1 =el renglon i termino con un espacio
        # 0= el renglon i no termino con espacio
        self.esp_reg = []

        # Lo uso para acentuar letras con comilla simple
        self.double_key = None

    def set_text(self, text):
        self.texto = text
        self.renglones = self.texto.split('\r')
        for i in range(len(self.renglones)):
            self.esp_reg.append(0)
        self.cursor = len(text)

    def imprimir(self, context):
        context.set_source_rgb(self.color_r, self.color_g, self.color_b)
        if self.mostrar_borde:
            #dibuja recuadro
            context.set_line_width(1)
            context.rectangle(self.x - self.ancho, self.y - self.alto,
                2 * self.ancho, 2 * self.alto)
            context.stroke()

        # Insertando el texto
        slant = cairo.FONT_SLANT_NORMAL
        if self.italic:
            slant = cairo.FONT_SLANT_ITALIC
        weight = cairo.FONT_WEIGHT_NORMAL
        if self.bold:
            weight = cairo.FONT_WEIGHT_BOLD

        context.select_font_face(self.font_type, slant, weight)
        context.set_font_size(self.font_size)

        if self.texto:
            cursor_dib = self.cursor    # dibujar cursor

            for i in range(len(self.renglones)):
                #text_reng = unicode(self.renglones[i],'UTF8')
                text_reng = self.renglones[i]
                xbearing, ybearing, width, height, xadvance, yadvance = \
                context.text_extents(self.renglones[i].replace(" ", "-"))

                context.move_to(self.x - width / 2 - 1,
                    self.y - self.alto + (i + 1) * self.alto_renglon)
                context.set_source_rgb(self.color_r, self.color_g,
                    self.color_b)
                context.show_text(self.renglones[i])

                if self.mostrar_cursor:
                    if cursor_dib >= len(text_reng) + self.esp_reg[i]:
                        cursor_dib -= (len(text_reng) + self.esp_reg[i])

                    elif cursor_dib != -99:
                        try:
                            xbearing1, ybearing1, width1, \
                            height1, xadvance1, yadvance1 = \
                                context.text_extents( \
                                text_reng[0:cursor_dib].replace(" ", "-"))
                            context.move_to(self.x - width / 2 - 1 + width1,
                                self.y - self.alto + \
                                (i + 1) * self.alto_renglon)
                            context.show_text("_")
                            # para que no lo vuelva a dibujar en otro renglon
                            cursor_dib = - 99
                        except:
                            print "ERROR", \
                                text_reng[0:cursor_dib].replace(" ", "-")

        elif self.mostrar_cursor:
            context.move_to(self.x, self.y - self.alto + self.alto_renglon)
            context.set_source_rgb(0, 0, 0)
            context.show_text("_")

        context.stroke()

    def insertar_texto(self, key, keyval, context):

        # correcion para teclado de uruguay -->
        if (keyval == 65105):
            # comilla simple
            if self.double_key == None:
                self.double_key = "'"
            else:
                key = "'"
                self.double_key = None

        if self.double_key == "'":
            vocals = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", \
                      "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú"}
            if key in vocals:
                key = vocals[key]
                self.double_key = None

        if (keyval == 65111):
            # comilla doble
            if self.double_key == None:
                self.double_key = '"'
            else:
                key = '"'
                self.double_key = None

        if self.double_key == '"':
            vocals = {"a": "ä", "e": "ë", "i": "ï", "o": "ö", "u": "ü", \
                      "A": "Ä", "E": "Ë", "I": "Ï", "O": "Ö", "U": "Ü"}
            if key in vocals:
                key = vocals[key]
                self.double_key = None

        if self.texto:

            if keyval == gtk.gdk.keyval_from_name('BackSpace'):
                if self.cursor >= 1:
                    self.texto = self.texto[0:self.cursor - 1] + \
                        self.texto[self.cursor:len(self.texto)]
                    self.cursor -= 1
                self.redimensionar(context)

            elif keyval == gtk.gdk.keyval_from_name('Return'):
                self.texto = self.texto[0:self.cursor] + "\n" + \
                    self.texto[self.cursor:len(self.texto)]
                self.cursor += 1
                self.redimensionar(context)

            elif keyval == gtk.gdk.keyval_from_name('Right'):
                if self.cursor < len(self.texto):
                    self.cursor += 1

            elif keyval == gtk.gdk.keyval_from_name('Left'):
                if self.cursor > 0:
                    self.cursor -= 1

            elif keyval == gtk.gdk.keyval_from_name('Up'):
                sum_ren = 0
                #se averigua en que renglon esta el cursor
                for i in range(len(self.renglones)):
                    if sum_ren <= self.cursor < \
                        (sum_ren + len(self.renglones[i]) + self.esp_reg[i]):
                        if i != 0:
                            #calculo desplazamiento dentro de un renglon
                            cur_ren = self.cursor - sum_ren
                            self.cursor = \
                                min(sum_ren - len(self.renglones[i - 1])
                                - self.esp_reg[i - 1] + \
                                cur_ren, sum_ren - 1)
                        break
                    else:
                        sum_ren += (len(self.renglones[i]) + self.esp_reg[i])

            elif keyval == gtk.gdk.keyval_from_name('Down'):
                sum_ren = 0
                #se averigua en que renglon esta el cursor
                for i in range(len(self.renglones)):
                    if sum_ren <= self.cursor < (sum_ren +
                        len(self.renglones[i]) + self.esp_reg[i]):
                        if i != len(self.renglones) - 1:
                            #calculo desplazamiento dentro de un renglon
                            cur_ren = self.cursor - sum_ren
                            self.cursor = min(sum_ren + \
                                len(self.renglones[i]) + \
                                self.esp_reg[i] + cur_ren, \
                                sum_ren + len(self.renglones[i]) + \
                                self.esp_reg[i] + \
                                len(self.renglones[i + 1]) + \
                                self.esp_reg[i + 1] - 1)
                        break
                    else:
                        sum_ren += (len(self.renglones[i]) + self.esp_reg[i])

            else:
                agregar = unicode(key, 'UTF8')
                self.texto = self.texto[0:self.cursor] + agregar + \
                    self.texto[self.cursor:len(self.texto)]
                if key != "":
                    self.cursor += len(agregar)
                    self.redimensionar(context)

        else:
            self.texto = unicode(key, 'UTF8')
            self.cursor = len(self.texto)
            self.redimensionar(context)

    """
    ATENCION: redimensionar no funciona bien con utf8
    """

    def redimensionar(self, context):
        pass
        """
        Establece el texto en cada renglon dependiendo de las dimensiones
        del cuadro, manteniendo fijo el ancho,
        y redimensionando el alto si es necesario
        """

        if self.texto is not None:

            texto_oracion = self.texto.split("\n")

            self.renglones = []  # texto en cada renglon
            self.esp_reg = []  # 1=indica si el renglon termino con un espacio.

            for j in range(len(texto_oracion)):

                texto_renglon = texto_oracion[j]

                while texto_renglon is not None:

                    for i in range(len(texto_renglon.split(" "))):

                        xbearing, ybearing, width, height, \
                            xadvance, yadvance = \
                            context.text_extents( \
                            texto_renglon.rsplit(" ", i)[0].replace(" ", "-"))
                        # es remplazado " " por "-" para que pueda calcular
                        # el ancho considerando los
                        # espacios (el caracter - tiene el mismo ancho
                        # que el espacio)

                        if width <= self.ancho * 2:

                            self.renglones.append(texto_renglon.rsplit(" ", \
                                i)[0])
                            self.esp_reg.append(1)

                            if i != 0:
                                posi_space = len(texto_renglon.split(" "))
                                texto_renglon = \
                                    texto_renglon.split(" ",
                                    posi_space - i)[posi_space - i]
                            else:
                                texto_renglon = None
                            break

                        elif i == (len(texto_renglon.split(" ")) - 1):
                            #este es el caso que no entra ni una palabra

                            #tiene problemas de performance:se podria mejorar
                            #empezando desde la izq

                            palabra = (texto_renglon.rsplit(" ", i)[0])
                            if i != 0:
                                posi_space = len(texto_renglon.split(" "))
                                texto_renglon = " " + \
                                    texto_renglon.split(" ",
                                    posi_space - i)[posi_space - i]
                            else:
                                texto_renglon = ""

                            for k in range(1, len(palabra)):
                                xbearing, ybearing, width, height, \
                                    xadvance, yadvance = \
                                    context.text_extents( \
                                    palabra[:len(palabra) - k])
                                if width <= self.ancho * 2:
                                    self.renglones.append( \
                                        palabra[:len(palabra) - k])
                                    self.esp_reg.append(0)
                                    texto_renglon = \
                                    palabra[len(palabra) - k:len(palabra)] + \
                                    texto_renglon
                                    break

                if len(self.renglones) * self.alto_renglon > self.alto * 2:
                    self.alto = len(self.renglones) * self.alto_renglon / 2

    def mover_a(self, x, y):
        "Mueve el centro del cuadro a la posicion (x,y)"
        self.y = y
        self.x = x

    def set_dimension(self, ancho, alto):
        """
        Establece las dimensiones del cuadro siendo
        el ancho del cuadro = 2*ancho
        y el alto del cuadro=2*alto
        """
        self.ancho = ancho
        self.alto = alto

    def deshacer(self, context):
        "Se utiliza para deshacer la creacion de un nuevo renglon de texto"
        self.texto = self.texto[0:self.cursor - 1] + \
                self.texto[self.cursor:len(self.texto)]
        self.cursor -= 1
        self.alto -= self.alto_renglon
        self.redimensionar(context)
