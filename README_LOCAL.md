# speak-ai — Local Developer Toolkit

Run the full speak-ai GTK activity in **VS Code on plain Ubuntu** — no Sugar desktop,  
no D-Bus, no Telepathy. Works for **any contributor**, regardless of hardware.

---

## ⚡ Quick Start (30 seconds)

```bash
# 1. Clone speak-ai
git clone https://github.com/sugarlabs/speak-ai && cd speak-ai

# 2. Copy this toolkit into the repo root
cp -r /path/to/speak-ai-toolkit/* .

# 3. Check your hardware
python check_hardware.py
```

The hardware check will tell you exactly which path to follow.

---

## 🔀 Two Paths

```
                 python check_hardware.py
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
   RAM ≥ 12 GB                      RAM < 12 GB
   (or has GPU)                     (4 GB etc.)
          │                               │
      PATH A                         PATH B
  Full local setup               Colab TTS backend
  Kokoro runs on                 Kokoro runs FREE
  your machine                   on Google Colab
```

---

## PATH A — Full Local (12+ GB RAM or GPU)

> ⚠️ **WARNING: ~2–4 GB will be downloaded**
> - `torch`: 700 MB – 2 GB depending on CUDA
> - Kokoro TTS models: ~500 MB (on first run, cached after)
> - `transformers` models: ~500 MB+
>
> Make sure you have a stable internet connection and enough disk space (~5 GB free).

### 1 — System dependencies (one time)
```bash
sudo apt install -y \
  espeak-ng \
  gstreamer1.0-espeak \
  gir1.2-gstreamer-1.0 \
  gir1.2-gst-plugins-base-1.0 \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-base \
  python3-gi python3-gi-cairo
```

### 2 — Python dependencies
```bash
pip install -r requirements_full.txt
```

### 3 — Copy patched files
```bash
cp speech_patched.py speech.py
cp voice_patched.py voice.py
```

### 4 — Run
```bash
python run_local.py
```

VS Code: open the `speak-ai/` folder, then run in the integrated terminal.

### Optional: Enable Hindi Kokoro voices
```bash
export SPEAK_AI_TTS=kokoro   # force kokoro backend
python run_local.py
```
Select `Hindi Neural (hf_alpha)` etc. from the voice dropdown.

---

## PATH B — Colab TTS Backend (4 GB RAM, no GPU)

The GTK face, chat UI, and espeak all run **locally** on your machine (lightweight).  
Only the heavy Kokoro neural TTS runs on **Google Colab's free GPU/CPU**.

> ℹ️ No torch, no kokoro installed on your machine. Total local install: ~50 MB.

### 1 — System dependencies (same as above)
```bash
sudo apt install -y espeak-ng gstreamer1.0-espeak \
  gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-base \
  python3-gi python3-gi-cairo
```

### 2 — Lightweight Python dependencies
```bash
pip install -r requirements_light.txt
```

### 3 — Copy patched files
```bash
cp speech_patched.py speech.py
cp voice_patched.py voice.py
```

### 4 — Set up Google Colab TTS server

**Step 4a** — Upload `colab_tts_server.ipynb` to [Google Colab](https://colab.research.google.com)  
or open it directly from Google Drive.

**Step 4b** — Get a free ngrok auth token:  
Go to [dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)  
(free account, takes 1 minute)

**Step 4c** — In the notebook, paste your token into Cell 4:
```python
NGROK_TOKEN = 'your_token_here'   # ← replace this
```

**Step 4d** — Run all cells top to bottom (Ctrl+F9).  
Cell 4 will print something like:
```
══════════════════════════════════════════════════════════
  ✓ Kokoro TTS server running!
  ✓ Public URL: https://abc123.ngrok-free.app

  ► On your local machine:
    echo "https://abc123.ngrok-free.app" > colab_url.txt
    python run_local.py
══════════════════════════════════════════════════════════
```

**Step 4e** — On your local machine, inside `speak-ai/`:
```bash
echo "https://abc123.ngrok-free.app" > colab_url.txt
```

### 5 — Run
```bash
python run_local.py
```

speak-ai automatically detects `colab_url.txt` and routes all neural TTS to Colab.  
Espeak still works offline as a fallback.

### If Colab restarts
Re-run **Cells 3 and 4** only. Update `colab_url.txt` with the new URL:
```bash
echo "https://newurl.ngrok-free.app" > colab_url.txt
```

---

## 🇮🇳 Hindi Support

| Voice type | Backend needed | Quality | Command |
|---|---|---|---|
| espeak Hindi | None (built-in) | Robotic but functional | Select "Hindi" in voice dropdown |
| espeak Hindi variants | None | Slightly varied | Select "Hindi (Female 1)" etc. |
| Kokoro Hindi (hf_alpha) | PATH A or PATH B | Natural, neural | Select "Hindi Neural (hf_alpha)" |
| Kokoro Hindi (hf_beta, hm_omega, hm_psi) | PATH A or PATH B | Natural, neural | Select from voice dropdown |

---

## 📁 File Structure

```
speak-ai/
├── run_local.py              ← Main launcher
├── check_hardware.py         ← Run this first
├── tts_client.py             ← TTS backend abstraction
├── speech_patched.py         ← Copy to speech.py
├── voice_patched.py          ← Copy to voice.py
├── colab_tts_server.ipynb    ← Upload to Google Colab (Path B)
├── colab_url.txt             ← Paste ngrok URL here (Path B, not committed)
├── dbus_mock.py              ← Silences dbus import errors
├── telepathy_mock.py         ← Silences TelepathyGLib import errors
├── requirements_full.txt     ← Path A: full heavy deps
├── requirements_light.txt    ← Path B: lightweight deps
└── sugar3_mock/              ← Sugar3 stubs
    ├── __init__.py           ← profile, mime
    ├── activity/             ← Activity base class, widgets
    ├── graphics/             ← style, ToolButton, ToolbarBox, etc.
    ├── presence/             ← presenceservice stub
    ├── datastore/            ← datastore stub (no-op)
    └── speech/               ← GstSpeechPlayer stub
```

---

## 🔧 TTS Backend Selection

| Env var | Effect |
|---|---|
| `SPEAK_AI_TTS=auto` | Auto-detect: Colab → Kokoro → espeak (default) |
| `SPEAK_AI_TTS=colab` | Force Colab backend (needs `colab_url.txt` or `COLAB_TTS_URL`) |
| `SPEAK_AI_TTS=kokoro` | Force local Kokoro (needs torch + kokoro installed) |
| `SPEAK_AI_TTS=espeak` | Force espeak (always works, no deps) |
| `COLAB_TTS_URL=https://...` | Colab URL via env instead of colab_url.txt |

---

## ✅ Feature Status

| Feature | Path A | Path B |
|---|---|---|
| GTK face animation | ✅ | ✅ |
| espeak English TTS | ✅ | ✅ |
| espeak Hindi TTS | ✅ | ✅ |
| Kokoro English (neural) | ✅ | ✅ via Colab |
| Kokoro Hindi (neural) | ✅ | ✅ via Colab |
| LLM chat (API) | ✅ | ✅ |
| Local GGUF inference | ✅ | ⚠️ slow |
| Sugar collaboration | 🔇 stubbed | 🔇 stubbed |
| Sugar Journal | 🔇 no-op | 🔇 no-op |

---

## 🐛 Troubleshooting

**`No module named 'gi'`**
```bash
sudo apt install python3-gi python3-gi-cairo
```

**`espeak element not found` (GStreamer)**
```bash
sudo apt install gstreamer1.0-espeak
gst-inspect-1.0 espeak   # should show the plugin
```

**`Kokoro ImportError`** — You're on Path B, this is expected. Use Colab.

**`Colab TTS not reachable`** — Check `colab_url.txt` has the latest ngrok URL.  
Cell 4 must still be running in the Colab tab.

**Window opens but no sound** — Check GStreamer:
```bash
gst-inspect-1.0 autoaudiosink
gst-inspect-1.0 espeak
```

**`SpeakActivity.__init__` crash** — Paste the full traceback; likely a missing sugar3 stub.  
Open an issue or add the missing stub to `sugar3_mock/`.