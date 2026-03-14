# sugar3_mock/activity/__init__.py
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

_ACTIVITY_ROOT = os.path.join(GLib.get_user_data_dir(), 'speak-ai-local')

class Activity(Gtk.Window):
    """
    Minimal Sugar Activity stub.
    Behaves as a plain GTK Window so SpeakActivity can inherit from it
    and still call set_canvas(), get_toolbar_box() etc.
    """
    def __init__(self, handle=None):
        Gtk.Window.__init__(self)
        self.set_title('Speak AI (local)')
        self.set_default_size(1200, 800)
        self.connect('destroy', Gtk.main_quit)

        # Root vbox: toolbar area on top, canvas below
        self._root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        Gtk.Window.add(self, self._root_box)

        self._toolbar_box = None
        self._canvas = None

        os.makedirs(_ACTIVITY_ROOT, exist_ok=True)

    # --- Sugar Activity API stubs ---
    def set_canvas(self, widget):
        if self._canvas is not None:
            self._root_box.remove(self._canvas)
        self._canvas = widget
        self._root_box.pack_start(widget, True, True, 0)

    def get_toolbar_box(self):
        return self._toolbar_box

    def set_toolbar_box(self, toolbar_box):
        if self._toolbar_box is not None:
            self._root_box.remove(self._toolbar_box)
        self._toolbar_box = toolbar_box
        self._root_box.pack_start(toolbar_box, False, False, 0)
        self._root_box.reorder_child(toolbar_box, 0)

    def read_file(self, file_path):
        pass

    def write_file(self, file_path):
        pass

    def get_activity_root(self):
        return _ACTIVITY_ROOT

    def share(self, private=False):
        pass

    def _share_cb(self, ps, error_seq):
        pass

    # Handle object (passed by Sugar, we stub it)
    class _Handle:
        activity_id = 'local-dev-0001'
        object_id   = None
        invited     = False
        uri         = None

    handle = _Handle()