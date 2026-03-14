#!/usr/bin/env python3
"""
check_hardware.py — Run this first to know which path to take.
Usage: python check_hardware.py
"""

import sys, os, shutil, platform

SEP  = '─' * 55
SEPP = '═' * 55

def mb(b): return round(b / 1024**2)
def gb(b): return round(b / 1024**3, 1)

print()
print(SEPP)
print('  speak-ai Hardware Check')
print(SEPP)

# ── RAM ──────────────────────────────────────────────────────
try:
    import psutil
    ram_gb = gb(psutil.virtual_memory().total)
    ram_avail = gb(psutil.virtual_memory().available)
    print(f'\n  RAM:       {ram_gb} GB total,  {ram_avail} GB free')
except ImportError:
    try:
        with open('/proc/meminfo') as f:
            lines = f.read().splitlines()
        total = int([l for l in lines if l.startswith('MemTotal')][0].split()[1]) // 1024
        avail = int([l for l in lines if l.startswith('MemAvailable')][0].split()[1]) // 1024
        ram_gb = round(total / 1024, 1)
        ram_avail = round(avail / 1024, 1)
        print(f'\n  RAM:       {ram_gb} GB total,  {ram_avail} GB free')
    except Exception:
        ram_gb = 0
        print('\n  RAM:       unknown')

# ── GPU ──────────────────────────────────────────────────────
gpu_name = None
try:
    import subprocess
    r = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total',
                        '--format=csv,noheader'], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        gpu_name = r.stdout.strip()
        print(f'  GPU:       {gpu_name}')
    else:
        print('  GPU:       None detected (CPU only)')
except Exception:
    print('  GPU:       None detected (CPU only)')

# ── Python ───────────────────────────────────────────────────
print(f'  Python:    {sys.version.split()[0]}')
print(f'  OS:        {platform.system()} {platform.release()}')

# ── Key packages ─────────────────────────────────────────────
print(f'\n{SEP}')
print('  Package availability:')

packages = [
    ('torch',         'torch'),
    ('kokoro',        'kokoro'),
    ('soundfile',     'soundfile'),
    ('flask',         'flask'),
    ('requests',      'requests'),
    ('numpy',         'numpy'),
    ('gi (PyGObject)','gi'),
]
for label, mod in packages:
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', '?')
        print(f'    ✓  {label:<22} {ver}')
    except ImportError:
        print(f'    ✗  {label:<22} not installed')

# ── System tools ─────────────────────────────────────────────
print(f'\n{SEP}')
print('  System tools:')
tools = [
    ('espeak-ng',                   'espeak-ng'),
    ('espeak',                      'espeak'),
    ('gst-inspect-1.0',             'gst-inspect-1.0'),
]
for label, cmd in tools:
    found = shutil.which(cmd)
    status = f'✓  {found}' if found else '✗  not found'
    print(f'    {status}  ({label})')

# ── Recommendation ───────────────────────────────────────────
print(f'\n{SEPP}')

if ram_gb >= 12 or gpu_name:
    print('  RECOMMENDATION:  PATH A  — Full local setup')
    print()
    print('  Your machine has enough resources to run Kokoro TTS locally.')
    print()
    print('  Install:')
    print('    pip install -r requirements_full.txt')
    print('  Run:')
    print('    python run_local.py')

elif 0 < ram_gb < 12:
    print('  RECOMMENDATION:  PATH B  — Colab TTS backend')
    print()
    print(f'  Your machine has {ram_gb} GB RAM. torch + kokoro need 4–8 GB.')
    print('  Use Google Colab to run TTS in the cloud for free.')
    print()
    print('  Install (lightweight):')
    print('    pip install -r requirements_light.txt')
    print('  Then open colab_tts_server.ipynb in Google Colab.')
    print('  Copy the URL → paste into colab_url.txt → python run_local.py')

else:
    print('  Could not detect RAM. Try PATH B (Colab) to be safe.')

print()
print('  Both paths:  sudo apt install -y espeak-ng gstreamer1.0-espeak')
print('               gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0')
print(SEPP)
print()