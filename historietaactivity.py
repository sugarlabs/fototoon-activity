# -*- coding: UTF-8 -*-

import os
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import cairo

import globos
import persistencia

from sugar3.activity import activity
from gettext import gettext as _

from sugar3.graphics.toolbarbox import ToolbarBox, ToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.toolbutton import ToolButton
from toolbar import TextToolbar
from toolbar import GlobesManager

from slideview import SlideView

import time
from sugar3.datastore import datastore
from sugar3 import profile
from sugar3.graphics import style
from sugar3.graphics.alert import Alert
from sugar3.graphics.icon import Icon
import dbus
import logging
import inspect


class HistorietaActivity(activity.Activity):

    _EXPORT_FORMATS = [['image/png', _('Save as Image'), _('PNG'), ""]]

    def __init__(self, handle):
        print "INICIALIZANDO FOTOTOON"
        activity.Activity.__init__(self, handle)
        self.set_title('FotoToon')

        self._max_participants = 1

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        activity_toolbar = activity_button.page
        toolbar_box.toolbar.insert(activity_button, 0)

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)

        view_subtoolbar = ToolbarButton()
        view_toolbar = Gtk.Toolbar()
        view_subtoolbar.props.page = view_toolbar
        view_subtoolbar.props.icon_name = 'toolbar-view'
        view_subtoolbar.label = _('View')
        toolbar_box.toolbar.insert(view_subtoolbar, -1)

        slideview_btn = ToggleToolButton('slideshow')
        slideview_btn.set_tooltip(_('Slideshow'))
        slideview_btn.set_active(False)
        view_toolbar.insert(slideview_btn, -1)
        slideview_btn.show()

        fullscreen_btn = ToolButton('view-fullscreen')
        fullscreen_btn.set_tooltip(_('Fullscreen'))
        fullscreen_btn.props.accelerator = '<Alt>Return'
        fullscreen_btn.connect('clicked', lambda w: self.fullscreen())
        view_toolbar.insert(fullscreen_btn, -1)
        fullscreen_btn.show()

        #self._add_toolbar_buttons(toolbar_box)
        self.set_toolbar_box(toolbar_box)

        toolbar = toolbar_box.toolbar

        self.page = Page()

        self.globes_manager = GlobesManager(toolbar, self.page, self)

        # fonts
        text_button = ToolbarButton()
        text_button.props.page = TextToolbar(self.page)
        text_button.props.icon_name = 'format-text-size'
        text_button.props.label = _('Text')
        slideview_btn.connect('clicked', self._switch_view_mode, text_button)
        toolbar_box.toolbar.insert(text_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)

        toolbar_box.toolbar.insert(separator, -1)

        stop = StopButton(self)
        toolbar_box.toolbar.insert(stop, -1)

        toolbar_box.show_all()

        # add export button

        separator_2 = Gtk.SeparatorToolItem()
        separator_2.show()
        activity_toolbar.insert(separator_2, -1)

        self.bt_save_as_image = ToolButton()
        self.bt_save_as_image.props.icon_name = 'save-as-image'
        self.bt_save_as_image.connect('clicked', self.write_image)
        self.bt_save_as_image.set_tooltip(_('Save as Image'))
        activity_toolbar.insert(self.bt_save_as_image, -1)
        self.bt_save_as_image.show()

        activity_button.page.title.connect("focus-in-event",
            self.on_title)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scrolled.add_with_viewport(self.page)
        scrolled.show_all()

        self._slideview = SlideView(self)
        self._slideview.show_all()

        self._notebook = Gtk.Notebook()
        self._notebook.set_show_tabs(False)
        self._notebook.append_page(scrolled, Gtk.Label('Fototoon'))
        self._notebook.append_page(self._slideview, Gtk.Label('SlideView'))
        self._notebook.show_all()

        self.set_canvas(self._notebook)
        self.show()
        self.metadata['mime_type'] = 'application/x-fototoon-activity'

        self.page.empty_page = handle.object_id is None
        self._key_press_signal_id = None

        #print "screen witdh " , SCREEN_WIDTH
        #print "page witdh " , self.page.size_request()

    # quiero que al ingresar al titulo se des seleccione el globo seleccionado
    def on_title(self, widget, event):
        print "Ingresando al titulo"
        if (self.page.get_active_box() != None):
            box = self.page.get_active_box()
            self.page.set_active_box(None)
            box.glob_press = False
            box.set_globo_activo(None)
            box.redraw()

            print "Fin de Ingresando al titulo"

    def write_file(self, file_path):
        print "write file path", file_path
        persistence = persistencia.Persistence()
        persistence.write(file_path, self.page)

    def read_file(self, file_path):
        print "read file path", file_path
        persistence = persistencia.Persistence()
        persistence.read(file_path, self.page)

    def write_image(self, button):
        # calculate image size
        image_height, image_width = 0, 0
        posi = 0
        for box in self.page.boxs:
            if posi > 0:
                try:
                    reng = int((posi + 1) / 2)
                    column = (posi + 1) - (reng * 2)
                    #logging.error("reng %d column %d" % (reng, column))
                    if column == 0:
                        image_height = image_height + box.height
                except:
                    pass
            else:
                image_width = box.width
                image_height = image_height + box.height
            # hide the cursor
            for globe in box.globos:
                globo.set_selected(False)

            posi = posi + 1

        #logging.error("image_width %d image_height %d" %
        #    (image_width, image_height))
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
            image_width + 1, image_height + 1)
        ctx = cairo.Context(surface)

        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, image_width + 1, image_height + 1)
        ctx.fill()

        posi = 0
        y_posi = 0
        for box in self.page.boxs:
            #logging.error("posi %d" % (posi))

            if posi > 0:
                try:
                    reng = int((posi + 1) / 2)
                    column = (posi + 1) - (reng * 2)
                    #logging.error("reng %d column %d" % (reng, column))
                    ctx.rectangle(column * box.width, y_posi,
                        (column + 1) * box.width, y_posi + box.height)
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.stroke()
                    ctx.translate(column * box.width, y_posi)
                    box.draw_in_context(ctx)
                    ctx.translate(column * box.width * - 1, y_posi * - 1)
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

        surface.write_to_png(temp_file_name)
        #logging.error("temp file name  %s" % (temp_file_name))

        self.dl_jobject = datastore.create()

        self.dl_jobject.metadata['progress'] = '0'
        self.dl_jobject.metadata['keep'] = '0'
        self.dl_jobject.metadata['buddies'] = ''
        self.dl_jobject.metadata['icon-color'] = \
                profile.get_color().to_string()
        self.dl_jobject.metadata['mime_type'] = 'image/png'

        self.dl_jobject.metadata['title'] = \
            self._jobject.metadata['title'] + " as image"
        self.dl_jobject.metadata['description'] = ""
        self.dl_jobject.metadata['progress'] = '100'
        self.dl_jobject.file_path = temp_file_name

        self.dl_jobject.metadata['preview'] = \
            self._get_preview_image(temp_file_name)

        datastore.write(self.dl_jobject, transfer_ownership=True)
        self._object_id = self.dl_jobject.object_id
        self._show_journal_alert(_('Success'),
                _('A image was created in the Journal'))

    def _show_journal_alert(self, title, msg):
        _stop_alert = Alert()
        _stop_alert.props.title = title
        _stop_alert.props.msg = msg
        _stop_alert.add_button(Gtk.ResponseType.APPLY,
                _('Show in Journal'), Icon(icon_name='zoom-activity'))
        _stop_alert.add_button(Gtk.ResponseType.OK, _('Ok'),
                Icon(icon_name='dialog-ok'))
        # Remove other alerts
        for alert in self._alerts:
            self.remove_alert(alert)

        self.add_alert(_stop_alert)
        _stop_alert.connect('response', self.__stop_response_cb)
        _stop_alert.show_all()

    def __stop_response_cb(self, alert, response_id):
        if response_id is Gtk.ResponseType.APPLY:
            activity.show_object_in_journal(self._object_id)
        self.remove_alert(alert)

    def _get_preview_image(self, file_name):
        preview_width, preview_height = style.zoom(300), style.zoom(225)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_name)
        width, height = pixbuf.get_width(), pixbuf.get_height()

        scale = 1
        if (width > preview_width) or (height > preview_height):
            scale_x = preview_width / float(width)
            scale_y = preview_height / float(height)
            scale = min(scale_x, scale_y)

        pixbuf2 = GdkPixbuf.Pixbuf(GdkPixbuf.Colorspace.RGB, \
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
                            GdkPixbuf.InterpType.BILINEAR)

        preview_data = []

        def save_func(buf, data):
            data.append(buf)

        pixbuf2.save_to_callback(save_func, 'png', user_data=preview_data)
        preview_data = ''.join(preview_data)
        return dbus.ByteArray(preview_data)

    def _switch_view_mode(self, widget, textbutton):
        if widget.get_active():
            self._notebook.set_current_page(1)
            self._slideview.set_boxes(self.page.boxs)
            self._slideview.set_current_box(0)
            #disable edition mode in the globes
            for box in self.page.boxs:
                box.set_globo_activo(None)

            self._key_press_signal_id = self.connect('key_press_event',
                    self._slideview.key_press_cb)
        else:
            self._notebook.set_current_page(0)
            if self._key_press_signal_id is not None:
                self.disconnect(self._key_press_signal_id)
        self.globes_manager.set_buttons_sensitive(not widget.get_active())
        textbutton.set_sensitive(not widget.get_active())


DEF_SPACING = 6
DEF_WIDTH = 4

SCREEN_HEIGHT = Gdk.Screen.height()
SCREEN_WIDTH = Gdk.Screen.width()
BOX_HEIGHT = 450


class Page(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self, False, 0)

        self._internal_box = Gtk.VBox()

        self.set_homogeneous(False)

        self.boxs = []
        self._active_box = None
        self.selected_font_name = globos.DEFAULT_FONT

        logging.error('SCREEN WIDTH %d DEF_SPACING %d', SCREEN_WIDTH,
                DEF_SPACING)

        # Agrego cuadro titulo
        self.title_box = ComicBox(self, None, 0)
        self.title_box.set_size_request(SCREEN_WIDTH, 100)
        self.title_box.width, self.title_box.height = SCREEN_WIDTH, 100
        self._internal_box.pack_start(self.title_box, False, False, 0)
        self.set_active_box(self.title_box)
        self.boxs.append(self.title_box)

        # Agrego tabla para las fotos
        self.table = Gtk.Table(10, 2, True)
        self.table.set_homogeneous(True)
        self.table.set_row_spacings(DEF_SPACING)
        self.table.set_col_spacings(DEF_SPACING)
        self._internal_box.pack_start(self.table, False, False, 0)
        self.pack_start(self._internal_box, True, True, 0)
        self.show_all()

    def add_box_from_journal_image(self, image_file_name):
        posi = len(self.boxs) - 1
        num_foto = posi - (posi / 4) * 4
        box = ComicBox(self, image_file_name, posi + 1)
        reng = int(posi / 2)
        column = posi - (reng * 2)

        self.table.attach(box, column, column + 1, reng, reng + 1)
        self.set_active_box(box)
        self.boxs.append(box)

    def set_active_box(self, box):
        if self._active_box == box:
            return
        box_anterior = None
        if (self._active_box != None):
            box_anterior = self._active_box
        self._active_box = box
        if (box != None):
            box.redraw()
        if (box_anterior != None):
            for g in box_anterior.globos:
                g.set_selected(False)
            box_anterior.redraw()

    def get_active_box(self):
        return self._active_box

    def get_globo_activo(self):
        box = self.get_active_box()
        if box != None:
            if (box.get_globo_activo() != None):
                return box.get_globo_activo()
        return None


class ComicBox(Gtk.EventBox):

    def __init__(self, page, image_file_name, posi):
        print ('Cuadro INIT')
        Gtk.EventBox.__init__(self)

        self._page = page
        self.modify_bg(Gtk.StateType.NORMAL,
                style.COLOR_WHITE.get_gdk_color())

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self._drawingarea = Gtk.DrawingArea()
        self.fixed.put(self._drawingarea, 0, 0)

        self.textviewbox = Gtk.VBox()
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_justification(Gtk.Justification.CENTER)
        self.textview.modify_bg(Gtk.StateType.NORMAL,
                style.COLOR_TEXT_FIELD_GREY.get_gdk_color())

        self.fixed.put(self.textviewbox, 0, 0)
        self.textviewbox.pack_start(self.textview, True, False, 0)

        #se agregan los eventos de pulsacion y movimiento del raton
        self._drawingarea.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.BUTTON_MOTION_MASK)

        #self.globos es una lista que contiene los globos de ese cuadro
        self.globos = []
        self.posi = posi

        #self.pixbuf = pixbuf
        self.glob_press = False
        self.is_dimension = False
        self.is_punto = False
        self.image_name = ''
        self.image = None
        self.image_saved = False
        self.title_globe = None

        self.width = (int)(SCREEN_WIDTH - DEF_SPACING) / 2
        self.height = BOX_HEIGHT

        if image_file_name is not None:
            logging.error('seting image_name %s', image_file_name)
            self.image_name = image_file_name

        self._globo_activo = None

        self._drawingarea.connect("draw", self.draw_cb)
        self.connect("button_press_event", self.pressing)
        self.connect("motion_notify_event", self.mouse_move)
        self.connect("motion_notify_event", self.moving)
        self.connect("button_release_event", self.releassing)
        self.redraw()

        def size_allocate(widget, allocation):
            self.fixed.set_size_request(self.width, self.height)
            self._drawingarea.set_size_request(self.width, self.height)

        self.connect('size_allocate', size_allocate)
        self.set_size_request(self.width, self.height)
        self._drawingarea.set_size_request(self.width, self.height)
        self.fixed.set_size_request(self.width, self.height)
        self.show_all()

    def set_globo_activo(self, globo):
        if globo == None:
            if self._globo_activo != None:
                self._globo_activo.set_selected(False)
        else:
            globo.set_selected(True)
        self._globo_activo = globo
        if (globo != None):
            self._page._text_toolbar.setToolbarState(globo.texto)

    def redraw(self):
        self._drawingarea.queue_draw()

    def get_globo_activo(self):
        return self._globo_activo

    def add_globo(self, xpos, ypos, gmodo="normal", \
                gdireccion=globos.DIR_ABAJO, font_name=globos.DEFAULT_FONT):
        #agrega un globo al cuadro
        globo = globos.Globo(self, x=xpos, y=ypos, modo=gmodo,
                             direccion=gdireccion, font_name=font_name)
        self.globos.append(globo)
        self._globo_activo = globo
        self.redraw()

    def add_rectangulo(self, xpos, ypos, font_name=globos.DEFAULT_FONT):
        #agrega un cuadro de texto al cuadro
        self.globos.append(globos.Rectangulo(self, x=xpos, y=ypos,
                font_name=font_name))
        self.redraw()

    def add_nube(self, xpos, ypos, font_name=globos.DEFAULT_FONT):
        #agrega un globo de pensamiento al cuadro
        globo = globos.Nube(self, x=xpos, y=ypos, font_name=font_name)
        self.globos.append(globo)
        self._globo_activo = globo
        self.redraw()

    def add_imagen(self, imagen, xpos, ypos):
        #agrega una imagen al cuadro
        globo = globos.Imagen(self, imagen, x=xpos, y=ypos)
        self.globos.append(globo)
        self._globo_activo = globo
        self.redraw()

    def add_grito(self, xpos, ypos, font_name=globos.DEFAULT_FONT):
        #agrega un globo de grito al cuadro
        globo = globos.Grito(self, x=xpos, y=ypos, font_name=font_name)
        self.globos.append(globo)
        self._globo_activo = globo
        self.redraw()

    def draw_cb(self, widget, context):
        # check if is the title box and is a new page
        if self._page.title_box == self and self._page.empty_page:
            self._page.empty_page = False
            # select title box
            rect = self.get_allocation()
            x = rect.width / 2
            y = rect.height / 2
            self.add_rectangulo(x, y)
            self.title_globe = self.globos[0]
            self.title_globe.texto.set_text(_('Title:'))

        self.draw_in_context(context)
        return False

    def draw_in_context(self, ctx):
        # Dibujamos la foto

        self.image_height = 0

        instance_path = os.path.join(activity.get_activity_root(), \
            'instance')
        if (self.image == None) and (self.image_name != ''):
            # si la imagen no tiene el path viene del archivo
            # de historieta ya grabado,
            # si viene con path, es una imagen que se tomo del journal
            if (not self.image_name.startswith(instance_path)):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(
                    os.path.join(instance_path, self.image_name))
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.image_name)
            width_pxb = pixbuf.get_width()
            height_pxb = pixbuf.get_height()
            scale = (self.width) / (1.0 * width_pxb)
            self.image_height = int(scale * height_pxb)
            self.image = ctx.get_target().create_similar(
                    cairo.CONTENT_COLOR_ALPHA, self.width, self.image_height)

            if (scale != 1):
                # falta tener en cuenta el caso de una imagen
                # que venga del journal y tenga el tamanio justo,
                # es decir con scale = 1
                pixb_scaled = pixbuf.scale_simple(int(self.width),
                    int(self.image_height), GdkPixbuf.InterpType.BILINEAR)
                ct = cairo.Context(self.image)
                Gdk.cairo_set_source_pixbuf(ct, pixb_scaled, 0, 0)
                ct.paint()
                if (not self.image_saved):
                    self.image_saved = True
                    # print instance_path
                    image_file_name = 'image' + str(self.posi) + '.png'
                    self.image.write_to_png(os.path.join(instance_path,
                            image_file_name))
                    # grabamos el nombre de la imagen sin el path
                    self.image_name = image_file_name
            else:
                ct = cairo.Context(self.image)
                Gdk.cairo_set_source_pixbuf(ct, pixbuf, 0, 0)
                ct.paint()
                self.image.flush()

        if self.image is not None:
            ctx.save()
            ctx.rectangle(0, 0, self.width, self.height)
            ctx.clip()
            ctx.set_source_surface(self.image, 0, 0)
            ctx.paint()
            ctx.restore()

        # Dibujamos el recuadro
        ctx.save()
        ctx.set_line_width(DEF_WIDTH)
        ctx.rectangle(0, 0, self.width, self.height)
        if (self._page.get_active_box() == self):
            ctx.set_source_rgb(1, 1, 1)
        else:
            ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()
        ctx.set_source_rgb(0, 0, 0)
        ctx.restore()

        # Por ultimo dibujamos los globos
        self.draw_globos(ctx)

    def draw_globos(self, context):
        if len(self.globos) > 0:
            for g in self.globos:
                g.imprimir(context)

    def pressing(self, widget, event):
        # si no es el cuadro seleccionado actualmente redibujo este
        # y el anterior seleccionado
        if (self._page.get_active_box() != self):
            self._page.set_active_box(self)

        #Verifica si al pulsar el mouse se hizo sobre algun globo
        if self._globo_activo != None:
            if self._globo_activo.is_selec_tam(event.x, event.y) or \
                (self._globo_activo.get_cursor_type(event.x, event.y) != None):
                self.is_dimension = True
            elif self._globo_activo.is_selec_punto(event.x, event.y):
                self.is_punto = True

        if (not self.is_dimension) and not (self.is_punto):
            if self._globo_activo != None:
                #self.glob_press.is_selec(event.x,event.y)
                self._globo_activo.set_selected(False)
                self.glob_press = False

            if self.globos:
                list_aux = self.globos[:]
                list_aux.reverse()
                for i in list_aux:
                    if i.is_selec(event.x, event.y):
                        # i.mover_a(event.x,event.y,self.get_allocation())
                        self.glob_press = True
                        self.set_globo_activo(i)
                        self.redraw()
                        break

    def releassing(self, widget, event):
        #Cuando se deja de pulsar el mouse
        self.glob_press = False
        self.is_dimension = False
        self.is_punto = False

    def mouse_move(self, widget, event):
        if self._globo_activo != None:
            cursor_type = self._globo_activo.get_cursor_type(event.x, event.y)
            cursor = None
            if cursor_type is not None:
                cursor = Gdk.Cursor(cursor_type)
            self.get_window().set_cursor(cursor)

    def moving(self, widget, event):
        if self.is_dimension:
            self._globo_activo.set_dimension(event.x, event.y,
                self.get_allocation())
            self.redraw()
        elif self.is_punto:
            self._globo_activo.mover_punto(event.x, event.y,
                self.get_allocation())
            self.redraw()
        elif self.glob_press:
            self._globo_activo.mover_a(event.x, event.y,
                self.get_allocation())
            self.redraw()

    def move_textview(self, x, y):
        self.fixed.move(self.textviewbox, x, y)
        self.textviewbox.show_all()
