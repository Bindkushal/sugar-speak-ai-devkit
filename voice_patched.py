# voice_patched.py  —  Drop-in replacement for speak-ai/voice.py
# ==============================================================
# Changes from original:
#   1. Hindi espeak voice added as a proper Voice object
#   2. get_hindi_voices() helper for UI dropdowns
#   3. defaultVoice() falls back gracefully when get_all_voices() is missing
#      (happens when running with sugar3_mock / espeak unavailable)
# ==============================================================

import re
import os
from gettext import gettext as _

import logging
logger = logging.getLogger('speak')

expectedVoiceNames = [
    _("Portuguese (Brazil)"), _("Swedish"), _("Icelandic"),
    _("Romanian"), _("Swahili"), _("Hindi"), _("Dutch"),
    _("Latin"), _("Hungarian"), _("Macedonian"), _("Welsh"),
    _("French"), _("Norwegian"), _("Russian"), _("Afrikaans"),
    _("Finnish"), _("Default"), _("Cantonese"), _("Scottish"),
    _("Greek"), _("Vietnamese"), _("English"), _("Lancashire"),
    _("Italian"), _("Portuguese"), _("German"), _("Whisper"),
    _("Croatian"), _("Czech"), _("Slovak"), _("Spanish"),
    _("Polish"), _("Esperanto"),
]

_allVoices = {}
_defaultVoice = None


def _friendly_name(full_name):
    parts = re.split('[ _-]', full_name)
    short_name = _(parts[0].capitalize())
    return ' '.join([short_name] + parts[1:])


class Voice:
    def __init__(self, language, name, friendlyname_override=None):
        self.language = language
        self.name = name

        friendlyname = name
        friendlyname = friendlyname.replace('-test', '')
        friendlyname = friendlyname.replace('_test', '')
        friendlyname = friendlyname.replace('en-', '')
        friendlyname = friendlyname.replace('english-wisper', 'whisper')
        friendlyname = friendlyname.replace('english-us', 'us')

        friendlynameRP = name
        friendlynameRP = friendlynameRP.replace('english_rp', 'rp')
        friendlynameRP = friendlynameRP.replace('english_wmids', 'wmids')

        parts = re.split('[ _-]', friendlyname)
        self.short_name = _(parts[0].capitalize())
        self.friendlyname = ' '.join([self.short_name] + parts[1:])

        if friendlynameRP == 'rp':
            self.friendlyname = 'English (Received Pronunciation)'
        if friendlyname == 'us':
            self.friendlyname = 'English (USA)'
        if friendlynameRP == 'wmids':
            self.friendlyname = 'English (West Midlands)'

        # Allow explicit override (used for Hindi variants)
        if friendlyname_override:
            self.friendlyname = friendlyname_override

    def __lt__(self, other):
        return self.friendlyname < other.friendlyname


# ── Hindi voice definitions ──────────────────────────────────
# espeak-ng lang code 'hi' — no extra deps required
HINDI_ESPEAK_VOICES = [
    Voice('hi', 'hi',      'Hindi'),
    Voice('hi', 'hi+f1',   'Hindi (Female 1)'),
    Voice('hi', 'hi+f2',   'Hindi (Female 2)'),
    Voice('hi', 'hi+m1',   'Hindi (Male 1)'),
    Voice('hi', 'hi+m2',   'Hindi (Male 2)'),
]

# Kokoro Hindi voices — available when TTS backend is Kokoro or Colab
HINDI_KOKORO_VOICES = [
    Voice('hi', 'hf_alpha', 'Hindi Neural (hf_alpha)'),
    Voice('hi', 'hf_beta',  'Hindi Neural (hf_beta)'),
    Voice('hi', 'hm_omega', 'Hindi Neural (hm_omega)'),
    Voice('hi', 'hm_psi',   'Hindi Neural (hm_psi)'),
]


def get_hindi_voices(neural=False):
    """
    Returns Hindi Voice objects.
    neural=False  → espeak Hindi (always available)
    neural=True   → Kokoro Hindi (requires neural TTS backend)
    """
    return HINDI_KOKORO_VOICES if neural else HINDI_ESPEAK_VOICES


def allVoices():
    global _allVoices
    if _allVoices:
        return _allVoices

    # Try loading espeak voices via speech module
    try:
        import speech as _speech_mod
        sp = _speech_mod.get_speech()
        if hasattr(sp, 'get_all_voices'):
            voice_list = sp.get_all_voices()
            for language, name in voice_list.items():
                voice = Voice(language, name)
                _allVoices[voice.friendlyname] = voice
    except Exception as e:
        logger.warning(f'Could not load espeak voice list: {e}')

    # Always inject a basic English fallback so the UI never breaks
    en_key = _friendly_name('English')
    if en_key not in _allVoices:
        _allVoices[en_key] = Voice('en', 'en', 'English')

    # Inject common espeak voices so the UI never has KeyError
    fallback_voices = [
        Voice('en', 'en',          'English'),
        Voice('en', 'en-us',       'English (America)'),
        Voice('en', 'en-gb',       'English (Great Britain)'),
        Voice('es', 'es',          'Spanish'),
        Voice('es', 'es-la',       'Spanish (Latin America)'),
        Voice('fr', 'fr',          'French'),
        Voice('de', 'de',          'German'),
        Voice('it', 'it',          'Italian'),
        Voice('pt', 'pt',          'Portuguese'),
        Voice('pt', 'pt-br',       'Portuguese (Brazil)'),
        Voice('ru', 'ru',          'Russian'),
        Voice('zh', 'zh',          'Cantonese'),
        Voice('sv', 'sv',          'Swedish'),
        Voice('nl', 'nl',          'Dutch'),
        Voice('pl', 'pl',          'Polish'),
        Voice('fi', 'fi',          'Finnish'),
        Voice('hu', 'hu',          'Hungarian'),
        Voice('el', 'el',          'Greek'),
        Voice('ro', 'ro',          'Romanian'),
        Voice('cs', 'cs',          'Czech'),
        Voice('sk', 'sk',          'Slovak'),
        Voice('hr', 'hr',          'Croatian'),
        Voice('af', 'af',          'Afrikaans'),
        Voice('sw', 'sw',          'Swahili'),
        Voice('cy', 'cy',          'Welsh'),
        Voice('la', 'la',          'Latin'),
        Voice('eo', 'eo',          'Esperanto'),
        Voice('vi', 'vi',          'Vietnamese'),
        Voice('is', 'is',          'Icelandic'),
        Voice('mk', 'mk',          'Macedonian'),
        Voice('no', 'no',          'Norwegian'),
        Voice('en', 'whisper',     'Whisper'),
    ]
    for v in fallback_voices:
        if v.friendlyname not in _allVoices:
            _allVoices[v.friendlyname] = v

    # Inject Hindi espeak voices
    for v in HINDI_ESPEAK_VOICES:
        _allVoices[v.friendlyname] = v

    return _allVoices


def by_name(name):
    return allVoices().get(name, defaultVoice())


def defaultVoice():
    global _defaultVoice
    if _defaultVoice:
        return _defaultVoice

    voices = allVoices()

    def fit(a, b):
        as_ = re.split(r'[^a-z]+', a.lower())
        bs  = re.split(r'[^a-z]+', b.lower())
        for count in range(0, min(len(as_), len(bs))):
            if as_[count] != bs[count]:
                count -= 1
                break
        return count

    try:
        lang = os.environ.get('LANG', 'en')
    except Exception:
        lang = 'en'

    # Preferred fallback order
    voice_names = [
        _friendly_name('English (America)'),
        _friendly_name('English'),
        _friendly_name('Default'),
    ]

    best = None
    for vname in voice_names:
        if vname in voices:
            best = voices[vname]
            break

    if best is None:
        # Last resort — first voice in the dict
        best = next(iter(voices.values()))

    # Check if system LANG matches a better voice
    for voice in list(voices.values()):
        try:
            if fit(voice.language, lang) > fit(best.language, lang):
                best = voice
        except Exception:
            pass

    _defaultVoice = best
    return best