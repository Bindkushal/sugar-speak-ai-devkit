"""
tts_client.py  —  Transparent TTS abstraction layer for speak-ai
================================================================
Handles three TTS backends in priority order:

  1. COLAB mode   — sends text to Colab TTS server, gets WAV bytes back
  2. KOKORO mode  — local kokoro pipeline (Path A, 12+ GB RAM)
  3. ESPEAK mode  — system espeak-ng (always available, zero deps)

speak-ai's speech.py calls get_tts_backend() once at startup.
The rest of the code doesn't need to know which backend is active.

Configuration (pick one):
  export SPEAK_AI_TTS=colab   and   export COLAB_TTS_URL=https://xxxx.ngrok.io
  export SPEAK_AI_TTS=kokoro
  export SPEAK_AI_TTS=espeak
  (default: auto-detect based on what's installed)
"""

import os
import io
import logging
import tempfile
import threading
import numpy as np

logger = logging.getLogger('speak.tts_client')

# ── Read config ─────────────────────────────────────────────
TTS_MODE    = os.environ.get('SPEAK_AI_TTS', 'auto').lower()
COLAB_URL   = os.environ.get('COLAB_TTS_URL', '').rstrip('/')

# Also accept URL from a file (user drops colab_url.txt into repo root)
_URL_FILE = os.path.join(os.path.dirname(__file__), 'colab_url.txt')
if not COLAB_URL and os.path.exists(_URL_FILE):
    with open(_URL_FILE) as f:
        COLAB_URL = f.read().strip().rstrip('/')
    if COLAB_URL:
        logger.info(f'Loaded Colab URL from colab_url.txt: {COLAB_URL}')


# ─────────────────────────────────────────────────────────────
# Backend: COLAB
# ─────────────────────────────────────────────────────────────
class ColabTTSBackend:
    """
    Sends text to a running colab_tts_server.ipynb instance.
    Returns raw PCM int16 numpy array at 24000 Hz (matches Kokoro output).
    """
    name = 'colab'

    def __init__(self, base_url):
        self.base_url = base_url
        self._session = None
        self._ok = False
        self._check()

    def _check(self):
        try:
            import requests
            r = requests.get(f'{self.base_url}/ping', timeout=5)
            if r.status_code == 200:
                self._ok = True
                logger.info(f'Colab TTS server reachable at {self.base_url}')
            else:
                logger.warning(f'Colab TTS ping returned {r.status_code}')
        except Exception as e:
            logger.warning(f'Colab TTS server not reachable: {e}')

    @property
    def available(self):
        return self._ok and bool(self.base_url)

    def synthesize(self, text, voice='hf_alpha', lang='hi'):
        """Returns (sample_rate, numpy_int16_array) or None on failure."""
        import requests, soundfile as sf
        try:
            resp = requests.post(
                f'{self.base_url}/tts',
                json={'text': text, 'voice': voice, 'lang': lang},
                timeout=60
            )
            resp.raise_for_status()
            buf = io.BytesIO(resp.content)
            data, sr = sf.read(buf, dtype='int16')
            return sr, data
        except Exception as e:
            logger.error(f'Colab TTS request failed: {e}')
            return None


# ─────────────────────────────────────────────────────────────
# Backend: LOCAL KOKORO
# ─────────────────────────────────────────────────────────────
class KokoroTTSBackend:
    """Wraps the local KPipeline. Loads in background thread."""
    name = 'kokoro'

    def __init__(self):
        self._pipelines = {}   # lang_code → KPipeline
        self._lock = threading.Lock()
        self._loading = set()

    @property
    def available(self):
        try:
            import kokoro  # noqa
            return True
        except ImportError:
            return False

    def _get_pipeline(self, lang_code='a'):
        with self._lock:
            if lang_code not in self._pipelines:
                from kokoro import KPipeline
                logger.info(f'Loading Kokoro pipeline lang={lang_code} ...')
                self._pipelines[lang_code] = KPipeline(lang_code=lang_code)
                logger.info(f'Kokoro pipeline lang={lang_code} ready')
            return self._pipelines[lang_code]

    def synthesize(self, text, voice='af_heart', lang='a'):
        try:
            pipe = self._get_pipeline(lang)
            chunks = []
            for _, _, audio in pipe(text, voice=voice):
                chunks.append(audio.numpy())
            if not chunks:
                return None
            audio_f32 = np.concatenate(chunks)
            audio_i16 = (audio_f32 * 32767).astype(np.int16)
            return 24000, audio_i16
        except Exception as e:
            logger.error(f'Kokoro synthesis failed: {e}')
            return None

    def preload(self, lang_code='a'):
        """Start loading a pipeline in a background thread."""
        threading.Thread(
            target=self._get_pipeline,
            args=(lang_code,),
            daemon=True
        ).start()


# ─────────────────────────────────────────────────────────────
# Backend: ESPEAK (always available)
# ─────────────────────────────────────────────────────────────
class EspeakTTSBackend:
    """
    Falls back to system espeak-ng.
    Returns None — espeak is driven directly by GStreamer in speech.py,
    not through this client. This backend is a sentinel so the caller
    knows to use the GStreamer espeak pipeline.
    """
    name = 'espeak'

    @property
    def available(self):
        import shutil
        return shutil.which('espeak-ng') is not None or shutil.which('espeak') is not None

    def synthesize(self, text, voice='en', lang=None):
        # espeak is handled by GStreamer pipeline in speech.py directly
        return None


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────
_backend = None

def get_tts_backend():
    """
    Returns the best available TTS backend based on SPEAK_AI_TTS env var
    or auto-detection. Call once at startup.
    """
    global _backend
    if _backend is not None:
        return _backend

    if TTS_MODE == 'colab' or (TTS_MODE == 'auto' and COLAB_URL):
        b = ColabTTSBackend(COLAB_URL)
        if b.available:
            logger.info('TTS backend: COLAB')
            _backend = b
            return _backend

    if TTS_MODE in ('kokoro', 'auto'):
        b = KokoroTTSBackend()
        if b.available:
            logger.info('TTS backend: LOCAL KOKORO')
            _backend = b
            return _backend

    logger.info('TTS backend: ESPEAK (fallback)')
    _backend = EspeakTTSBackend()
    return _backend


def backend_name():
    return get_tts_backend().name