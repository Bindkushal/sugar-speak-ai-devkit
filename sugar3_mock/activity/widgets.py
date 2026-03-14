from gi.repository import Gtk

class ActivityToolbarButton(Gtk.ToolButton):
    def __init__(self, activity=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        self.set_label('Activity')
        self._activity = activity
        self._expanded = False

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded

    def get_page(self):
        return Gtk.Box()

class StopButton(Gtk.ToolButton):
    def __init__(self, activity=None, **kwargs):
        Gtk.ToolButton.__init__(self)
        self.set_icon_name("process-stop")
        self.set_tooltip_text("Stop")
        self.connect("clicked", lambda _: Gtk.main_quit())
