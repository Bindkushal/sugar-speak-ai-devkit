from gi.repository import Gtk

class ToolbarBox(Gtk.Box):
    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.toolbar = Gtk.Toolbar()
        self.pack_start(self.toolbar, False, False, 0)

class ToolbarButton(Gtk.ToolButton):
    def __init__(self, page=None, icon_name=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)
        self._page = page or Gtk.Box()
        self._expanded = False

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded

    def set_tooltip(self, text):
        self.set_tooltip_text(text)

    def get_page(self):
        return self._page
