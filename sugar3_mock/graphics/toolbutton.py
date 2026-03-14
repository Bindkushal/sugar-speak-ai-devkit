# sugar3_mock/graphics/toolbutton.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ToolButton(Gtk.ToolButton):
    """Minimal ToolButton stub - just a plain GTK ToolButton."""
    def __init__(self, icon_name=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)

    def create_palette(self):
        return None