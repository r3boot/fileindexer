
import os
import time

import Queue
import whoosh.index
import whoosh.fields
import whoosh.writing
import whoosh.qparser

class WhooshIndex:
    _index_name = 'fileindexer'
    _schema = whoosh.fields.Schema(
        url=whoosh.fields.TEXT(stored=True),
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

    def __init__(self, logger, index_base='/data1'):
        self.__l = logger
        self._idx_dir = os.path.join(index_base, self._index_name)
        self.idx = None
        self.qparser = None
        self.writer = None
        self.batch = []
        self.batch_cnt = 0
        self.__q = Queue.Queue()
        self.open_index()

    def __destroy__(self):
        if self.idx:
            self.idx.close()

    def _process_results(self):
        pass

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
        self.writer = whoosh.writing.BufferedWriter(self.idx, period=60, limit=10000)
        self.qparser = whoosh.qparser.QueryParser('url', schema=self._schema)

    def query(self, query):
        results = {
            'documents': [],
            'hits': 0
        }
        q = self.qparser.parse(query)
        with self.idx.searcher() as s:
            r = s.search(q)
            for (docid, raw_doc) in enumerate(r):
                raw_doc = dict(raw_doc)
                results['documents'].append(raw_doc)
                results['hits'] += 1
       
        return results