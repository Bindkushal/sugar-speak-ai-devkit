# sugar3_mock/activity/activity.py
import os
from gi.repository import GLib

_ACTIVITY_ROOT = os.path.join(GLib.get_user_data_dir(), 'speak-ai-local')

def get_activity_root():
    os.makedirs(_ACTIVITY_ROOT, exist_ok=True)
    return _ACTIVITY_ROOT

def show_object_in_journal(object_id):
    """No-op: no Sugar journal in local mode."""
    pass