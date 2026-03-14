#!/usr/bin/env python3
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT  = os.path.dirname(SCRIPT_DIR)
for p in [SCRIPT_DIR, REPO_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

import dbus_mock
sys.modules["dbus"] = dbus_mock

import telepathy_mock
import gi
sys.modules["gi.repository.TelepathyGLib"] = telepathy_mock

original_require = gi.require_version
def patched_require(namespace, version):
    if namespace == "TelepathyGLib":
        return
    return original_require(namespace, version)
gi.require_version = patched_require

import sugar3_mock
import sugar3_mock.activity               as _act
import sugar3_mock.activity.activity      as _act_activity
import sugar3_mock.activity.widgets       as _act_widgets
import sugar3_mock.graphics               as _gfx
import sugar3_mock.graphics.style         as _style
import sugar3_mock.graphics.toolbutton    as _toolbtn
import sugar3_mock.graphics.radiotoolbutton as _rtoolbtn
import sugar3_mock.graphics.toolbarbox    as _toolbarbox
import sugar3_mock.graphics.objectchooser as _objchooser
import sugar3_mock.graphics.icon           as _icon
import sugar3_mock.graphics.palette        as _palette
import sugar3_mock.graphics.palettemenu    as _palettemenu
import sugar3_mock.util                    as _util
import sugar3_mock.activity.bundlebuilder  as _bundlebuilder
import sugar3_mock.presence               as _pres
import sugar3_mock.presence.presenceservice as _presservice
import sugar3_mock.datastore              as _ds
import sugar3_mock.datastore.datastore    as _datastore
import sugar3_mock.speech                 as _speech_mod

sys.modules["sugar3"]                          = sugar3_mock
sys.modules["sugar3.activity"]                 = _act
sys.modules["sugar3.activity.activity"]        = _act_activity
sys.modules["sugar3.activity.widgets"]         = _act_widgets
sys.modules["sugar3.graphics"]                 = _gfx
sys.modules["sugar3.graphics.style"]           = _style
sys.modules["sugar3.graphics.toolbutton"]      = _toolbtn
sys.modules["sugar3.graphics.radiotoolbutton"] = _rtoolbtn
sys.modules["sugar3.graphics.toolbarbox"]      = _toolbarbox
sys.modules["sugar3.graphics.objectchooser"]   = _objchooser
sys.modules["sugar3.graphics.icon"]           = _icon
sys.modules["sugar3.graphics.palette"]        = _palette
sys.modules["sugar3.graphics.palettemenu"]    = _palettemenu
sys.modules["sugar3.util"]                    = _util
sys.modules["sugar3.activity.bundlebuilder"]  = _bundlebuilder
sys.modules["sugar3.presence"]                 = _pres
sys.modules["sugar3.presence.presenceservice"] = _presservice
sys.modules["sugar3.datastore"]                = _ds
sys.modules["sugar3.datastore.datastore"]      = _datastore
sys.modules["sugar3.speech"]                   = _speech_mod
sys.modules["sugar3.mime"]                     = sugar3_mock.mime
sys.modules["sugar3.profile"]                  = sugar3_mock.profile

sugar3_mock.activity  = _act
sugar3_mock.presence  = _pres
sugar3_mock.datastore = _ds
sugar3_mock.speech    = _speech_mod
sugar3_mock.graphics  = _gfx

gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")
from gi.repository import Gtk, Gst, GObject

GObject.threads_init()
Gst.init(None)

print("✓ Mocks injected")
print("✓ GTK + GStreamer initialised")

try:
    from activity import SpeakActivity
    print("✓ SpeakActivity imported")
except Exception as e:
    print(f"✗ Failed to import SpeakActivity: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

try:
    app = SpeakActivity(handle=None)
    app.show_all()
    print("✓ Window shown — starting GTK main loop")
    Gtk.main()
except Exception as e:
    print(f"✗ Failed to start activity: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)