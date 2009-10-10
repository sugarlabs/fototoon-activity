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

    def __init__(self, pagina):

        gtk.Toolbar.__init__(self)

        self._pagina = pagina

        # agregar cuadro
        self.b_add_photo = ToolButton('add-photo')
        self.b_add_photo.connect('clicked', self.add_photo)
        self.insert(self.b_add_photo, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)

        # agrega globo
        self.b_agregar = ToolButton('add-globe')
        self.b_agregar.connect('clicked', self.agrega_gnormal)
        self.insert(self.b_agregar, -1)
    
        #agrega nube
        self.b_agregar = ToolButton('add-nube')
        self.b_agregar.connect('clicked', self.agrega_gpensar)
        self.insert(self.b_agregar, -1)
    
        # agrega susurro
        self.b_agregar = ToolButton('add-susurro')
        self.b_agregar.connect('clicked', self.agrega_gdespacio)
        self.insert(self.b_agregar, -1)
    
        # agrega grito
        self.b_agregar = ToolButton('add-grito')
        self.b_agregar.connect('clicked', self.agrega_ggrito)
        self.insert(self.b_agregar, -1)
    
        # agrega caja
        self.b_agregar = ToolButton('add-box')
        self.b_agregar.connect('clicked', self.agrega_grect)
        self.insert(self.b_agregar, -1)
    
        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)

        # girar
        self.b_girar = ToolButton('turn')
        self.b_girar.connect('clicked', self.girar)
        self.insert(self.b_girar, -1)

        # borrar
        self.b_borrar = ToolButton('gtk-delete')
        self.b_borrar.connect('clicked', self.borrar)
        self.insert(self.b_borrar, -1)


    def add_photo(self, boton):
        self._pagina.add_photo()

    def agrega_gnormal(self, boton):
        self._pagina.get_cuadro_activo().add_globo(60, 60)

    def agrega_gnormal(self, boton):
        self._pagina.get_cuadro_activo().add_globo(60, 60)
    
    def agrega_gpensar(self, boton):
        self._pagina.get_cuadro_activo().add_nube(60, 60)
    
    def agrega_gdespacio(self, boton):
        self._pagina.get_cuadro_activo().add_globo(60, 60,gmodo="despacio")
    
    def agrega_ggrito(self, boton):
        self._pagina.get_cuadro_activo().add_grito(60, 60)
    
    def agrega_grect(self, boton):
        self._pagina.get_cuadro_activo().add_rectangulo(60, 60)
    
    def agrega_imagen(self, boton):
        self._pagina.get_cuadro_activo().add_imagen(60, 60)

    def girar(self, boton):
        print "girando"
        #veo cual es el globo seleccionado y o giro
        cuadro = self._pagina.get_cuadro_activo()
        if (cuadro.globo_activo != None):
            print "globo activo",
            if (cuadro.globo_activo.direccion == globos.DIR_ABAJO):
                cuadro.globo_activo.direccion = globos.DIR_IZQ        

            elif (cuadro.globo_activo.direccion == globos.DIR_IZQ):
                cuadro.globo_activo.direccion = globos.DIR_ARRIBA        

            elif (cuadro.globo_activo.direccion == globos.DIR_ARRIBA):
                cuadro.globo_activo.direccion = globos.DIR_DER        

            elif (cuadro.globo_activo.direccion == globos.DIR_DER):
                cuadro.globo_activo.direccion = globos.DIR_ABAJO        
            cuadro.globo_activo.punto[0],cuadro.globo_activo.punto[1] = cuadro.globo_activo.punto[1],cuadro.globo_activo.punto[0]

            cuadro.queue_draw()

    def borrar(self, boton):
        print "borrando"
        cuadro = self._pagina.get_cuadro_activo()
        if (cuadro.globo_activo != None):
            print "borrando globo"
            cuadro.globos.remove(cuadro.globo_activo)
            cuadro.globo_activo = None
            cuadro.queue_draw()
        # Borrar un cuadro es mas complicado
        """
        else:
            print "borrando cuadro"
            self.pagina.cuadros.remove(cuadro)
            if (len(self.pagina.cuadros) > 0):
                print "seteo el primero como activo"
                self.pagina.set_cuadro_activo(self.pagina.cuadros[0])
                for cu in self.pagina.cuadros:
                    print "redibujo"
                    cu.queue_draw()
            else:
                self.pagina._cuadro_activo = None
        """



class TextToolbar(gtk.Toolbar):

    def __init__(self, pagina):
        self._colorseldlg = None

        gtk.Toolbar.__init__(self)

        self._pagina = pagina

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
        self._font_sizes = ['8', '9', '10', '11', '12', '14', '16', '20', '22', '24', '26', '28', '36', '48', '72']
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

    def setToggleButtonState(self,button,b,id):
        button.handler_block(id)
        button.set_active(b)
        button.handler_unblock(id)

    def _bold_cb(self, button):
        globo_activo = self._pagina.get_globo_activo()
        if (globo_activo != None):
            globo_activo.texto.bold = not globo_activo.texto.bold
            self._pagina.get_cuadro_activo().queue_draw()    

    def _italic_cb(self, button):
        globo_activo = self._pagina.get_globo_activo()
        if (globo_activo != None):
            globo_activo.texto.italic = not globo_activo.texto.italic
            self._pagina.get_cuadro_activo().queue_draw()    

    def _text_color_cb(self, button):
        globo_activo = self._pagina.get_globo_activo()
        if (globo_activo != None):
            newcolor = self._text_color.get_color()
            texto = globo_activo.texto
            texto.color_r,texto.color_g,texto.color_b = newcolor.red,newcolor.green,newcolor.blue
            self._pagina.get_cuadro_activo().queue_draw()    


    def _font_size_changed_cb(self, combobox):
        if self._font_size_combo.get_active() != -1:
            size = int(self._font_sizes[self._font_size_combo.get_active()])
            logger.debug('Setting font size: %d', size)
            globo_activo = self._pagina.get_globo_activo()
            if (globo_activo != None):
                globo_activo.texto.font_size = size
                globo_activo.texto.alto_renglon = size
                self._pagina.get_cuadro_activo().queue_draw()    

    def _font_changed_cb(self, combobox):
        if self._font_combo.get_active() != -1:
            logger.debug('Setting font name: %s', self._fonts[self._font_combo.get_active()])
            globo_activo = self._pagina.get_globo_activo()
            if (globo_activo != None):
                globo_activo.texto.font_type = self._fonts[self._font_combo.get_active()]
                self._pagina.get_cuadro_activo().queue_draw()    
            



	"""
	Estos son los metodos para setear los contrles de la barra en base a el texto del globo
	como el globo va a tener un solo font seleccionado, voy a hacer un solo metodo

	"""


    def _isBold_cb(self, abi, b):
        self.setToggleButtonState(self._bold,b,self._bold_id)

    def _isItalic_cb(self, abi, b):
        self.setToggleButtonState(self._italic, b, self._italic_id)

    def _isUnderline_cb(self, abi, b):
        self.setToggleButtonState(self._underline, b, self._underline_id)

    def _color_cb(self, abi, r, g, b):
        self._text_color.set_color(gtk.gdk.Color(r * 256, g * 256, b * 256))


    def _font_size_cb(self, abi, size):
        for i, s in enumerate(self._font_sizes):
            if int(s) == int(size):
                self._font_size_combo.handler_block(self._font_size_changed_id)
                self._font_size_combo.set_active(i)
                self._font_size_combo.handler_unblock(self._font_size_changed_id)
                break;


    def _font_family_cb(self, abi, font_family):
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




"""
class ImageToolbar(gtk.Toolbar):
    def __init__(self, toolbox, abiword_canvas, parent):
        gtk.Toolbar.__init__(self)

        self._toolbox = toolbox
        self._abiword_canvas = abiword_canvas
        self._parent = parent

        self._image = ToolButton('insert-image')
        self._image.set_tooltip(_('Insert Image'))
        self._image_id = self._image.connect('clicked', self._image_cb)
        self.insert(self._image, -1)
        self._image.show()

        self._abiword_canvas.connect('image-selected', self._image_selected_cb)

    def _image_cb(self, button):
        chooser = ObjectChooser(_('Choose image'), self._parent,
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        try:
            result = chooser.run()
            if result == gtk.RESPONSE_ACCEPT:
                logging.debug('ObjectChooser: %r' % chooser.get_selected_object())
                jobject = chooser.get_selected_object()
                if jobject and jobject.file_path:
                    self._abiword_canvas.insert_image(jobject.file_path, True)
        finally:
            chooser.destroy()
            del chooser
 
    def _image_selected_cb(self, abi, b):
        if b:
            self._toolbox.set_current_toolbar(TOOLBAR_IMAGE)
            self._abiword_canvas.grab_focus() # hack: bad toolbox, bad!

class TableToolbar(gtk.Toolbar):
    def __init__(self, toolbox, abiword_canvas):
        gtk.Toolbar.__init__(self)

        self._toolbox = toolbox
        self._abiword_canvas = abiword_canvas

        self._table = abiword.TableCreator()
        self._table.set_labels(_('Table'), _('Cancel'))
        self._table_id = self._table.connect('selected', self._table_cb)
        self._table.show()
        tool_item = gtk.ToolItem()
        tool_item.add(self._table)
        self.insert(tool_item, -1)
        tool_item.show_all()

        self._table_rows_after = ToolButton('row-insert')
        self._table_rows_after.set_tooltip(_('Insert Row'))
        self._table_rows_after_id = self._table_rows_after.connect('clicked', self._table_rows_after_cb)
        self.insert(self._table_rows_after, -1)
        self._table_rows_after.show()

        self._table_delete_rows = ToolButton('row-remove')
        self._table_delete_rows.set_tooltip(_('Delete Row'))
        self._table_delete_rows_id = self._table_delete_rows.connect('clicked', self._table_delete_rows_cb)
        self.insert(self._table_delete_rows, -1)
        self._table_delete_rows.show()

        self._table_cols_after = ToolButton('column-insert')
        self._table_cols_after.set_tooltip(_('Insert Column'))
        self._table_cols_after_id = self._table_cols_after.connect('clicked', self._table_cols_after_cb)
        self.insert(self._table_cols_after, -1)
        self._table_cols_after.show()

        self._table_delete_cols = ToolButton('column-remove')
        self._table_delete_cols.set_tooltip(_('Delete Column'))
        self._table_delete_cols_id = self._table_delete_cols.connect('clicked', self._table_delete_cols_cb)
        self.insert(self._table_delete_cols, -1)
        self._table_delete_cols.show()

        self._abiword_canvas.connect('table-state', self._isTable_cb)

    def _table_cb(self, abi, rows, cols):
        self._abiword_canvas.insert_table(rows,cols)

    def _table_rows_after_cb(self, button):
        self._abiword_canvas.invoke_cmd('insertRowsAfter', '', 0, 0)

    def _table_delete_rows_cb(self, button):
        self._abiword_canvas.invoke_cmd('deleteRows', '', 0, 0)

    def _table_cols_after_cb(self, button):
        self._abiword_canvas.invoke_cmd('insertColsAfter', '', 0, 0)

    def _table_delete_cols_cb(self, button):
        self._abiword_canvas.invoke_cmd('deleteColumns', '', 0, 0)

    def _isTable_cb(self, abi, b):
        self._table_rows_after.set_sensitive(b)
        self._table_delete_rows.set_sensitive(b)
        self._table_cols_after.set_sensitive(b)
        self._table_delete_cols.set_sensitive(b)
        if b:
            self._toolbox.set_current_toolbar(TOOLBAR_TABLE)
            self._abiword_canvas.grab_focus() # hack: bad toolbox, bad!

class FormatToolbar(gtk.Toolbar):
    def __init__(self, toolbox, abiword_canvas):
        gtk.Toolbar.__init__(self)

        self._toolbox = toolbox
        self._abiword_canvas = abiword_canvas

        style_label = gtk.Label(_("Style: "))
        style_label.show()
        tool_item_style_label = gtk.ToolItem()
        tool_item_style_label.add(style_label)
        self.insert(tool_item_style_label, -1)
        tool_item_style_label.show()

        self._has_custom_styles = False

        self._style_combo = ComboBox()
        self._styles = [['Heading 1',_('Heading 1')], 
            ['Heading 2',_('Heading 2')], 
            ['Heading 3',_('Heading 3')],
            ['Heading 4',_('Heading 4')],
            ['Bullet List',_('Bullet List')],
            ['Dashed List',_('Dashed List')],
            ['Numbered List',_('Numbered List')],
            ['Lower Case List',_('Lower Case List')],
            ['Upper Case List',_('Upper Case List')],
            ['Block Text',_('Block Text')],
            ['Normal',_('Normal')],
            ['Plain Text',_('Plain Text')]]
        self._style_changed_id = self._style_combo.connect('changed', self._style_changed_cb)
        for i, s in enumerate(self._styles):
            self._style_combo.append_item(i, s[1], None)
            if s[0] == 'Normal':
                self._style_combo.set_active(i)
        tool_item = ToolComboBox(self._style_combo)
        self.insert(tool_item, -1);
        tool_item.show()

        self._abiword_canvas.connect('style-name', self._style_cb)

    def _style_cb(self, abi, style_name):
        style_index = -1
        for i, s in enumerate(self._styles):
            if s[0] == style_name:
                style_index = i
                break;

        # if we don't know this style yet, then add it (temporary) to the list
        if style_index == -1:
            logger.debug('Style not found in style list: %s', style_name)
            if not self._has_custom_styles:
                # add a separator to seperate the non-available styles from
                # the available ones
                self._styles.append(['','']) # ugly
                self._style_combo.append_separator()
                self._has_custom_styles = True
            # add the new style
            self._styles.append([style_name, style_name])
            self._style_combo.append_item(0, style_name, None)
            # see how many styles we have now, so we can select the last one
            model = self._style_combo.get_model()
            num_children = model.iter_n_children(None)
            logger.debug('Number of styles in the list: %d', num_children)
            style_index = num_children-1

        if style_index > -1:
            self._style_combo.handler_block(self._style_changed_id)
            self._style_combo.set_active(style_index)
            self._style_combo.handler_unblock(self._style_changed_id)

    def _style_changed_cb(self, combobox):
        if self._style_combo.get_active() != -1:
            logger.debug('Setting style name: %s', self._styles[self._style_combo.get_active()][0])
            self._abiword_canvas.set_style(self._styles[self._style_combo.get_active()][0])

class ViewToolbar(gtk.Toolbar):
    def __init__(self, abiword_canvas):
        gtk.Toolbar.__init__(self)

        self._abiword_canvas = abiword_canvas
        self._zoom_percentage = 0;

        self._zoom_out = ToolButton('zoom-out')
        self._zoom_out.set_tooltip(_('Zoom Out'))
        self._zoom_out_id = self._zoom_out.connect('clicked', self._zoom_out_cb)
        self.insert(self._zoom_out, -1)
        self._zoom_out.show()

        self._zoom_in = ToolButton('zoom-in')
        self._zoom_in.set_tooltip(_('Zoom In'))
        self._zoom_in_id = self._zoom_in.connect('clicked', self._zoom_in_cb)
        self.insert(self._zoom_in, -1)
        self._zoom_in.show()

        # TODO: fix the initial value
        self._zoom_spin_adj = gtk.Adjustment(0, 25, 400, 25, 50, 0)
        self._zoom_spin = gtk.SpinButton(self._zoom_spin_adj, 0, 0)
        self._zoom_spin_id = self._zoom_spin.connect('value-changed', self._zoom_spin_cb)
        self._zoom_spin.set_numeric(True)
        self._zoom_spin.show()
        tool_item_zoom = gtk.ToolItem()
        tool_item_zoom.add(self._zoom_spin)
        self.insert(tool_item_zoom, -1)
        tool_item_zoom.show()

        zoom_perc_label = gtk.Label(_("%"))
        zoom_perc_label.show()
        tool_item_zoom_perc_label = gtk.ToolItem()
        tool_item_zoom_perc_label.add(zoom_perc_label)
        self.insert(tool_item_zoom_perc_label, -1)
        tool_item_zoom_perc_label.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        separator.show()
        self.insert(separator, -1)

        page_label = gtk.Label(_("Page: "))
        page_label.show()
        tool_item_page_label = gtk.ToolItem()
        tool_item_page_label.add(page_label)
        self.insert(tool_item_page_label, -1)
        tool_item_page_label.show()

        self._page_spin_adj = gtk.Adjustment(0, 1, 0, 1, 1, 0)
        self._page_spin = gtk.SpinButton(self._page_spin_adj, 0, 0)
        self._page_spin_id = self._page_spin.connect('value-changed', self._page_spin_cb)
        self._page_spin.set_numeric(True)
        self._page_spin.show()
        tool_item_page = gtk.ToolItem()
        tool_item_page.add(self._page_spin)
        self.insert(tool_item_page, -1)
        tool_item_page.show()

        self._total_page_label = gtk.Label(" / 0")
        self._total_page_label.show()
        tool_item = gtk.ToolItem()
        tool_item.add(self._total_page_label)
        self.insert(tool_item, -1)
        tool_item.show()

        self._abiword_canvas.connect("page-count", self._page_count_cb)
        self._abiword_canvas.connect("current-page", self._current_page_cb)
        self._abiword_canvas.connect("zoom", self._zoom_cb)

    def set_zoom_percentage(self, zoom):
        self._zoom_percentage = zoom
        self._abiword_canvas.set_zoom_percentage(self._zoom_percentage)
        
    def _zoom_cb(self, canvas, zoom):
        self._zoom_spin.handler_block(self._zoom_spin_id)
        try:
            self._zoom_spin.set_value(zoom)
        finally:
            self._zoom_spin.handler_unblock(self._zoom_spin_id)

    def _zoom_out_cb(self, button):
        if self._zoom_percentage == 0:
            self._zoom_percentage = self._abiword_canvas.get_zoom_percentage()
        if self._zoom_percentage >= 50:
            self.set_zoom_percentage(self._zoom_percentage - 25)

    def _zoom_in_cb(self, button):
        if self._zoom_percentage == 0:
            self._zoom_percentage = self._abiword_canvas.get_zoom_percentage()
        if self._zoom_percentage <= 375:
            self.set_zoom_percentage(self._zoom_percentage + 25)

    def _zoom_spin_cb(self, button):
        self._zoom_percentage = self._zoom_spin.get_value_as_int()
        self._abiword_canvas.set_zoom_percentage(self._zoom_percentage)

    def _page_spin_cb(self, button):
        self._page_num = self._page_spin.get_value_as_int()
        self._abiword_canvas.set_current_page(self._page_num)

    def _page_count_cb(self, canvas, count):
        current_page = canvas.get_current_page_num()
        self._page_spin_adj.set_all(current_page, 1, count, 1, 1, 0)
        self._total_page_label.props.label = \
            ' / ' + str(count)

    def _current_page_cb(self, canvas, num):
        self._page_spin.handler_block(self._page_spin_id)
        try:
            self._page_spin.set_value(num)
        finally:
            self._page_spin.handler_unblock(self._page_spin_id)

"""
