# This script patches GenAI/__init__.py in speak-ai
# to not crash when llama-cpp-python is not installed
import os

target = os.path.join(os.path.dirname(__file__), 'GenAI', '__init__.py')
if not os.path.exists(target):
    print(f"GenAI/__init__.py not found at {target}")
else:
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
    print(f"Patched {target}")
