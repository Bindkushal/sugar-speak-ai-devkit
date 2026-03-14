# sugar3_mock/activity/activity.py
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GObject

_ACTIVITY_ROOT = os.path.join(GLib.get_user_data_dir(), "speak-ai-local")

def get_activity_root():
    os.makedirs(_ACTIVITY_ROOT, exist_ok=True)
    return _ACTIVITY_ROOT

def get_bundle_path():
    return os.path.dirname(os.path.abspath(__file__))

def show_object_in_journal(object_id):
    pass

class Activity(Gtk.Window):
    __gsignals__ = {
        "shared":     (GObject.SIGNAL_RUN_FIRST, None, []),
        "joined":     (GObject.SIGNAL_RUN_FIRST, None, []),
        "closing":    (GObject.SIGNAL_RUN_FIRST, None, []),
        "save-error": (GObject.SIGNAL_RUN_FIRST, None, [object]),
    }

    def __init__(self, handle=None):
        Gtk.Window.__init__(self)
        self.set_title("Speak AI (local)")
        self.set_resizable(True)
        self.set_default_size(1000, 600)
        self.connect("destroy", Gtk.main_quit)

        self._root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        Gtk.Window.add(self, self._root_box)

        self._toolbar_box = None
        self._canvas = None
        self.shared_activity = None
        self.metadata = {}
        self.handle = type("Handle", (), {
            "activity_id": "local-0001",
            "object_id":   None,
            "invited":     False,
            "uri":         None,
        })()

    def set_canvas(self, widget):
        if self._canvas is not None:
            self._root_box.remove(self._canvas)
        self._canvas = widget
        self._root_box.pack_end(widget, True, True, 0)

    def set_toolbar_box(self, toolbar_box):
        if self._toolbar_box is not None:
            self._root_box.remove(self._toolbar_box)
        self._toolbar_box = toolbar_box
        self._root_box.pack_start(toolbar_box, False, False, 0)
        self._root_box.reorder_child(toolbar_box, 0)

    def get_toolbar_box(self):
        return self._toolbar_box

    @property
    def toolbar_box(self):
        return self._toolbar_box

    @toolbar_box.setter
    def toolbar_box(self, toolbar_box):
        self.set_toolbar_box(toolbar_box)

    def read_file(self, file_path): pass
    def write_file(self, file_path): pass
    def get_activity_root(self): return _ACTIVITY_ROOT
    def share(self, private=False): pass
