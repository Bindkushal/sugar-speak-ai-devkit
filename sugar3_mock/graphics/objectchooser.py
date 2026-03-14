# sugar3_mock/graphics/objectchooser.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ObjectChooser(Gtk.Dialog):
    """Stub - always returns None (no journal)."""
    RESPONSE_ACCEPT = Gtk.ResponseType.ACCEPT

    def __init__(self, parent=None, what_filter=None):
        Gtk.Dialog.__init__(self, parent=parent)
        self.set_title('Choose Object (stub)')

    def get_selected_object(self):
        return None