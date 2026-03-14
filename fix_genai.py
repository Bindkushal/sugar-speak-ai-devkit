import os
import sys

# Target is speak-ai dir passed as argument, or auto-detect
if len(sys.argv) > 1:
    speak_ai_dir = sys.argv[1]
else:
    speak_ai_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'speak-ai')
    speak_ai_dir = os.path.realpath(speak_ai_dir)

target = os.path.join(speak_ai_dir, 'GenAI', '__init__.py')

if not os.path.exists(target):
    print(f"Not found: {target}")
    sys.exit(1)

with open(target, 'w') as f:
    f.write("""# Copyright (C) 2025, Mebin J Thattil <mail@mebin.in>
# GPL-3.0 — see COPYING for details

try:
    from .gguf_inference import load_gguf_model
    GGUF_AVAILABLE = True
except ImportError:
    GGUF_AVAILABLE = False
    load_gguf_model = None

from .profainity_check import *
""")
print(f"✓ Patched {target}")
