# sugar3_mock/activity/widgets.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ActivityToolbarButton(Gtk.ToolButton):
    """Stub for the Sugar activity toolbar button (title + share etc.)."""
    def __init__(self, activity=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        self.set_label('Activity')
        self._activity = activity

class StopButton(Gtk.ToolButton):
    """Stub stop button - quits GTK main loop when clicked."""
    def __init__(self, activity=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        self.set_icon_name('process-stop')
        self.set_tooltip_text('Stop')
        self.connect('clicked', lambda _: Gtk.main_quit())