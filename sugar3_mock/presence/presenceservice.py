# sugar3_mock/presence/presenceservice.py

class _MockProps:
    nick = 'User'
    color = '#8b0000,#1e90ff'

class _MockOwner:
    def __init__(self):
        self.props = _MockProps()

    def get_key(self):
        return ''

    def get_color(self):
        return self.props.color

    def get_nick(self):
        return self.props.nick

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
