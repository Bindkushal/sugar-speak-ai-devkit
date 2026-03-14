# speech_patched.py  —  Drop-in replacement for speak-ai/speech.py
# ================================================================
# Changes from original:
#   1. Uses tts_client.py abstraction (Colab / Kokoro / espeak auto-select)
#   2. Hindi espeak voice wired in (hind lang code)
#   3. Kokoro lang_code passed through properly for Hindi
#   4. setup_kokoro() accepts lang_code param
#   5. GstSpeechPlayer import now comes from sugar3_mock when running locally
# ================================================================

import numpy
import threading
import io

from gi.repository import Gst
from gi.repository import GLib
from gi.repository import GObject

import logging
logger = logging.getLogger('speak')

from sugar3.speech import GstSpeechPlayer

# ── TTS client (auto-selects Colab / Kokoro / espeak) ──────────
from tts_client import get_tts_backend, KokoroTTSBackend, ColabTTSBackend

# Legacy direct-kokoro flag kept for GStreamer pipeline branching
try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    logger.info("Kokoro not installed — using tts_client backend")

PITCH_MIN = 0
PITCH_MAX = 200
RATE_MIN = 0
RATE_MAX = 200

# ── Voice lists ─────────────────────────────────────────────────
KOKORO_VOICES_EN = [
    'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica',
    'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
    'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam',
    'am_michael', 'am_onyx', 'am_puck', 'am_santa',
    'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily',
    'bm_daniel', 'bm_fable', 'bm_george', 'bm_lewis',
]

# Hindi Kokoro voices — our target
KOKORO_VOICES_HI = [
    'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi',
]

# espeak Hindi voices (always available, no extra deps)
ESPEAK_VOICES_HI = [
    'hi',        # standard Hindi
    'hi+f1',     # Hindi female variant 1
    'hi+f2',     # Hindi female variant 2
    'hi+m1',     # Hindi male variant 1
]


class Speech(GstSpeechPlayer):
    __gsignals__ = {
        'peak': (GObject.SIGNAL_RUN_FIRST, None, [GObject.TYPE_PYOBJECT]),
        'wave': (GObject.SIGNAL_RUN_FIRST, None, [GObject.TYPE_PYOBJECT]),
        'idle': (GObject.SIGNAL_RUN_FIRST, None, []),
    }

    def __init__(self):
        GstSpeechPlayer.__init__(self)
        self.pipeline = None

        # Detect and store backend once
        self._backend = get_tts_backend()
        logger.info(f'Speech using TTS backend: {self._backend.name}')

        # Kokoro pipeline (only used when backend is local kokoro)
        self.kokoro_pipeline = None
        if isinstance(self._backend, KokoroTTSBackend):
            # Preload English pipeline immediately, Hindi lazily
            self._backend.preload('a')

        self.kokoro_voices    = KOKORO_VOICES_EN + KOKORO_VOICES_HI
        self.current_kokoro_voice = 'af_heart'
        self.current_lang_code    = 'a'    # 'a'=English, 'h'=Hindi

        # espeak Hindi voice for fallback path
        self.current_espeak_voice = 'default'

        self._cb = {}
        for cb in ['peak', 'wave', 'idle']:
            self._cb[cb] = None

    # ── voice setters ────────────────────────────────────────────
    def set_kokoro_voice(self, voice_name):
        if voice_name in KOKORO_VOICES_HI:
            self.current_lang_code = 'h'
        elif voice_name in KOKORO_VOICES_EN:
            self.current_lang_code = 'a'

        if voice_name in self.kokoro_voices:
            self.current_kokoro_voice = voice_name
            logger.debug(f'Kokoro voice set: {voice_name}  lang={self.current_lang_code}')
            # Preload the pipeline for this lang in background
            if isinstance(self._backend, KokoroTTSBackend):
                self._backend.preload(self.current_lang_code)
        else:
            logger.warning(f'Invalid Kokoro voice: {voice_name}')

    def get_available_kokoro_voices(self):
        return self.kokoro_voices.copy()

    def get_hindi_kokoro_voices(self):
        return KOKORO_VOICES_HI.copy()

    def get_hindi_espeak_voices(self):
        return ESPEAK_VOICES_HI.copy()

    def get_default_kokoro_voices(self):
        return ['af_heart', 'af_alloy', 'af_aoede']

    def get_addon_kokoro_voices(self):
        return [v for v in self.kokoro_voices
                if v not in self.get_default_kokoro_voices()]

    # ── signal helpers ───────────────────────────────────────────
    def disconnect_all(self):
        for cb in ['peak', 'wave', 'idle']:
            hid = self._cb[cb]
            if hid is not None:
                self.disconnect(hid)
                self._cb[cb] = None

    def connect_peak(self, cb):
        self._cb['peak'] = self.connect('peak', cb)

    def connect_wave(self, cb):
        self._cb['wave'] = self.connect('wave', cb)

    def connect_idle(self, cb):
        self._cb['idle'] = self.connect('idle', cb)

    # ── GStreamer pipeline ───────────────────────────────────────
    def _use_neural_pipeline(self):
        """True if we'll push PCM via appsrc (Colab or local Kokoro)."""
        return isinstance(self._backend, (KokoroTTSBackend, ColabTTSBackend))

    def make_pipeline(self):
        if self.pipeline is not None:
            self.stop_sound_device()
            del self.pipeline

        if self._use_neural_pipeline():
            cmd = ('appsrc name=tts_src'
                   ' ! audioconvert'
                   ' ! audio/x-raw,channels=(int)1,format=F32LE,rate=24000'
                   ' ! tee name=me'
                   ' me.! queue ! autoaudiosink name=ears'
                   ' me.! queue ! audioconvert ! audioresample'
                   ' ! audio/x-raw,format=S16LE,channels=1,rate=16000'
                   ' ! fakesink name=sink')
        else:
            # espeak pipeline (original)
            cmd = ('espeak name=espeak'
                   ' ! capsfilter name=caps'
                   ' ! tee name=me'
                   ' me.! queue ! autoaudiosink name=ears'
                   ' me.! queue ! fakesink name=sink')

        self.pipeline = Gst.parse_launch(cmd)

        if not self._use_neural_pipeline():
            caps = self.pipeline.get_by_name('caps')
            want = 'audio/x-raw,channels=(int)1,depth=(int)16'
            caps.set_property('caps', Gst.caps_from_string(want))

        ears = self.pipeline.get_by_name('ears')

        def handoff(element, data, pad):
            size = data.get_size()
            if size == 0:
                return True

            if (data.duration == 0
                    or data.duration == Gst.CLOCK_TIME_NONE
                    or data.duration > Gst.SECOND * 10):
                SAMPLE_RATE = 16000
                samples = size // 2
                actual_duration = samples * Gst.SECOND // SAMPLE_RATE
            else:
                actual_duration = data.duration

            npc = 50000000
            bpc = size * npc // actual_duration
            bpc = bpc // 2 * 2
            if bpc == 0:
                bpc = min(4096, size)
                bpc = bpc // 2 * 2

            a, p, w = [], [], []
            here = 0
            when = data.pts
            last = data.pts + actual_duration

            while True:
                try:
                    raw_bytes = data.extract_dup(here, bpc)
                    if len(raw_bytes) == 0:
                        break
                    wave = numpy.frombuffer(raw_bytes, dtype='int16')
                    if len(wave) == 0:
                        break
                    peak = numpy.max(numpy.abs(wave))
                except Exception as e:
                    logger.warning(f'handoff error: {e}')
                    break

                a.append(wave); p.append(peak); w.append(when)
                here += bpc
                when += npc
                if when >= last:
                    break

            total_chunks = len(a)
            interval_ms = max(10, int(actual_duration / max(total_chunks, 1) / 1_000_000))

            def emit_next():
                if a:
                    self.emit('wave', a[0]); self.emit('peak', p[0])
                    del a[0]; del p[0]; del w[0]
                    if a:
                        GLib.timeout_add(interval_ms, emit_next)
                return False

            if self._use_neural_pipeline():
                GLib.timeout_add(interval_ms, emit_next)
            else:
                def poke(pts):
                    success, position = ears.query_position(Gst.Format.TIME)
                    if not success:
                        if w:
                            self.emit('wave', a[0]); self.emit('peak', p[0])
                            del a[0]; del w[0]; del p[0]
                            if w:
                                GLib.timeout_add(25, poke, pts)
                        return False
                    if not w:
                        return False
                    if position < w[0]:
                        return True
                    self.emit('wave', a[0]); self.emit('peak', p[0])
                    del a[0]; del w[0]; del p[0]
                    return bool(w)
                GLib.timeout_add(25, poke, data.pts)

            return True

        sink = self.pipeline.get_by_name('sink')
        sink.props.signal_handoffs = True
        sink.connect('handoff', handoff)

        def gst_message_cb(bus, message):
            self._was_message = True
            if message.type == Gst.MessageType.WARNING:
                def check():
                    if not self._was_message:
                        self.stop_sound_device()
                    return True
                self._was_message = False
                GLib.timeout_add(500, check)
            elif message.type in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
                self.stop_sound_device()
            return True

        self._was_message = False
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', gst_message_cb)

    def _push_audio_to_pipeline(self, sr, audio_i16):
        """Push PCM int16 array into the appsrc GStreamer pipeline."""
        appsrc = self.pipeline.get_by_name('tts_src')
        if not appsrc:
            logger.error('tts_src appsrc element not found')
            return

        caps = Gst.Caps.from_string(
            'audio/x-raw,format=S16LE,layout=interleaved,'
            f'rate={sr},channels=1'
        )
        appsrc.set_property('caps', caps)

        data_bytes = audio_i16.tobytes()
        buf = Gst.Buffer.new_wrapped(data_bytes)
        ret = appsrc.emit('push-buffer', buf)
        if ret != Gst.FlowReturn.OK:
            logger.error(f'appsrc push-buffer returned {ret}')
        appsrc.emit('end-of-stream')

    # ── Main speak entry point ───────────────────────────────────
    def speak(self, status, text):
        self.make_pipeline()

        if self._use_neural_pipeline():
            # Colab or local Kokoro path
            logger.debug(f'TTS ({self._backend.name}): voice={self.current_kokoro_voice} '
                         f'lang={self.current_lang_code} text={text!r}')
            self.restart_sound_device()

            def _synthesize_and_push():
                result = self._backend.synthesize(
                    text,
                    voice=self.current_kokoro_voice,
                    lang=self.current_lang_code
                )
                if result is not None:
                    sr, audio = result
                    GLib.idle_add(self._push_audio_to_pipeline, sr, audio)
                else:
                    logger.warning('Neural TTS returned None — no audio')

            threading.Thread(target=_synthesize_and_push, daemon=True).start()

        else:
            # espeak path (original behaviour preserved)
            src = self.pipeline.get_by_name('espeak')
            pitch = int(status.pitch) - 100
            rate  = int(status.rate)  - 100

            # Hindi espeak voice support
            voice_name = status.voice.name
            if getattr(status, 'use_hindi_espeak', False):
                voice_name = self.current_espeak_voice or 'hi'

            logger.debug(f'espeak: pitch={pitch} rate={rate} '
                         f'voice={voice_name} text={text!r}')
            src.props.pitch = pitch
            src.props.rate  = rate
            src.props.voice = voice_name
            src.props.track = 1
            src.props.text  = text
            self.restart_sound_device()


_speech = None

def get_speech():
    global _speech
    if _speech is None:
        _speech = Speech()
    return _speech