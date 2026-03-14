#!/usr/bin/env python3
"""
run_local.py — Local launcher for speak-ai
==========================================
Runs speak-ai's full GTK face + TTS pipeline in VS Code / plain Ubuntu desktop
WITHOUT needing the Sugar shell, D-Bus session, or Telepathy.

Usage:
    cd /path/to/speak-ai
    python run_local.py

Requirements (install once):
    pip install kokoro misaki[en] soundfile numpy torch requests huggingface_hub
    sudo apt install gstreamer1.0-espeak gir1.2-gstreamer-1.0 \
                     gir1.2-gst-plugins-base-1.0 espeak-ng
"""

import sys
import os
import types

# ──────────────────────────────────────────────
# 0. Make sure this script's directory (speak-ai root) is on the path
# ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# run_local.py lives in speak-ai-local/ which is dropped into speak-ai/
# So the speak-ai source root is one level up if running from there,
# OR the same dir if you copied run_local.py into the repo root.
# We add both so it works either way.
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
for p in [SCRIPT_DIR, REPO_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ──────────────────────────────────────────────
# 1. Inject dbus + TelepathyGLib mocks BEFORE any other import
# ──────────────────────────────────────────────
import dbus_mock                # our stub
sys.modules['dbus'] = dbus_mock

import telepathy_mock
# TelepathyGLib lives under gi.repository
import gi
# Patch gi.repository so that `from gi.repository import TelepathyGLib` works
if not hasattr(gi.repository, 'TelepathyGLib'):
    sys.modules['gi.repository.TelepathyGLib'] = telepathy_mock
    # Also make it accessible as an attribute so gi.require_version doesn't crash
    original_require = gi.require_version
    def patched_require(namespace, version):
        if namespace == 'TelepathyGLib':
            return  # silently accept
        return original_require(namespace, version)
    gi.require_version = patched_require

# ──────────────────────────────────────────────
# 2. Inject sugar3 mock package
# ──────────────────────────────────────────────
import sugar3_mock                                          # top-level: profile, mime

# Register submodules so `from sugar3.X import Y` works
import sugar3_mock.activity            as _act
import sugar3_mock.activity.activity   as _act_activity
import sugar3_mock.activity.widgets    as _act_widgets
import sugar3_mock.graphics            as _gfx
import sugar3_mock.graphics.style      as _style
import sugar3_mock.graphics.toolbutton as _toolbtn
import sugar3_mock.graphics.radiotoolbutton as _rtoolbtn
import sugar3_mock.graphics.toolbarbox as _toolbarbox
import sugar3_mock.graphics.objectchooser as _objchooser
import sugar3_mock.presence            as _pres
import sugar3_mock.presence.presenceservice as _presservice
import sugar3_mock.datastore           as _ds
import sugar3_mock.datastore.datastore as _datastore
import sugar3_mock.speech              as _speech_mod

sys.modules['sugar3']                           = sugar3_mock
sys.modules['sugar3.activity']                  = _act
sys.modules['sugar3.activity.activity']         = _act_activity
sys.modules['sugar3.activity.widgets']          = _act_widgets
sys.modules['sugar3.graphics']                  = _gfx
sys.modules['sugar3.graphics.style']            = _style
sys.modules['sugar3.graphics.toolbutton']       = _toolbtn
sys.modules['sugar3.graphics.radiotoolbutton']  = _rtoolbtn
sys.modules['sugar3.graphics.toolbarbox']       = _toolbarbox
sys.modules['sugar3.graphics.objectchooser']    = _objchooser
sys.modules['sugar3.presence']                  = _pres
sys.modules['sugar3.presence.presenceservice']  = _presservice
sys.modules['sugar3.datastore']                 = _ds
sys.modules['sugar3.datastore.datastore']       = _datastore
sys.modules['sugar3.speech']                    = _speech_mod
sys.modules['sugar3.mime']                      = sugar3_mock.mime
sys.modules['sugar3.profile']                   = sugar3_mock.profile  # type: ignore

# Make `from sugar3 import profile` and `from sugar3 import mime` work
sugar3_mock.profile  = sugar3_mock.profile   # already a class attribute
sugar3_mock.mime     = sugar3_mock.mime       # already a class attribute
sugar3_mock.activity = _act
sugar3_mock.presence = _pres
sugar3_mock.datastore= _ds
sugar3_mock.speech   = _speech_mod
sugar3_mock.graphics = _gfx

# ──────────────────────────────────────────────
# 3. Now it's safe to import GTK and the activity
# ──────────────────────────────────────────────
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GObject

GObject.threads_init()
Gst.init(None)

print("✓ Mocks injected")
print("✓ GTK + GStreamer initialised")

# ──────────────────────────────────────────────
# 4. Import the activity and launch
# ──────────────────────────────────────────────
try:
    from activity import SpeakActivity  # speak-ai's main class
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