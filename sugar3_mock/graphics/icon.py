from gi.repository import Gtk

class Icon(Gtk.Image):
    def __init__(self, icon_name=None, pixel_size=None, **kwargs):
        Gtk.Image.__init__(self)
        if icon_name:
            self.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        if pixel_size:
            self.set_pixel_size(pixel_size)
