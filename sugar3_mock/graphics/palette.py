from gi.repository import Gtk, GObject

class Invoker(GObject.GObject):
    def __init__(self):
        GObject.GObject.__init__(self)
    def attach(self, widget): pass
    def detach(self): pass

class Palette(Gtk.Popover):
    def __init__(self, label=None, primary_text=None, **kwargs):
        Gtk.Popover.__init__(self)
        self._label = label or primary_text or ''
    def set_primary_text(self, text): self._label = text
    def get_primary_text(self): return self._label
    def set_content(self, widget): pass
    def set_secondary_text(self, text): pass
    def set_invoker(self, invoker): pass
    def popup(self, *args, **kwargs): pass
    def popdown(self, *args, **kwargs): pass

class MouseSpeedDetector(GObject.GObject):
    __gsignals__ = {
        'motion-slow': (GObject.SIGNAL_RUN_FIRST, None, []),
        'motion-fast': (GObject.SIGNAL_RUN_FIRST, None, []),
    }
    def __init__(self, delay, thresh):
        GObject.GObject.__init__(self)
    def start(self): pass
    def stop(self): pass
