
import os

import whoosh.index
import whoosh.fields
import whoosh.writing

class WhooshIndex:
    _index_name = 'fileindexer'
    _schema = whoosh.fields.Schema(
        filename=whoosh.fields.TEXT(stored=True),
        atime=whoosh.fields.DATETIME(stored=True),
        ctime=whoosh.fields.DATETIME(stored=True),
        parent=whoosh.fields.TEXT(stored=True),
        gid=whoosh.fields.NUMERIC(stored=True),
        mode=whoosh.fields.NUMERIC(stored=True),
        mtime=whoosh.fields.DATETIME(stored=True),
        is_dir=whoosh.fields.BOOLEAN(stored=True),
        size=whoosh.fields.NUMERIC(stored=True),
        uid=whoosh.fields.NUMERIC(stored=True)
    )

    def __init__(self, logger, index_base='/tmp'):
        self.__l = logger
        self._idx_dir = os.path.join(index_base, self._index_name)
        self.idx = None
        self.writer = None
        self.open_index()

    def __destroy__(self):
        if self.idx:
            self.idx.close()

    def has_index(self):
        if not os.path.exists(self._idx_dir):
            return False
        if whoosh.index.exists_in(self._idx_dir):
            return True
        return False

    def create_index(self):
        if self.has_index():
            self.__l.error('Index already exists')
        else:
            if not os.path.exists(self._idx_dir):
                self.__l.debug('Creating %s' % self._idx_dir)
                os.mkdir(self._idx_dir)
            self.__l.debug('Creating index %s' % self._index_name)
            self.idx = whoosh.index.create_in(self._idx_dir, self._schema)

    def open_index(self):
        if self.has_index():
            self.idx = whoosh.index.open_dir(self._idx_dir)
        else:
            self.create_index()
        self.writer = whoosh.writing.BufferedWriter(self.idx, period=30, limit=100)

    def commit(self):
        if not self.writer:
            self.__l.error('Cannot commit, no writer')
        else:
            self.writer.commit()

    def merge(self):
        if not self.writer:
            self.__l.error('Cannot merge, no writer')
        else:
            self.writer.commit(merge=True)

    def optimize_index(self):
        if not self.writer:
            self.__l.error('Cannot optimize index, no writer')
        else:
            self.writer.commit(optimize=True)

    def add_document(self, *args, **kwargs):
        if not self.writer:
            self.__l.error('Cannot add, no writer')
        else:
            self.writer.add_document(**kwargs)
