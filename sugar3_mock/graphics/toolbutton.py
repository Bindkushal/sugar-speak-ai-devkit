from gi.repository import Gtk

class _MockPalette:
    def set_primary_text(self, text): pass
    def get_primary_text(self): return ""
    def set_content(self, widget): pass
    def set_secondary_text(self, text): pass
    def set_invoker(self, invoker): pass
    def popup(self): pass
    def popdown(self): pass

class ToolButton(Gtk.ToolButton):
    def __init__(self, icon_name=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)
        self._palette = _MockPalette()

    def set_tooltip(self, text):
        self.set_tooltip_text(text)

    def set_named_icon(self, icon_name):
        self.set_icon_name(icon_name)

    def get_palette(self):
        return self._palette

    def create_palette(self):
        return self._palette
