import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

GRID_CELL_SIZE            = 55
DEFAULT_PADDING           = 6
DEFAULT_SPACING           = 4
STANDARD_ICON_SIZE        = 55
SMALL_ICON_SIZE           = 33
LARGE_ICON_SIZE           = 75
XLARGE_ICON_SIZE          = 100
LINE_WIDTH                = 2
FOCUS_LINE_WIDTH          = 2
SEPARATOR_SIZE            = 4
SCROLLBAR_SIZE            = 13
EXPAND_ANIMATION_DURATION = 250
TOOLBOX_SEPARATOR_HEIGHT  = 4

class Color:
    def __init__(self, color_string, default=None):
        self._color_string = color_string or (default or '#888888')
    def get_gdk_color(self):
        try:
            ok, c = Gdk.Color.parse(self._color_string)
            if ok: return c
        except Exception: pass
        return Gdk.Color.parse('#888888')[1]
    def get_rgba(self):
        r = Gdk.RGBA(); r.parse(self._color_string); return r
    def to_string(self): return self._color_string

COLOR_BLACK           = Color('#000000')
COLOR_WHITE           = Color('#ffffff')
COLOR_BUTTON_GREY     = Color('#808080')
COLOR_PANEL_GREY      = Color('#c0c0c0')
COLOR_SELECTION_GREY  = Color('#a0a0a0')
COLOR_TOOLBAR_GREY    = Color('#282828')
COLOR_INACTIVE_FILL   = Color('#a0a0a0')
COLOR_INACTIVE_STROKE = Color('#808080')
