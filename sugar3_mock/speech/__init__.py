# sugar3_mock/speech/__init__.py
# Stub for sugar3.speech.GstSpeechPlayer
# Speech in speak-ai inherits from this and emits GObject signals.

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

class GstSpeechPlayer(GObject.GObject):
    """Minimal stub matching the real sugar3.speech.GstSpeechPlayer interface."""

    def __init__(self):
        GObject.GObject.__init__(self)
        self._pipeline = None

    def restart_sound_device(self):
        if self._pipeline:
            self._pipeline.set_state(Gst.State.PLAYING)

    def stop_sound_device(self):
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)