from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository.GdkPixbuf import Pixbuf

from sugar3.graphics import style
from sugar3.graphics.toolbutton import ToolButton


class ReorderView(Gtk.Window):
    def __init__(self, activity):
        GObject.GObject.__init__(self)
        self.set_border_width(style.LINE_WIDTH)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_decorated(False)
        self.set_resizable(False)
        width = Gdk.Screen.width() - style.GRID_CELL_SIZE * 2
        height = Gdk.Screen.height() - style.GRID_CELL_SIZE * 2
        self.set_size_request(width, height)
        self.set_default_size(width, height)

        self.toolbar = Gtk.Toolbar()

        icon = ToolButton('thumbs-view')
        self.toolbar.insert(icon, -1)

        label = Gtk.Label()
        title = _('Drag the images to reorder')
        label.set_markup('<b>%s</b>' % title)
        label.set_alignment(0, 0.5)
        tool_item = Gtk.ToolItem()
        tool_item.set_expand(True)
        tool_item.add(label)
        tool_item.show_all()
        self.toolbar.insert(tool_item, -1)

        self.stop = ToolButton(icon_name='dialog-cancel')
        self.stop.set_tooltip(_('Cancel'))
        self.stop.connect('clicked', self.__stop_clicked_cb)
        self.toolbar.insert(self.stop, -1)
        self.stop.show()

        self.confirm = ToolButton(icon_name='dialog-ok')
        self.confirm.set_tooltip(_('Done'))
        self.confirm.connect('clicked', self.__ok_clicked_cb)
        self.toolbar.insert(self.confirm, -1)
        self.confirm.show()

        self.scrollwin = ReorderObjects(activity)
        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.toolbar, False, False, 0)
        self.vbox.pack_start(self.scrollwin, True, True, 0)
        self.add(self.vbox)
        self.scrollwin.show()

    def __stop_clicked_cb(self, button):
        self.destroy()

    def __ok_clicked_cb(self, button):
        self.scrollwin.reorder_comicboxs()
        self.scrollwin.display_comicboxs()
        self.destroy()


class ReorderObjects(Gtk.ScrolledWindow):
    def __init__(self, activity):
        GObject.GObject.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.activity = activity
        self.comicboxes = self.activity.page.boxs

        self.liststore = Gtk.ListStore(Pixbuf)
        self.iconview = Gtk.IconView.new()
        #self.iconview.set_columns(2)
        self.iconview.set_property('item-width', 200)
        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_reorderable(True)

        for comicbox in self.comicboxes[1:]:
            self.liststore.append([comicbox.get_thumbnail()])

        self.add(self.iconview)

    def reorder_comicboxs(self):
        sorted_list = []
        for row in self.liststore:
            for comicbox in self.comicboxes[1:]:
                if row[0] is comicbox.thumbnail:
                    self.activity.page.table.remove(comicbox)
                    sorted_list.append(comicbox)
                    break
        sorted_list.insert(0, self.comicboxes[0])
        self.comicboxes = sorted_list
        self.activity.page.boxs = self.comicboxes

    def display_comicboxs(self):
        for i in range(0, len(self.comicboxes[1:])):
            reng = int(i / 2)
            column = i - (reng * 2)
            self.activity.page.table.attach(
                self.comicboxes[i+1], column, column + 1, reng, reng + 1)
