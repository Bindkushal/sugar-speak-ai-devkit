from gi.repository import Gtk

class RadioToolButton(Gtk.RadioToolButton):
    def __init__(self, icon_name=None, group=None, **kwargs):
        if group is not None:
            Gtk.RadioToolButton.__init__(self, group=group)
        else:
            Gtk.RadioToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)

    def set_tooltip(self, text):
        self.set_tooltip_text(text)

    def set_named_icon(self, icon_name):
        self.set_icon_name(icon_name)
