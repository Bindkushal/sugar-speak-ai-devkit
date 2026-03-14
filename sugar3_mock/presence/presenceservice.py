# sugar3_mock/presence/presenceservice.py
# Stub for sugar3.presence.presenceservice
# In local mode there is no XMPP / collaboration.

class _MockOwner:
    """Fake 'owner' buddy returned by presenceservice."""
    def get_key(self):
        return ''
    def get_color(self):
        return '#8b0000,#1e90ff'
    def props(self):
        return self
    nick = 'User'
    color = '#8b0000,#1e90ff'

class _MockPresenceService:
    def __init__(self):
        self._owner = _MockOwner()

    def get_owner(self):
        return self._owner

    def get_buddies(self):
        return []

    def connect(self, *args, **kwargs):
        pass

_instance = None

def get_instance():
    global _instance
    if _instance is None:
        _instance = _MockPresenceService()
    return _instance