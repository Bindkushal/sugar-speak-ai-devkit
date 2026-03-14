#!/bin/bash
# sync.sh — copy devkit files into speak-ai and apply patches
# Usage: bash sync.sh /path/to/speak-ai
# Default: ~/Desktop/speak-ai

SPEAK_AI=${1:-~/Desktop/speak-ai}
SPEAK_AI=$(eval echo $SPEAK_AI)
DEVKIT=$(dirname $(realpath $0))

echo "Syncing devkit → $SPEAK_AI"

# Copy all devkit files
cp -r $DEVKIT/sugar3_mock $SPEAK_AI/
cp $DEVKIT/run_local.py $SPEAK_AI/
cp $DEVKIT/dbus_mock.py $SPEAK_AI/
cp $DEVKIT/telepathy_mock.py $SPEAK_AI/
cp $DEVKIT/tts_client.py $SPEAK_AI/
cp $DEVKIT/check_hardware.py $SPEAK_AI/
cp $DEVKIT/local_tts_server.py $SPEAK_AI/
cp $DEVKIT/test_toolkit.py $SPEAK_AI/
cp $DEVKIT/voice_patched.py $SPEAK_AI/
cp $DEVKIT/speech_patched.py $SPEAK_AI/
cp $DEVKIT/colab_tts_server.ipynb $SPEAK_AI/
cp $DEVKIT/requirements*.txt $SPEAK_AI/

# Apply patched files
cp $DEVKIT/speech_patched.py $SPEAK_AI/speech.py
cp $DEVKIT/voice_patched.py $SPEAK_AI/voice.py

# Apply GenAI patch
python3 $DEVKIT/fix_genai.py

echo "✓ Sync done. Now run: cd $SPEAK_AI && python run_local.py"
