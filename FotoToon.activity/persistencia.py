# -*- coding: UTF_8 -*-

import os, sys
import pickle
import globos

class PaginaData:

    def __init__(self):
        self.cuadros = []

class CuadroData:

    def __init__(self):
        self.globos = []
        self.image_name = None

class Persistence:

    def write(self,file_name,pagina):
        """
        Persitencia:
        Cuadro_titulo, globos[]
        Lista de cuadros, imagen de fondo, globos[]
        por cada globo: tipo, posicion (x,y), ancho, alto, direccion, pos_flecha (x,y), texto,font, tamanio, color
    
        """

        # Copio los datos de Pagina en PaginaData

        paginaData = PaginaData()
        for cuadro in pagina.cuadros:
            cuadroData = CuadroData()
            cuadroData.image_name = cuadro.image_name
            for globo in cuadro.globos:
                globoData = {}
                print "Grabando",globo.__class__
                globoData['tipo_globo'] = globo.__class__
                globoData['radio'] = globo.radio
                globoData['ancho'],globoData['alto'] = globo.ancho,globo.alto
                globoData['punto_0'] = globo.punto[0]
                globoData['punto_1'] = globo.punto[1]
                globoData['direccion'] = globo.direccion
                if (globo.__class__ == globos.Globo):
                    globoData['modo'] = globo.modo
                globoData['x'],globoData['y'] = globo.x,globo.y
                #globoData.ancho_text, globoData.alto_text = globo.ancho_text, globo.alto_text
                
                globoData['text_ancho'] = globo.texto.ancho
                globoData['text_alto']  = globo.texto.alto
                globoData['text_ancho'] = globo.texto.ancho
                globoData['text_x'], globoData['text_y']  = globo.texto.x, globo.texto.y
                globoData['text_texto'] = globo.texto.texto
                globoData['text_renglones'] = globo.texto.renglones
                globoData['text_esp_renglones'] = globo.texto.esp_reg
                
                globoData['text_alto_renglon'] = globo.texto.alto_renglon
                globoData['text_font_size'] = globo.texto.font_size
                globoData['text_font_type'] = globo.texto.font_type
                globoData['text_bold'] = globo.texto.bold
                globoData['text_italic'] = globo.texto.italic
                
                globoData['text_color_r'] = globo.texto.color_r
                globoData['text_color_g'] = globo.texto.color_g
                globoData['text_color_b'] = globo.texto.color_b

                globoData['text_mostrar_borde'] = globo.texto.mostrar_borde
                globoData['text_mostrar_cursor'] = globo.texto.mostrar_cursor

                cuadroData.globos.append(globoData)                        
            paginaData.cuadros.append(cuadroData)
    
        # hago picle de paginaData

        f = open(file_name, 'w')
        try:
            pickle.dump(paginaData, f)
        finally:
            f.close()


    def read(self,file_name,pagina):

        paginaData = PaginaData()
        f = open(file_name, 'r')
        try:
            paginaData = pickle.load(f)
        finally:
            f.close()

        primero = True
        for cuadroData in paginaData.cuadros:
            if not primero: 
                # el primero ya está creado
                pagina.add_cuadro()
            primero = False
            cuadro = pagina.get_cuadro_activo()
            cuadro.image_name = cuadroData.image_name
            for globoData in cuadroData.globos:
                globo_x,globo_y = globoData['x'],globoData['y']
                globo_modo = None
                if ('modo' in globoData):
                    globo_modo = globoData['modo']
                globo_direccion = globoData['direccion']
                
                tipo_globo = globoData['tipo_globo']
                print "tipo_globo", tipo_globo
                globo = None
                if (tipo_globo == globos.Globo):
                    globo = globos.Globo(x = globo_x , y = globo_y , modo = globo_modo , direccion = globo_direccion)
                elif (tipo_globo == globos.Nube):   
                    globo = globos.Nube(x = globo_x , y = globo_y , direccion = globo_direccion)
                elif (tipo_globo == globos.Grito):   
                    globo = globos.Grito(x = globo_x , y = globo_y , direccion = globo_direccion)
                elif (tipo_globo == globos.Rectangulo):   
                    globo = globos.Grito(x = globo_x , y = globo_y)
    
                if globo != None:
                    globo.radio = globoData['radio']
                    globo.ancho,globo.alto = globoData['ancho'],globoData['alto']                    globo.punto = [globoData['punto_0'],globoData['punto_1']]

                    globo.x,globo.y = globoData['x'],globoData['y']
                    
                    globo.texto.ancho = globoData['text_ancho']
                    globo.texto.alto = globoData['text_alto'] 
                    globo.texto.ancho = globoData['text_ancho']
                    globo.texto.x, globo.texto.y = globoData['text_x'], globoData['text_y']
                    globo.texto.texto = globoData['text_texto']
                    globo.texto.renglones = globoData['text_renglones']
                    globo.texto.esp_reg = globoData['text_esp_renglones']

                    globo.texto.alto_renglon = globoData['text_alto_renglon']
                    globo.texto.font_size = globoData['text_font_size']
                    globo.texto.font_type = globoData['text_font_type']
                    globo.texto.bold = globoData['text_bold']
                    globo.texto.italic = globoData['text_italic']
                    
                    globo.texto.color_r = globoData['text_color_r']
                    globo.texto.color_g = globoData['text_color_g']
                    globo.texto.color_b = globoData['text_color_b']

                    globo.texto.mostrar_borde = globoData['text_mostrar_borde']
                    globo.texto.mostrar_cursor = globoData['text_mostrar_cursor']
                    cuadro.globos.append(globo)

            cuadro.queue_draw()    

