from gi.repository import Gtk

class ToolButton(Gtk.ToolButton):
    def __init__(self, icon_name=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)

    def set_tooltip(self, text):
        self.set_tooltip_text(text)

    def set_named_icon(self, icon_name):
        self.set_icon_name(icon_name)

    def create_palette(self):
        return None
