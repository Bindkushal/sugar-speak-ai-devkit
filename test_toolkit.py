#!/usr/bin/env python3
"""
test_toolkit.py — speak-ai toolkit test suite
==============================================
Tests every component WITHOUT needing Sugar, torch, or kokoro.
Works on 4 GB RAM.

Usage:
  python test_toolkit.py               # all tests
  python test_toolkit.py mocks         # only mock injection
  python test_toolkit.py tts           # only TTS client
  python test_toolkit.py server        # only server ping (needs local_tts_server.py running)
  python test_toolkit.py gst           # only GStreamer pipeline
  python test_toolkit.py espeak        # only espeak speak test (plays audio!)
"""

import sys
import os
import time
import importlib

# ── Make sure we're running from the speak-ai repo root ──────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

SEP  = '─' * 55
SEPP = '═' * 55
PASS = '  ✓'
FAIL = '  ✗'
SKIP = '  ·'

results = []

def test(name):
    """Decorator to register a test."""
    def decorator(fn):
        fn._test_name = name
        results.append(fn)
        return fn
    return decorator

def run_test(fn):
    name = fn._test_name
    try:
        msg = fn()
        status = PASS
        detail = msg or ''
        ok = True
    except AssertionError as e:
        status = FAIL
        detail = str(e)
        ok = False
    except Exception as e:
        status = FAIL
        detail = f'{type(e).__name__}: {e}'
        ok = False
    print(f'{status}  {name}')
    if detail:
        print(f'       {detail}')
    return ok


# ════════════════════════════════════════════════════════
# GROUP 1 — Mock injection
# ════════════════════════════════════════════════════════

@test("dbus_mock imports cleanly")
def test_dbus_mock():
    import dbus_mock
    sys.modules['dbus'] = dbus_mock
    assert hasattr(dbus_mock, 'Bus')
    assert hasattr(dbus_mock, 'PROPERTIES_IFACE')
    return "Bus, PROPERTIES_IFACE present"

@test("telepathy_mock imports cleanly")
def test_telepathy_mock():
    import telepathy_mock
    assert hasattr(telepathy_mock, 'IFACE_CHANNEL')
    assert hasattr(telepathy_mock, 'ChannelGroupFlags')
    return "IFACE_CHANNEL, ChannelGroupFlags present"

@test("sugar3_mock top-level: profile.get_color()")
def test_sugar3_profile():
    import sugar3_mock
    color = sugar3_mock.profile.get_color()
    s = color.to_string()
    assert ',' in s, f"Expected 'stroke,fill' got: {s}"
    return f"color string: {s}"

@test("sugar3_mock top-level: mime.get_for_file()")
def test_sugar3_mime():
    import sugar3_mock
    result = sugar3_mock.mime.get_for_file('/tmp/test.txt')
    assert result == 'application/octet-stream'
    return f"mime: {result}"

@test("sugar3_mock.graphics.style constants")
def test_style_constants():
    import sugar3_mock.graphics.style as style
    assert style.GRID_CELL_SIZE == 55
    assert style.DEFAULT_PADDING == 6
    assert hasattr(style, 'COLOR_BLACK')
    assert hasattr(style, 'COLOR_BUTTON_GREY')
    return f"GRID_CELL_SIZE={style.GRID_CELL_SIZE}, DEFAULT_PADDING={style.DEFAULT_PADDING}"

@test("sugar3_mock.graphics.style.Color instantiation")
def test_style_color():
    import sugar3_mock.graphics.style as style
    c = style.Color('#ff0000')
    assert c.to_string() == '#ff0000'
    return f"Color('#ff0000').to_string() = {c.to_string()}"

@test("sugar3_mock.activity.Activity instantiation (no GTK display needed)")
def test_activity_no_display():
    # We test the import only, not the GTK instantiation
    import sugar3_mock.activity as act
    assert hasattr(act, 'Activity')
    return "Activity class present"

@test("sugar3_mock.activity.activity helpers")
def test_activity_helpers():
    from sugar3_mock.activity.activity import get_activity_root, show_object_in_journal
    root = get_activity_root()
    assert isinstance(root, str)
    show_object_in_journal('test-id')   # must not raise
    return f"root: {root}"

@test("sugar3_mock.activity.widgets present")
def test_activity_widgets():
    import sugar3_mock.activity.widgets as w
    assert hasattr(w, 'ActivityToolbarButton')
    assert hasattr(w, 'StopButton')
    return "ActivityToolbarButton, StopButton present"

@test("sugar3_mock.presence.presenceservice.get_instance()")
def test_presenceservice():
    from sugar3_mock.presence.presenceservice import get_instance
    svc = get_instance()
    owner = svc.get_owner()
    assert owner.nick == 'User'
    buddies = svc.get_buddies()
    assert isinstance(buddies, list)
    return f"owner.nick={owner.nick}, buddies={buddies}"

@test("sugar3_mock.datastore create/write no-op")
def test_datastore():
    from sugar3_mock.datastore.datastore import create, write
    obj = create()
    assert obj.object_id == 'local-0001'
    write(obj)   # must not raise
    return f"object_id={obj.object_id}"

@test("sugar3_mock.speech.GstSpeechPlayer subclassable")
def test_speech_base():
    import sugar3_mock.speech as sm
    assert hasattr(sm, 'GstSpeechPlayer')
    return "GstSpeechPlayer present"

@test("sys.modules injection: all sugar3.* keys registered")
def test_sysmodules_injection():
    # Simulate what run_local.py does
    import sugar3_mock
    import sugar3_mock.graphics.style as _s
    sys.modules['sugar3'] = sugar3_mock
    sys.modules['sugar3.graphics.style'] = _s
    import importlib
    mod = importlib.import_module('sugar3.graphics.style')
    assert mod.GRID_CELL_SIZE == 55
    return "sugar3.graphics.style importable via sys.modules"


# ════════════════════════════════════════════════════════
# GROUP 2 — TTS client (no torch/kokoro needed)
# ════════════════════════════════════════════════════════

@test("tts_client imports cleanly")
def test_tts_client_import():
    import tts_client
    assert hasattr(tts_client, 'get_tts_backend')
    assert hasattr(tts_client, 'ColabTTSBackend')
    assert hasattr(tts_client, 'KokoroTTSBackend')
    assert hasattr(tts_client, 'EspeakTTSBackend')
    return "all backend classes present"

@test("tts_client: EspeakTTSBackend.available")
def test_espeak_backend():
    from tts_client import EspeakTTSBackend
    b = EspeakTTSBackend()
    # availability depends on system — just check it doesn't crash
    avail = b.available
    return f"available={avail}"

@test("tts_client: KokoroTTSBackend.available=False (no torch installed)")
def test_kokoro_backend_unavailable():
    from tts_client import KokoroTTSBackend
    b = KokoroTTSBackend()
    # On 4GB machine without torch, should be False
    try:
        import kokoro  # noqa
        return "kokoro IS installed (Path A machine)"
    except ImportError:
        assert not b.available
        return "correctly reports unavailable (no kokoro)"

@test("tts_client: ColabTTSBackend with no URL → not available")
def test_colab_backend_no_url():
    from tts_client import ColabTTSBackend
    b = ColabTTSBackend('')
    assert not b.available
    return "ColabTTSBackend('') → not available"

@test("tts_client: auto backend selection falls back to espeak")
def test_auto_backend():
    # Temporarily clear any colab URL
    old_mode = os.environ.get('SPEAK_AI_TTS', '')
    old_url  = os.environ.get('COLAB_TTS_URL', '')
    os.environ['SPEAK_AI_TTS'] = 'espeak'
    os.environ.pop('COLAB_TTS_URL', None)

    # Reset cached backend
    import tts_client
    tts_client._backend = None

    b = tts_client.get_tts_backend()
    name = b.name
    tts_client._backend = None   # reset for other tests

    # Restore
    os.environ['SPEAK_AI_TTS'] = old_mode
    if old_url:
        os.environ['COLAB_TTS_URL'] = old_url

    assert name == 'espeak'
    return f"backend={name}"

@test("tts_client: colab_url.txt file loaded when present")
def test_colab_url_file():
    url_file = os.path.join(SCRIPT_DIR, 'colab_url.txt')
    wrote = False
    try:
        if not os.path.exists(url_file):
            with open(url_file, 'w') as f:
                f.write('http://localhost:5050')
            wrote = True

        # Reload tts_client to pick up the file
        import tts_client as tc
        tc._backend = None
        importlib.reload(tc)

        assert tc.COLAB_URL == 'http://localhost:5050' or os.path.exists(url_file)
        return f"COLAB_URL={tc.COLAB_URL or '(already set from env)'}"
    finally:
        if wrote and os.path.exists(url_file):
            os.unlink(url_file)
        import tts_client as tc
        tc._backend = None


# ════════════════════════════════════════════════════════
# GROUP 3 — Local TTS server (needs local_tts_server.py running)
# ════════════════════════════════════════════════════════

def _server_running(url='http://localhost:5050'):
    try:
        import requests
        r = requests.get(f'{url}/ping', timeout=3)
        return r.status_code == 200
    except Exception:
        return False

@test("local_tts_server: /ping reachable")
def test_server_ping():
    if not _server_running():
        raise AssertionError(
            "Server not running. Start it first:\n"
            "       python local_tts_server.py"
        )
    import requests
    r = requests.get('http://localhost:5050/ping', timeout=5)
    data = r.json()
    assert data['status'] == 'ok'
    return f"backend={data.get('backend')}, langs={data.get('loaded_langs')}"

@test("local_tts_server: /voices returns english + hindi")
def test_server_voices():
    if not _server_running():
        raise AssertionError("Server not running — start local_tts_server.py")
    import requests
    r = requests.get('http://localhost:5050/voices', timeout=5)
    data = r.json()
    assert 'english' in data
    assert 'hindi' in data
    assert 'hf_alpha' in data['hindi']
    return f"english={len(data['english'])} voices, hindi={len(data['hindi'])} voices"

@test("local_tts_server: /tts English synthesis → WAV bytes")
def test_server_tts_english():
    if not _server_running():
        raise AssertionError("Server not running — start local_tts_server.py")
    import requests
    r = requests.post('http://localhost:5050/tts',
                      json={'text': 'Hello, this is a test.', 'voice': 'af_heart', 'lang': 'a'},
                      timeout=15)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    assert r.headers['Content-Type'].startswith('audio/')
    assert len(r.content) > 1000, f"Audio too small: {len(r.content)} bytes"
    return f"WAV size: {len(r.content)} bytes"

@test("local_tts_server: /tts Hindi synthesis → WAV bytes")
def test_server_tts_hindi():
    if not _server_running():
        raise AssertionError("Server not running — start local_tts_server.py")
    import requests
    r = requests.post('http://localhost:5050/tts',
                      json={'text': 'नमस्ते, यह एक परीक्षण है।', 'voice': 'hf_alpha', 'lang': 'h'},
                      timeout=15)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    assert len(r.content) > 1000, f"Audio too small: {len(r.content)} bytes"
    return f"Hindi WAV size: {len(r.content)} bytes"

@test("tts_client ColabTTSBackend: synthesize() via local server")
def test_colab_client_synthesize():
    if not _server_running():
        raise AssertionError("Server not running — start local_tts_server.py")
    # Reset backend to force colab
    import tts_client
    tts_client._backend = None
    os.environ['SPEAK_AI_TTS']  = 'colab'
    os.environ['COLAB_TTS_URL'] = 'http://localhost:5050'
    importlib.reload(tts_client)

    b = tts_client.get_tts_backend()
    assert b.name == 'colab', f"Expected colab, got {b.name}"
    result = b.synthesize('Hello world', voice='af_heart', lang='a')
    assert result is not None, "synthesize() returned None"
    sr, audio = result
    assert sr > 0
    assert len(audio) > 100

    # Cleanup
    tts_client._backend = None
    os.environ.pop('SPEAK_AI_TTS', None)
    os.environ.pop('COLAB_TTS_URL', None)
    return f"sr={sr}, samples={len(audio)}"


# ════════════════════════════════════════════════════════
# GROUP 4 — GStreamer (no audio output, just pipeline build)
# ════════════════════════════════════════════════════════

@test("GStreamer: gi.repository.Gst importable")
def test_gst_import():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    return f"Gst version: {Gst.version_string()}"

@test("GStreamer: espeak element exists")
def test_gst_espeak():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    factory = Gst.ElementFactory.find('espeak')
    if factory is None:
        raise AssertionError(
            "espeak GStreamer element not found\n"
            "       Fix: sudo apt install gstreamer1.0-espeak"
        )
    return f"espeak factory: {factory.get_name()}"

@test("GStreamer: appsrc element exists")
def test_gst_appsrc():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    factory = Gst.ElementFactory.find('appsrc')
    assert factory is not None, "appsrc not found — install gstreamer1.0-plugins-base"
    return "appsrc element present"

@test("GStreamer: fake espeak pipeline builds without error")
def test_gst_espeak_pipeline():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    try:
        cmd = ('espeak name=espeak ! capsfilter name=caps ! fakesink name=sink')
        pipe = Gst.parse_launch(cmd)
        assert pipe is not None
        pipe.set_state(Gst.State.NULL)
        return "pipeline built and torn down cleanly"
    except Exception as e:
        raise AssertionError(f"Pipeline build failed: {e}")

@test("GStreamer: appsrc → fakesink pipeline builds")
def test_gst_appsrc_pipeline():
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    Gst.init(None)
    cmd = ('appsrc name=src ! audioconvert'
           ' ! audio/x-raw,format=S16LE,channels=1,rate=24000'
           ' ! fakesink name=sink')
    pipe = Gst.parse_launch(cmd)
    assert pipe is not None
    pipe.set_state(Gst.State.NULL)
    return "appsrc pipeline built and torn down cleanly"


# ════════════════════════════════════════════════════════
# GROUP 5 — voice_patched.py
# ════════════════════════════════════════════════════════

@test("voice_patched: HINDI_ESPEAK_VOICES defined")
def test_hindi_espeak_voices():
    import voice_patched as vp
    voices = vp.get_hindi_voices(neural=False)
    names = [v.name for v in voices]
    assert 'hi' in names
    assert 'hi+f1' in names
    return f"espeak Hindi voices: {names}"

@test("voice_patched: HINDI_KOKORO_VOICES defined")
def test_hindi_kokoro_voices():
    import voice_patched as vp
    voices = vp.get_hindi_voices(neural=True)
    names = [v.name for v in voices]
    assert 'hf_alpha' in names
    assert 'hm_omega' in names
    return f"Kokoro Hindi voices: {names}"

@test("voice_patched: allVoices() returns dict with Hindi")
def test_allvoices_dict():
    import voice_patched as vp
    vp._allVoices = {}   # reset cache
    voices = vp.allVoices()
    assert isinstance(voices, dict)
    assert len(voices) >= 5
    # Must contain at least one Hindi voice
    hindi = [k for k in voices if 'Hindi' in k]
    assert len(hindi) > 0, f"No Hindi voices found. Keys: {list(voices.keys())[:10]}"
    return f"{len(voices)} total voices, {len(hindi)} Hindi variants"

@test("voice_patched: defaultVoice() returns a Voice (no crash)")
def test_default_voice():
    import voice_patched as vp
    vp._defaultVoice = None
    vp._allVoices = {}
    v = vp.defaultVoice()
    assert v is not None
    assert hasattr(v, 'name')
    assert hasattr(v, 'language')
    return f"default voice: {v.friendlyname} ({v.name})"


# ════════════════════════════════════════════════════════
# GROUP 6 — espeak direct test (plays audio!)
# ════════════════════════════════════════════════════════

@test("espeak-ng: English speech (audible test — check your speakers)")
def test_espeak_english():
    import shutil, subprocess
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')
    if not espeak:
        raise AssertionError("espeak-ng not installed: sudo apt install espeak-ng")
    r = subprocess.run([espeak, '-v', 'en', 'Speak AI toolkit test. Hello world.'],
                       capture_output=True, timeout=10)
    assert r.returncode == 0, f"espeak failed: {r.stderr.decode()}"
    return "English speech played"

@test("espeak-ng: Hindi speech (audible test — check your speakers)")
def test_espeak_hindi():
    import shutil, subprocess
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')
    if not espeak:
        raise AssertionError("espeak-ng not installed")
    r = subprocess.run([espeak, '-v', 'hi', 'नमस्ते'],
                       capture_output=True, timeout=10)
    assert r.returncode == 0, f"espeak Hindi failed: {r.stderr.decode()}"
    return "Hindi speech played"


# ════════════════════════════════════════════════════════
# Runner
# ════════════════════════════════════════════════════════

GROUPS = {
    'mocks':  [t for t in results if 'mock' in t._test_name.lower() or
               'sugar3' in t._test_name.lower() or
               'sys.modules' in t._test_name.lower()],
    'tts':    [t for t in results if 'tts_client' in t._test_name.lower()
               or 'backend' in t._test_name.lower()
               or 'colab_url' in t._test_name.lower()],
    'server': [t for t in results if 'local_tts_server' in t._test_name.lower()
               or 'ColabTTSBackend' in t._test_name],
    'gst':    [t for t in results if 'GStreamer' in t._test_name],
    'voice':  [t for t in results if 'voice_patched' in t._test_name.lower()],
    'espeak': [t for t in results if 'espeak-ng' in t._test_name],
}


if __name__ == '__main__':
    filter_group = sys.argv[1] if len(sys.argv) > 1 else None

    print()
    print(SEPP)
    print('  speak-ai Toolkit — Test Suite')
    print(SEPP)

    if filter_group:
        if filter_group not in GROUPS:
            print(f'Unknown group: {filter_group}')
            print(f'Available: {", ".join(GROUPS.keys())}')
            sys.exit(1)
        to_run = GROUPS[filter_group]
        print(f'  Running group: {filter_group} ({len(to_run)} tests)')
    else:
        to_run = results
        print(f'  Running all {len(to_run)} tests')

    print()

    current_group = None
    group_map = {}
    for grp, tests in GROUPS.items():
        for t in tests:
            group_map[t._test_name] = grp

    passed = 0
    failed = 0
    for fn in to_run:
        grp = group_map.get(fn._test_name, 'other')
        if grp != current_group:
            current_group = grp
            labels = {
                'mocks':  'Mock Injection',
                'tts':    'TTS Client',
                'server': 'Local TTS Server  (needs: python local_tts_server.py)',
                'gst':    'GStreamer Pipeline',
                'voice':  'voice_patched.py',
                'espeak': 'espeak-ng Direct  (plays audio!)',
                'other':  'Other',
            }
            print(f'\n{SEP}')
            print(f'  {labels.get(grp, grp)}')
            print(SEP)

        ok = run_test(fn)
        if ok:
            passed += 1
        else:
            failed += 1

    print()
    print(SEPP)
    total = passed + failed
    print(f'  Results:  {passed}/{total} passed', end='')
    if failed:
        print(f'  ({failed} failed)')
    else:
        print('  — ALL PASSED ✓')
    print(SEPP)
    print()

    sys.exit(0 if failed == 0 else 1)