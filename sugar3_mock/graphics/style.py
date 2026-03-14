# sugar3_mock/graphics/style.py
# Stubs for sugar3.graphics.style constants and Color class.

import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

GRID_CELL_SIZE = 55
DEFAULT_PADDING = 6
STANDARD_ICON_SIZE = 55
SMALL_ICON_SIZE = 33
MEDIUM_ICON_SIZE = 55
LARGE_ICON_SIZE = 75
XLARGE_ICON_SIZE = 100

class Color:
    """Minimal Color stub mimicking sugar3.graphics.style.Color."""
    def __init__(self, color_string, default=None):
        # color_string can be '#rrggbb' or a CSS name
        self._color_string = color_string or (default or '#888888')

    def get_gdk_color(self):
        try:
            ok, gdk_color = Gdk.Color.parse(self._color_string)
            if ok:
                return gdk_color
        except Exception:
            pass
        return Gdk.Color.parse('#888888')[1]

    def get_rgba(self):
        rgba = Gdk.RGBA()
        rgba.parse(self._color_string)
        return rgba

    def to_string(self):
        return self._color_string

    def __repr__(self):
        return f'Color({self._color_string!r})'


# Pre-defined colours used by speak-ai
COLOR_BLACK         = Color('#000000')
COLOR_WHITE         = Color('#ffffff')
COLOR_BUTTON_GREY   = Color('#808080')
COLOR_PANEL_GREY    = Color('#c0c0c0')
COLOR_SELECTION_GREY= Color('#a0a0a0')
COLOR_TOOLBAR_GREY  = Color('#282828')
LINE_WIDTH = 2
FOCUS_LINE_WIDTH = 2
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
DEFAULT_SPACING = 4
EXPAND_ANIMATION_DURATION = 250
TOOLBOX_SEPARATOR_HEIGHT = 4
COLOR_TOOLBAR_GREY = Color("#282828")
COLOR_INACTIVE_FILL = Color("#a0a0a0")
COLOR_INACTIVE_STROKE = Color("#808080")
FOCUS_LINE_WIDTH = 2
FOCUS_LINE_WIDTH = 2
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
DEFAULT_SPACING = 4
EXPAND_ANIMATION_DURATION = 250
TOOLBOX_SEPARATOR_HEIGHT = 4
COLOR_TOOLBAR_GREY = Color("#282828")
COLOR_INACTIVE_FILL = Color("#a0a0a0")
COLOR_INACTIVE_STROKE = Color("#808080")
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
EXPAND_ANIMATION_DURATION = 250

LINE_WIDTH = 2
FOCUS_LINE_WIDTH = 2
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
DEFAULT_SPACING = 4
EXPAND_ANIMATION_DURATION = 250
TOOLBOX_SEPARATOR_HEIGHT = 4
COLOR_TOOLBAR_GREY = Color("#282828")
COLOR_INACTIVE_FILL = Color("#a0a0a0")
COLOR_INACTIVE_STROKE = Color("#808080")
FOCUS_LINE_WIDTH = 2
FOCUS_LINE_WIDTH = 2
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
DEFAULT_SPACING = 4
EXPAND_ANIMATION_DURATION = 250
TOOLBOX_SEPARATOR_HEIGHT = 4
COLOR_TOOLBAR_GREY = Color("#282828")
COLOR_INACTIVE_FILL = Color("#a0a0a0")
COLOR_INACTIVE_STROKE = Color("#808080")
SEPARATOR_SIZE = 4
SCROLLBAR_SIZE = 13
EXPAND_ANIMATION_DURATION = 250
