#!/usr/bin/env python3
"""
local_tts_server.py — Local TTS server for testing Path B WITHOUT Colab
========================================================================
Runs the EXACT same Flask API as colab_tts_server.ipynb,
but uses espeak-ng instead of Kokoro.

This means:
  - Zero heavy deps (no torch, no kokoro)
  - Works on 4 GB RAM
  - Tests the FULL Path B pipeline end-to-end
  - Same tts_client.py code path as real Colab

Usage (two terminals in VS Code):
  Terminal 1:  python local_tts_server.py
  Terminal 2:  python run_local.py    (or python test_toolkit.py)

When you're happy it works → swap in colab_tts_server.ipynb for the real deal.
"""

import io
import subprocess
import tempfile
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s  %(message)s')
logger = logging.getLogger('local_tts')

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    print("Flask not installed. Run: pip install flask")
    sys.exit(1)

try:
    import soundfile as sf
    import numpy as np
    SF_AVAILABLE = True
except ImportError:
    SF_AVAILABLE = False
    logger.warning("soundfile not installed — audio responses will be raw PCM")

app = Flask(__name__)

PORT = 5050

# ── TTS backends (in order of preference) ────────────────────
def _espeak_synthesize(text, voice='en', rate=150):
    """
    Use espeak-ng to synthesize text.
    Returns WAV bytes or None.
    voice: espeak voice code e.g. 'en', 'hi', 'hi+f1'
    """
    import shutil
    espeak_cmd = shutil.which('espeak-ng') or shutil.which('espeak')
    if not espeak_cmd:
        return None

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        out_path = f.name

    try:
        cmd = [
            espeak_cmd,
            '-v', voice,
            '-s', str(rate),
            '-w', out_path,
            text
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=15)
        if result.returncode != 0:
            logger.error(f'espeak error: {result.stderr.decode()}')
            return None

        with open(out_path, 'rb') as f:
            wav_bytes = f.read()
        return wav_bytes

    except Exception as e:
        logger.error(f'espeak synthesis failed: {e}')
        return None
    finally:
        try:
            os.unlink(out_path)
        except Exception:
            pass


def _voice_for_request(voice_code, lang_code):
    """
    Map Kokoro voice names → espeak voice codes.
    This is what makes the local server API-compatible with Colab.
    """
    # Hindi Kokoro voices → espeak Hindi variants
    hindi_map = {
        'hf_alpha': 'hi+f1',
        'hf_beta':  'hi+f2',
        'hm_omega': 'hi+m1',
        'hm_psi':   'hi+m2',
    }
    # English Kokoro voices → espeak English variants
    english_female = {'af_heart','af_alloy','af_aoede','af_bella','af_jessica',
                      'af_kore','af_nicole','af_nova','af_river','af_sarah','af_sky',
                      'bf_alice','bf_emma','bf_isabella','bf_lily'}
    english_male   = {'am_adam','am_echo','am_eric','am_fenrir','am_liam',
                      'am_michael','am_onyx','am_puck','am_santa',
                      'bm_daniel','bm_fable','bm_george','bm_lewis'}

    if lang_code == 'h' or voice_code in hindi_map:
        return hindi_map.get(voice_code, 'hi')

    if voice_code in english_female:
        return 'en+f3'
    if voice_code in english_male:
        return 'en+m3'

    return 'en'   # safe default


# ── Routes (identical API to colab_tts_server.ipynb) ─────────

@app.route('/ping', methods=['GET'])
def ping():
    import shutil
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')
    return jsonify({
        'status': 'ok',
        'backend': 'espeak-local',
        'espeak': espeak or 'not found',
        'loaded_langs': ['a', 'h'],   # always claim both — espeak has both
    })


@app.route('/tts', methods=['POST'])
def tts():
    data  = request.get_json(force=True)
    text  = data.get('text', '').strip()
    voice = data.get('voice', 'en')
    lang  = data.get('lang',  'a')

    if not text:
        return jsonify({'error': 'empty text'}), 400

    logger.info(f'TTS: lang={lang} voice={voice} text={text!r}')

    espeak_voice = _voice_for_request(voice, lang)
    wav_bytes    = _espeak_synthesize(text, voice=espeak_voice)

    if not wav_bytes:
        return jsonify({'error': 'espeak synthesis failed — is espeak-ng installed?'}), 500

    buf = io.BytesIO(wav_bytes)
    buf.seek(0)
    return send_file(buf, mimetype='audio/wav', as_attachment=False)


@app.route('/voices', methods=['GET'])
def voices():
    return jsonify({
        'english': ['af_heart','af_alloy','af_aoede','am_adam','am_echo',
                    'bf_alice','bf_emma','bm_daniel','bm_george'],
        'hindi':   ['hf_alpha','hf_beta','hm_omega','hm_psi'],
        'note':    'local server — espeak backend, Kokoro-compatible API',
    })


# ── Main ──────────────────────────────────────────────────────
if __name__ == '__main__':
    import shutil
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')

    print()
    print('═' * 55)
    print('  speak-ai  Local TTS Server  (espeak backend)')
    print('═' * 55)

    if not espeak:
        print('  ✗ espeak-ng not found!')
        print('  Install: sudo apt install espeak-ng')
        sys.exit(1)

    print(f'  ✓ espeak found: {espeak}')
    print(f'  ✓ Listening on http://localhost:{PORT}')
    print()
    print('  In another terminal:')
    print(f'    echo "http://localhost:{PORT}" > colab_url.txt')
    print('    python run_local.py')
    print()
    print('  Or run tests:')
    print('    python test_toolkit.py')
    print('═' * 55)
    print()

    app.run(port=PORT, debug=False, use_reloader=False)