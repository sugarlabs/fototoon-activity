# -*- coding: UTF_8 -*-

import os, sys
import simplejson
import globos


class PageData:

    def __init__(self):
        self.boxs = []

class BoxData:

    def __init__(self):
        self.globos = []
        self.image_name = None



class Persistence:

    def write(self,file_name,page):
        """
        Persitencia:
        Cuadro_titulo, globos[]
        Lista de cuadros, imagen de fondo, globos[]
        por cada globo: tipo, posicion (x,y), ancho, alto, direccion, pos_flecha (x,y), texto,font, tamanio, color
    
        """

        # Copio los datos de Page en PageData

        pageData = {}
        pageData["boxs"]  = []
        for box in page.boxs:
            boxData = {}
            boxData["image_name"] = box.image_name
            boxData["globos"] = []
            for globo in box.globos:
                globoData = {}
                print "Grabando",globo.globe_type
                globoData['globe_type'] = globo.globe_type
                globoData['radio'] = globo.radio
                globoData['ancho'],globoData['alto'] = globo.ancho,globo.alto
                if (globo.__class__ != globos.Rectangulo):
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


                boxData["globos"].append(globoData)                        
            pageData["boxs"].append(boxData)
    
        # hago picle de pageData
        print pageData        
        f = open(file_name, 'w')
        try:
            simplejson.dump(pageData, f)
        finally:
            f.close()


    def read(self,file_name,page):

        pageData = PageData()
        f = open(file_name, 'r')
        try:
            pageData = simplejson.load(f)
        finally:
            f.close()

        primero = True
        for boxData in pageData["boxs"]:
            if not primero: 
                # el primero ya esta creado
                page.add_box()
            primero = False
            box = page.get_active_box()
            box.image_name = boxData["image_name"]
            for globoData in boxData["globos"]:
                globo_x,globo_y = globoData['x'],globoData['y']
                globo_modo = None
                if ('modo' in globoData):
                    globo_modo = globoData['modo']
                globo_direccion = globoData['direccion']
                
                tipo_globo = globoData['globe_type']
                print "tipo_globo", tipo_globo
                globo = None
                if (tipo_globo == "GLOBE"):
                    globo = globos.Globo(x = globo_x , y = globo_y , modo = globo_modo , direccion = globo_direccion)
                elif (tipo_globo == "CLOUD"):   
                    globo = globos.Nube(x = globo_x , y = globo_y , direccion = globo_direccion)
                elif (tipo_globo == "EXCLAMATION"):   
                    globo = globos.Grito(x = globo_x , y = globo_y , direccion = globo_direccion)
                elif (tipo_globo == "RECTANGLE"):   
                    globo = globos.Rectangulo(x = globo_x , y = globo_y)
    
                if globo != None:
                    globo.radio = globoData['radio']
                    globo.ancho,globo.alto = globoData['ancho'],globoData['alto']
                                        if (tipo_globo != "RECTANGLE"):
                        globo.punto = [globoData['punto_0'],globoData['punto_1']]

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
                    box.globos.append(globo)

            box.queue_draw()    

