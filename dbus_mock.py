# dbus_mock.py
# Replaces the `dbus` module for local development.
# speak-ai uses dbus only for Sugar XMPP collaboration — stubbed out entirely.

PROPERTIES_IFACE = 'org.freedesktop.DBus.Properties'

class _NullInterface:
    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None
        return _noop

class _NullObject(_NullInterface):
    pass

class Bus:
    SESSION   = 0
    SYSTEM    = 1
    STARTER   = 2

    def __init__(self, bus_type=None):
        pass

    def get_object(self, bus_name, object_path):
        return _NullObject()

    def add_signal_receiver(self, *args, **kwargs):
        pass

    def remove_signal_receiver(self, *args, **kwargs):
        pass

class Interface(_NullInterface):
    def __init__(self, obj=None, dbus_interface=None):
        pass

class SessionBus(Bus):
    def __init__(self):
        Bus.__init__(self, Bus.SESSION)

class SystemBus(Bus):
    def __init__(self):
        Bus.__init__(self, Bus.SYSTEM)

class DBusException(Exception):
    pass

class service:
    class Object:
        def __init__(self, bus=None, path=None):
            pass

class gobject_service:
    class ExportedGObject:
        def __init__(self, bus=None, path=None):
            pass