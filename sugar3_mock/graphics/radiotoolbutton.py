# sugar3_mock/graphics/radiotoolbutton.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RadioToolButton(Gtk.RadioToolButton):
    """Minimal RadioToolButton stub."""
    def __init__(self, icon_name=None, group=None, **kwargs):
        if group is not None:
            Gtk.RadioToolButton.__init__(self, group=group)
        else:
            Gtk.RadioToolButton.__init__(self)
        if icon_name:
            self.set_icon_name(icon_name)