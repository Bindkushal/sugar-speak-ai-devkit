# sugar3_mock/__init__.py
# Minimal Sugar3 mock for running speak-ai outside the Sugar desktop.

class _MockColor:
    def __init__(self, stroke='#8b0000', fill='#1e90ff'):
        self._stroke = stroke
        self._fill = fill
    def to_string(self):
        return f'{self._stroke},{self._fill}'
    def get_stroke_color(self):
        return self._stroke
    def get_fill_color(self):
        return self._fill

class profile:
    @staticmethod
    def get_color():
        return _MockColor()
    @staticmethod
    def get_nick_name():
        return 'User'
    @staticmethod
    def get_pubkey():
        return ''

class mime:
    @staticmethod
    def get_for_file(path):
        return 'application/octet-stream'
    @staticmethod
    def get_mime_types_for_file(path):
        return ['application/octet-stream']