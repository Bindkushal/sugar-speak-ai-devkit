# telepathy_mock.py
# Replaces TelepathyGLib (gi.repository.TelepathyGLib) for local development.
# speak-ai uses Telepathy only for Sugar XMPP collaboration — all stubbed.

# Interface name constants used in activity.py
IFACE_CHANNEL                        = 'org.freedesktop.Telepathy.Channel'
IFACE_CHANNEL_INTERFACE_GROUP        = 'org.freedesktop.Telepathy.Channel.Interface.Group'
IFACE_CHANNEL_TYPE_TEXT              = 'org.freedesktop.Telepathy.Channel.Type.Text'
IFACE_CONNECTION                     = 'org.freedesktop.Telepathy.Connection'
IFACE_CONNECTION_INTERFACE_ALIASING  = 'org.freedesktop.Telepathy.Connection.Interface.Aliasing'

class ChannelGroupFlags:
    CHANNEL_SPECIFIC_HANDLES = 0x00000400

class ChannelTextMessageType:
    NORMAL = 0

class _Null:
    """Catch-all null object for any other Telepathy attribute access."""
    def __getattr__(self, name):
        return _Null()
    def __call__(self, *a, **kw):
        return _Null()
    def __int__(self):
        return 0
    def __str__(self):
        return ''