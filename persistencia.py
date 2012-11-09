import os
import simplejson
import globos
from sugar3.activity import activity
import zipfile


class PageData:

    def __init__(self):
        self.boxs = []


class BoxData:

    def __init__(self):
        self.globos = []
        self.image_name = None


class Persistence:

    def write(self, file_name, page):

        """
        Persitencia:
        Cuadro_titulo, globos[]
        Lista de cuadros, imagen de fondo, globos[]
        por cada globo: tipo, posicion (x,y), ancho, alto,
        direccion, pos_flecha (x,y), texto,font, tamanio, color
        """
        instance_path = os.path.join(activity.get_activity_root(), 'instance')

        # Copio los datos de Page en PageData

        pageData = {}
        pageData['version'] = '1'
        pageData['boxs'] = []
        for box in page.boxs:
            boxData = {}
            boxData['image_name'] = box.image_name
            boxData['globes'] = []
            for globo in box.globos:
                globoData = {}
                globoData['title_globe'] = (globo == box.title_globe)
                print 'Grabando', globo.globe_type
                globoData['globe_type'] = globo.globe_type
                globoData['radio'] = globo.radio
                globoData['width'], globoData['height'] = \
                    globo.ancho, globo.alto
                if (globo.__class__ != globos.Rectangulo):
                    globoData['point_0'] = globo.punto[0]
                    globoData['point_1'] = globo.punto[1]
                globoData['direction'] = globo.direccion
                if (globo.__class__ == globos.Globo):
                    globoData['mode'] = globo.modo
                if (globo.__class__ == globos.Imagen):
                    globoData['image_name'] = globo.image_name
                globoData['x'], globoData['y'] = globo.x, globo.y
                #globoData.ancho_text, globoData.alto_text =
                #globo.ancho_text, globo.alto_text

                globoData['text_width'] = globo.texto.ancho
                globoData['text_height'] = globo.texto.alto
                globoData['text_x'], globoData['text_y'] = \
                    globo.texto.x, globo.texto.y
                globoData['text_text'] = globo.texto.texto
                globoData['text_rows'] = globo.texto.renglones
                globoData['text_sp_rows'] = globo.texto.esp_reg

                globoData['text_row_height'] = globo.texto.alto_renglon
                globoData['text_font_size'] = globo.texto.font_size
                globoData['text_font_type'] = globo.texto.font_type
                globoData['text_bold'] = globo.texto.bold
                globoData['text_italic'] = globo.texto.italic

                globoData['text_color_r'] = globo.texto.color_r
                globoData['text_color_g'] = globo.texto.color_g
                globoData['text_color_b'] = globo.texto.color_b

                globoData['text_show_border'] = globo.texto.mostrar_borde
                globoData['text_show_cursor'] = globo.texto.mostrar_cursor

                boxData['globes'].append(globoData)
            pageData['boxs'].append(boxData)

        # hago picle de pageData
        print pageData

        data_file_name = 'data.json'
        f = open(os.path.join(instance_path, data_file_name), 'w')
        try:
            simplejson.dump(pageData, f)
        finally:
            f.close()

        print 'file_name', file_name

        z = zipfile.ZipFile(file_name, 'w')
        z.write(os.path.join(instance_path, data_file_name).encode('ascii',
            'ignore'), data_file_name.encode('ascii', 'ignore'))
        for box in page.boxs:
            if (box.image_name != ''):
                z.write(os.path.join(instance_path,
                    box.image_name).encode('ascii', 'ignore'),
                    box.image_name.encode('ascii', 'ignore'))
        z.close()

    def read(self, file_name, page):

        instance_path = os.path.join(activity.get_activity_root(), 'instance')
        z = zipfile.ZipFile(file_name, 'r')
        for file_name in z.namelist():
            if (file_name != './'):
                try:
                    print 'extrayendo', file_name
                    # la version de python en las xo no permite hacer
                    # extract :(
                    # z.extract(file_name,instance_path)
                    data = z.read(file_name)
                    fout = open(os.path.join(instance_path, file_name), 'w')
                    fout.write(data)
                    fout.close()
                except:
                    print 'Error extrayendo', file_name
        z.close()
        data_file_name = 'data.json'

        pageData = PageData()
        f = open(os.path.join(instance_path, data_file_name), 'r')
        try:
            pageData = simplejson.load(f)
        finally:
            f.close()

        primero = True
        for boxData in pageData['boxs']:
            if not primero:
                # el primero ya esta creado
                page.add_box_from_journal_image(None)
            primero = False
            box = page.get_active_box()
            box.image_name = boxData['image_name']
            for globoData in boxData['globes']:
                globo_x, globo_y = globoData['x'], globoData['y']
                globo_modo = None
                if ('mode' in globoData):
                    globo_modo = globoData['mode']
                globo_direccion = globoData['direction']

                tipo_globo = globoData['globe_type']
                print 'tipo_globo', tipo_globo
                globo = None
                if (tipo_globo == 'GLOBE'):
                    globo = globos.Globo(x=globo_x, y=globo_y,
                        modo=globo_modo, direccion=globo_direccion)
                elif (tipo_globo == 'CLOUD'):
                    globo = globos.Nube(x=globo_x, y=globo_y,
                        direccion=globo_direccion)
                elif (tipo_globo == 'EXCLAMATION'):
                    globo = globos.Grito(x=globo_x, y=globo_y,
                        direccion=globo_direccion)
                elif (tipo_globo == 'RECTANGLE'):
                    globo = globos.Rectangulo(x=globo_x, y=globo_y)
                elif (tipo_globo == 'IMAGE'):
                    image_name = globoData['image_name']
                    globo = globos.Imagen(image_name, x=globo_x, y=globo_y)
                    globo.direccion = globo_direccion

                if globo != None:
                    globo.radio = globoData['radio']
                    globo.ancho, globo.alto = globoData['width'], \
                        globoData['height']

                    if (tipo_globo != 'RECTANGLE'):
                        globo.punto = [globoData['point_0'],
                            globoData['point_1']]

                    globo.x, globo.y = globoData['x'], globoData['y']

                    globo.texto.ancho = globoData['text_width']
                    globo.texto.alto = globoData['text_height']
                    globo.texto.x, globo.texto.y = globoData['text_x'], \
                        globoData['text_y']
                    globo.texto.texto = globoData['text_text']
                    globo.texto.renglones = globoData['text_rows']
                    globo.texto.esp_reg = globoData['text_sp_rows']

                    globo.texto.alto_renglon = globoData['text_row_height']
                    globo.texto.font_size = globoData['text_font_size']
                    globo.texto.font_type = globoData['text_font_type']
                    globo.texto.bold = globoData['text_bold']
                    globo.texto.italic = globoData['text_italic']

                    globo.texto.color_r = globoData['text_color_r']
                    globo.texto.color_g = globoData['text_color_g']
                    globo.texto.color_b = globoData['text_color_b']

                    globo.texto.mostrar_borde = globoData['text_show_border']
                    globo.texto.mostrar_cursor = globoData['text_show_cursor']
                    box.globos.append(globo)

                    if globoData['title_globe']:
                        box.title_globe = globo

            box.queue_draw()
