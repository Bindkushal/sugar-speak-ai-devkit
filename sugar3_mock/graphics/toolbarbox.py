# sugar3_mock/graphics/toolbarbox.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ToolbarBox(Gtk.Box):
    """Stub for sugar3 ToolbarBox - wraps a plain Gtk.Toolbar."""
    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.toolbar = Gtk.Toolbar()
        self.pack_start(self.toolbar, False, False, 0)

class ToolbarButton(Gtk.ToolButton):
    """Stub for sugar3 ToolbarButton (expandable toolbar button)."""
    def __init__(self, page=None, icon_name=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)
        self._page = page or Gtk.Box()

    def get_page(self):
        return self._page