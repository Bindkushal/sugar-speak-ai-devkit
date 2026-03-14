# sugar-speak-ai-devkit

A developer toolkit for running and testing [speak-ai](https://github.com/sugarlabs/speak-ai)
locally in VS Code — without the Sugar desktop, D-Bus, or Telepathy.

Built for GSoC contributors who want to develop and test speak-ai on any machine.

---

## The Problem

speak-ai depends on the full Sugar desktop environment to run. Cloning the repo
and typing `python activity.py` crashes immediately with `dbus`, `sugar3`, and
`TelepathyGLib` import errors. This makes local development nearly impossible
without a Sugar VM or live build.

This toolkit fixes that.

---

## What's Inside

| File | Purpose |
|---|---|
| `run_local.py` | Launch speak-ai in a plain GTK window |
| `check_hardware.py` | Detects your RAM and recommends a setup path |
| `test_toolkit.py` | Full test suite — works on 4 GB RAM, no torch needed |
| `local_tts_server.py` | espeak TTS server (API-compatible with Colab) |
| `tts_client.py` | Auto-selects Colab / Kokoro / espeak TTS backend |
| `speech_patched.py` | Drop-in `speech.py` with Hindi + backend support |
| `voice_patched.py` | Drop-in `voice.py` with Hindi voices wired in |
| `colab_tts_server.ipynb` | Kokoro TTS server on Google Colab (free GPU) |
| `dbus_mock.py` | Silences `dbus` import errors |
| `telepathy_mock.py` | Silences `TelepathyGLib` import errors |
| `sugar3_mock/` | Full Sugar3 stubs (activity, graphics, presence, etc.) |
| `requirements_full.txt` | Path A: full install with Kokoro + torch |
| `requirements_light.txt` | Path B: lightweight install, TTS on Colab |

---

## Quick Start
```bash
# 1. Clone speak-ai
git clone https://github.com/sugarlabs/speak-ai
cd speak-ai

# 2. Copy this toolkit into the repo root
git clone https://github.com/Bindkushal/sugar-speak-ai-devkit
cp -r sugar-speak-ai-devkit/* .

# 3. Check your hardware
python check_hardware.py
```

Then follow **[README_LOCAL.md](README_LOCAL.md)** for step-by-step setup.

---

## Two Paths — Any Hardware

**Path A (12+ GB RAM)** — Kokoro neural TTS runs locally on your machine.

**Path B (4 GB RAM)** — GTK face and chat run locally, Kokoro runs free on
Google Colab. Your machine sends text → gets audio back → plays it.
No torch, no heavy install locally.

---

## Testing on 4 GB RAM
```bash
pip install -r requirements_light.txt

python test_toolkit.py mocks    # Sugar3/dbus mock injection
python test_toolkit.py tts      # TTS client auto-detection
python test_toolkit.py gst      # GStreamer pipeline build
python test_toolkit.py voice    # Hindi voice list

# Full Path B end-to-end (two terminals):
python local_tts_server.py      # Terminal 1
python test_toolkit.py server   # Terminal 2
```

---

## Hindi Support

| Voice | Backend | Quality |
|---|---|---|
| espeak `hi`, `hi+f1`, `hi+f2` | Built-in, zero deps | Functional |
| Kokoro `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi` | Path A or Colab | Neural |

---

## Related

- [sugarlabs/speak-ai](https://github.com/sugarlabs/speak-ai) — the activity this toolkit targets
- [sugar-activity-devkit](https://github.com/Bindkushal/sugar-activity-devkit) — generic Sugar activity local dev toolkit

---

## License

GPL-3.0 — same as speak-ai
