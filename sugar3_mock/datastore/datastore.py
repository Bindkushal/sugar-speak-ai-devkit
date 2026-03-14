# sugar3_mock/datastore/datastore.py
# Stub for sugar3.datastore.datastore
# No journal in local mode - all operations are no-ops.

class _MockJobject:
    def __init__(self):
        self.object_id = 'local-0001'
        self.metadata = {}
        self.file_path = None

    def set_file_path(self, path):
        self.file_path = path

    def destroy(self):
        pass

def create():
    return _MockJobject()

def write(jobject, update_mtime=True, reply_handler=None, error_handler=None):
    """No-op write."""
    pass

def get(object_id):
    return _MockJobject()