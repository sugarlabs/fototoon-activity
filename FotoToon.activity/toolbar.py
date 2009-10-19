# copiado de la actividad write
# Copyright (C) 2006, Martin Sevior
# Copyright (C) 2006-2007, Marc Maurer <uwog@uwog.net>
# Copyright (C) 2007, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
from gettext import gettext as _
import logging
import os
import time

import gtk, pango, pangocairo

import globos

from sugar.graphics.icon import Icon
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.graphics.combobox import ComboBox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.graphics import iconentry
from sugar.graphics.objectchooser import ObjectChooser

#from sugar.datastore import datastore

#import sugar.profile

#import dbus

logger = logging.getLogger('write-activity')

#ick
TOOLBAR_ACTIVITY = 0
TOOLBAR_EDIT = 1
TOOLBAR_TEXT = 2
TOOLBAR_IMAGE = 3
TOOLBAR_TABLE = 4
TOOLBAR_VIEW = 5

class GlobesToolbar(gtk.Toolbar):

    def __init__(self, page,activity):

        gtk.Toolbar.__init__(self)

        self._page = page
        self._activity = activity

        # agregar cuadro
        self.b_add_photo = ToolButton('add-photo')
        self.b_add_photo.connect('clicked', self._image_cb)
        self.b_add_photo.set_tooltip(_('Add Photo'))
        self.insert(self.b_add_photo, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)

        # agrega globo
        self.b_agregar = ToolButton('add-globe')
        self.b_agregar.connect('clicked', self.agrega_gnormal)
        self.b_agregar.set_tooltip(_('Add Globe'))
        self.insert(self.b_agregar, -1)
    
        #agrega nube
        self.b_agregar = ToolButton('add-nube')
        self.b_agregar.connect('clicked', self.agrega_gpensar)
        self.b_agregar.set_tooltip(_('Add Think'))
        self.insert(self.b_agregar, -1)
    
        # agrega susurro
        self.b_agregar = ToolButton('add-susurro')
        self.b_agregar.connect('clicked', self.agrega_gdespacio)
        self.b_agregar.set_tooltip(_('Add Whisper'))
        self.insert(self.b_agregar, -1)
    
        # agrega grito
        self.b_agregar = ToolButton('add-grito')
        self.b_agregar.connect('clicked', self.agrega_ggrito)
        self.b_agregar.set_tooltip(_('Add Exclamation'))
        self.insert(self.b_agregar, -1)
    
        # agrega caja
        self.b_agregar = ToolButton('add-box')
        self.b_agregar.connect('clicked', self.agrega_grect)
        self.b_agregar.set_tooltip(_('Add Box'))
        self.insert(self.b_agregar, -1)
    
        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)

        # girar
        self.b_girar = ToolButton('turn')
        self.b_girar.connect('clicked', self.girar)
        self.b_girar.set_tooltip(_('Turn'))
        self.insert(self.b_girar, -1)

        # borrar
        self.b_borrar = ToolButton('gtk-delete')
        self.b_borrar.connect('clicked', self.borrar)
        self.b_borrar.set_tooltip(_('Delete'))
        self.insert(self.b_borrar, -1)



    def agrega_gnormal(self, boton):
        self._page.get_active_box().add_globo(60, 60)

    def agrega_gpensar(self, boton):
        self._page.get_active_box().add_nube(60, 60)
    
    def agrega_gdespacio(self, boton):
        self._page.get_active_box().add_globo(60, 60,gmodo="despacio")
    
    def agrega_ggrito(self, boton):
        self._page.get_active_box().add_grito(60, 60)
    
    def agrega_grect(self, boton):
        self._page.get_active_box().add_rectangulo(60, 60)
    
    def agrega_imagen(self, boton):
        self._page.get_active_box().add_imagen(60, 60)

    def girar(self, boton):
        print "girando"
        #veo cual es el globo seleccionado y o giro
        box = self._page.get_active_box()
        if (box.get_globo_activo() != None):
            print "globo activo",
            globe = box.get_globo_activo()
            if (globe.__class__ != globos.Rectangulo):            
                if (globe.direccion == globos.DIR_ABAJO):
                    globe.direccion = globos.DIR_IZQ        

                elif (globe.direccion == globos.DIR_IZQ):
                    globe.direccion = globos.DIR_ARRIBA        

                elif (globe.direccion == globos.DIR_ARRIBA):
                    globe.direccion = globos.DIR_DER        

                elif (globe.direccion == globos.DIR_DER):
                    globe.direccion = globos.DIR_ABAJO        
                globe.punto[0],globe.punto[1] = globe.punto[1],globe.punto[0]

                box.queue_draw()

    def borrar(self, boton):
        print "borrando"
        box = self._page.get_active_box()
        if (box.get_globo_activo() != None):
            print "borrando globo"
            box.globos.remove(box.get_globo_activo())
            box.set_globo_activo(None)
            box.queue_draw()
        # Borrar un box es mas complicado
        """
        else:
            print "borrando box"
            self.page.boxs.remove(box)
            if (len(self.page.boxs) > 0):
                print "seteo el primero como activo"
                self.page.set_active_box(self.page.boxs[0])
                for cu in self.page.boxs:
                    print "redibujo"
                    cu.queue_draw()
            else:
                self.page._active_box = None
        """

    def _image_cb(self, button):
    
        #chooser = ObjectChooser(_('Choose image'), self._activity,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,what_filter='Image')
        chooser = ObjectChooser(_('Choose image'), self._activity,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        #chooser = ObjectChooser(_('Choose image'), self._activity,
        #                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        try:
            result = chooser.run()
            print result, gtk.RESPONSE_ACCEPT
            if result == gtk.RESPONSE_ACCEPT:
                logging.debug('ObjectChooser: %r' % chooser.get_selected_object())
                jobject = chooser.get_selected_object()
                if jobject and jobject.file_path:
                    print "imagen seleccionada:",jobject.file_path
                    tempfile_name = os.path.join(self._activity.get_activity_root(), 'instance', 'tmp%i' % time.time())
                    os.link(jobject.file_path, tempfile_name)
                    self._page.add_box_from_journal_image(tempfile_name)
        finally:
            chooser.destroy()
            del chooser


class TextToolbar(gtk.Toolbar):

    def __init__(self, page):
        self._colorseldlg = None

        gtk.Toolbar.__init__(self)

        self._page = page
        page._text_toolbar = self

        self._bold = ToggleToolButton('format-text-bold')
        self._bold.set_tooltip(_('Bold'))
        self._bold_id = self._bold.connect('clicked', self._bold_cb)
        self.insert(self._bold, -1)
        self._bold.show()

        self._italic = ToggleToolButton('format-text-italic')
        self._italic.set_tooltip(_('Italic'))
        self._italic_id = self._italic.connect('clicked', self._italic_cb)
        self.insert(self._italic, -1)
        self._italic.show()

        """
        self._underline = ToggleToolButton('format-text-underline')
        self._underline.set_tooltip(_('Underline'))
        self._underline_id = self._underline.connect('clicked', self._underline_cb)
        self.insert(self._underline, -1)
        self._underline.show()
        """

        self._text_color = gtk.ColorButton()
        self._text_color_id = self._text_color.connect('color-set', self._text_color_cb)
        tool_item = gtk.ToolItem()
        tool_item.add(self._text_color)
        self.insert(tool_item, -1)
        tool_item.show_all()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.show()
        self.insert(separator, -1)

        # tamanio 
        self._font_size_icon = Icon(icon_name="format-text-size", icon_size=gtk.ICON_SIZE_LARGE_TOOLBAR)
        tool_item = gtk.ToolItem()
        tool_item.add(self._font_size_icon)
        self.insert(tool_item, -1)
        tool_item.show_all()

        self._font_size_combo = ComboBox()
        self._font_sizes = ['8', '10', '12', '14', '16', '20', '22', '24', '26', '28', '36', '48', '72']
        self._font_size_changed_id = self._font_size_combo.connect('changed', self._font_size_changed_cb)
        for i, s in enumerate(self._font_sizes):
            self._font_size_combo.append_item(i, s, None)
            if s == '12':
                self._font_size_combo.set_active(i)
        tool_item = ToolComboBox(self._font_size_combo)
        self.insert(tool_item, -1);
        tool_item.show()


        # font 
        self._has_custom_fonts = False

        self._fonts = []
        pango_context = gtk.Widget.create_pango_context(tool_item)
        for family in pango_context.list_families():
            self._fonts.append(family.get_name())
        self._fonts.sort()
            
        self._font_combo = ComboBox()
        self._fonts_changed_id = self._font_combo.connect('changed', self._font_changed_cb)
        for i, f in enumerate(self._fonts):
            self._font_combo.append_item(i, f, None)
            if f == 'Times New Roman':
                self._font_combo.set_active(i)
        tool_item = ToolComboBox(self._font_combo)
        self.insert(tool_item, -1);
        tool_item.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()


    def get_text_selected_handler(self):
        return self._text_selected_handler

    def _add_widget(self, widget, expand=False):
        tool_item = gtk.ToolItem()
        tool_item.set_expand(expand)

        tool_item.add(widget)
        widget.show()

        self.insert(tool_item, -1)
        tool_item.show()


    def _bold_cb(self, button):
        globo_activo = self._page.get_globo_activo()
        if (globo_activo != None):
            globo_activo.texto.bold = not globo_activo.texto.bold
            self._page.get_active_box().queue_draw()    

    def _italic_cb(self, button):
        globo_activo = self._page.get_globo_activo()
        if (globo_activo != None):
            globo_activo.texto.italic = not globo_activo.texto.italic
            self._page.get_active_box().queue_draw()    

    def _text_color_cb(self, button):
        globo_activo = self._page.get_globo_activo()
        if (globo_activo != None):
            newcolor = self._text_color.get_color()
            texto = globo_activo.texto
            texto.color_r,texto.color_g,texto.color_b = (newcolor.red / 65535.0),(newcolor.green / 65535.0),(newcolor.blue / 65535.0)
            self._page.get_active_box().queue_draw()    


    def _font_size_changed_cb(self, combobox):
        if self._font_size_combo.get_active() != -1:
            size = int(self._font_sizes[self._font_size_combo.get_active()])
            logger.debug('Setting font size: %d', size)
            globo_activo = self._page.get_globo_activo()
            if (globo_activo != None):
                globo_activo.texto.font_size = size
                globo_activo.texto.alto_renglon = size
                self._page.get_active_box().queue_draw()    

    def _font_changed_cb(self, combobox):
        if self._font_combo.get_active() != -1:
            logger.debug('Setting font name: %s', self._fonts[self._font_combo.get_active()])
            globo_activo = self._page.get_globo_activo()
            if (globo_activo != None):
                globo_activo.texto.font_type = self._fonts[self._font_combo.get_active()]
                self._page.get_active_box().queue_draw()    
            



	"""
	Estos son los metodos para setear los contrles de la barra en base a el texto del globo
	como el globo va a tener un solo font seleccionado, voy a hacer un solo metodo

	"""

    def setToggleButtonState(self,button,b,id):
        button.handler_block(id)
        button.set_active(b)
        button.handler_unblock(id)

    def setToolbarState(self,globeText):
        # seteo bold
        self.setToggleButtonState(self._bold,globeText.bold ,self._bold_id)
        # seteo italic
        self.setToggleButtonState(self._italic, globeText.italic, self._italic_id)
        # color
        self._text_color.set_color(gtk.gdk.Color(int(globeText.color_r * 65535), int(globeText.color_g * 65535), int(globeText.color_b * 65535)))
        # font size
        for i, s in enumerate(self._font_sizes):
            if int(s) == int(globeText.font_size):
                self._font_size_combo.handler_block(self._font_size_changed_id)
                self._font_size_combo.set_active(i)
                self._font_size_combo.handler_unblock(self._font_size_changed_id)
                break;
        
        # font seleccionada
        font_family = globeText.font_type
        font_index = -1

        # search for the font name in our font list
        for i, f in enumerate(self._fonts):
            if f == font_family:
                font_index = i
                break;

        # if we don't know this font yet, then add it (temporary) to the list
        if font_index == -1:
            logger.debug('Font not found in font list: %s', font_family)
            if not self._has_custom_fonts:
                # add a separator to seperate the non-available fonts from
                # the available ones
                self._fonts.append('') # ugly
                self._font_combo.append_separator()
                self._has_custom_fonts = True
            # add the new font
            self._fonts.append(font_family)
            self._font_combo.append_item(0, font_family, None)
            # see how many fonts we have now, so we can select the last one
            model = self._font_combo.get_model()
            num_children = model.iter_n_children(None)
            logger.debug('Number of fonts in the list: %d', num_children)
            font_index = num_children-1

        # activate the found font
        if (font_index > -1):
            self._font_combo.handler_block(self._fonts_changed_id)
            self._font_combo.set_active(font_index)
            self._font_combo.handler_unblock(self._fonts_changed_id)


