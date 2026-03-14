from gi.repository import Gtk

class PaletteMenuItem(Gtk.MenuItem):
    def __init__(self, text_label=None, icon_name=None, **kwargs):
        Gtk.MenuItem.__init__(self)
        if text_label:
            self.set_label(text_label)
