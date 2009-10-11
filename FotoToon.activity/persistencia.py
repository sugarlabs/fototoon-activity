# -*- coding: UTF_8 -*-

import os, sys
import pickle

class PaginaData:

    def __init__(self):
        self.cuadros = []

class CuadroData:

    def __init__(self):
        self.globos = []
        self.image_name = None

class GloboData:

    def __init__(self):
        self.radio = 30                    #determina tamaño minimo
        self.ancho,self.alto = 0,0        #dimensiones de la elipse        self.punto = [5,10]
        self.direccion = ""                 #direccion ="abajo","arriba","der","izq"
        self.modo = ""                    #2 tipos de globos: "normal" o "despacio"
        self.x,self.y  = 0,0            #Centro de la elipse
        self.ancho_text, self.alto_text = 0,0

class TextData:

    def __init__(self):
        self.ancho = 0                #Ancho del cuadro = 2*self.ancho
        self.alto = 0                #Alto del cuadro = 2*self.alto
    
        self.x,self.y = 0,0            #Centro del cuadro
                                     #Centro del cuadro
        
        self.texto = None        
        
        self.font_size = 0            #Caracteristicas de la tipografia
        self.font_type = ""
        
        self.alto_renglon = 12        #Tamaño del renglon
        
        self.mostrar_borde = False  #Permite dibujar o no recuadro
        
        self.mostrar_cursor = False    #Dibujar o no el cursor
        
        self.renglones = []         #texto en cada renglon


class Writer:

    def write(self,file_name,pagina):
        """
        Persitencia:
        Cuadro_titulo, globos[]
        Lista de cuadros, imagen de fondo, globos[]
        por cada globo: tipo, posicion (x,y), ancho, alto, direccion, pos_flecha (x,y), texto
    
        """

        # Copio los datos de Pagina en PaginaData

        paginaData = PaginaData()
        for cuadro in pagina.cuadros:
            cuadroData = CuadroData()
            cuadroData.image_name = cuadro.image_name
            for globo in cuadro.globos:
                globoData = GloboData()
                globoData.radio = globo.radio
                globoData.ancho,globoData.alto = globo.ancho,globo.alto                globoData.punto = globo.punto
                globoData.direccion = globo.direccion
                globoData.modo = globo.modo
                globoData.x,globoData.y = globo.x,globo.y
                #globoData.ancho_text, globoData.alto_text = globo.ancho_text, globo.alto_text
                
                textData = TextData()
                globo.text = textData

                textData.ancho = globo.text.ancho
                textData.alto  = globo.text.alto
                textData.ancho = globo.text.ancho
                textData.x, textData.y  = globo.text.x, globo.text.y
                textData.texto = globo.text.texto

                textData.font_size = globo.text.font_size
                textData.font_type = globo.text.font_type
                textData.alto_renglon = globo.text.alto_renglon

                textData.mostrar_borde = globo.text.mostrar_borde
                textData.mostrar_cursor = globo.text.mostrar_cursor
                textData.alto_renglon = globo.text.alto_renglon

                textData.alto_renglon = globo.text.alto_renglon

                cuadroData.globos.append(globoData)                        
            paginaData.cuadros.append(cuadroData)
    
        # hago picle de paginaData

        f = open(file_name, 'w')
        try:
            pickle.dump(paginaData, f)
        finally:
            f.close()

        
