
import os
import time

import Queue
import whoosh.index
import whoosh.fields
import whoosh.writing
import whoosh.qparser

class WhooshIndex:
    _index_name = 'index'
    _schema = whoosh.fields.Schema(
        url=whoosh.fields.TEXT(stored=True),
        full_path=whoosh.fields.TEXT(stored=True), ## TODO: remove
        filename=whoosh.fields.TEXT(stored=True),
        atime=whoosh.fields.NUMERIC(stored=True), ## TODO: convert to DATETIME
        ctime=whoosh.fields.NUMERIC(stored=True), ## TODO: convert to DATETIME
        gid=whoosh.fields.NUMERIC(stored=True),
        mode=whoosh.fields.NUMERIC(stored=True),
        mtime=whoosh.fields.NUMERIC(stored=True), ## TODO: convert to DATETIME
        is_dir=whoosh.fields.BOOLEAN(stored=True),
        size=whoosh.fields.NUMERIC(stored=True),
        uid=whoosh.fields.NUMERIC(stored=True),
        checksum=whoosh.fields.TEXT(stored=True),
        file=whoosh.fields.TEXT(stored=True),
        mime=whoosh.fields.TEXT(stored=True),
        bitrate=whoosh.fields.TEXT(stored=True),
        channel=whoosh.fields.TEXT(stored=True),
        comment=whoosh.fields.TEXT(stored=True),
        compression=whoosh.fields.TEXT(stored=True),
        duration=whoosh.fields.TEXT(stored=True),
        endianness=whoosh.fields.TEXT(stored=True),
        framerate=whoosh.fields.TEXT(stored=True),
        height=whoosh.fields.TEXT(stored=True),
        author=whoosh.fields.TEXT(stored=True),
        artist=whoosh.fields.TEXT(stored=True),
        album=whoosh.fields.TEXT(stored=True),
        language=whoosh.fields.TEXT(stored=True),
        producer=whoosh.fields.TEXT(stored=True),
        samplerate=whoosh.fields.TEXT(stored=True),
        title=whoosh.fields.TEXT(stored=True),
        width=whoosh.fields.TEXT(stored=True),
        audio_bitrate=whoosh.fields.TEXT(stored=True),
        audio_channel=whoosh.fields.TEXT(stored=True),
        audio_compression_rate=whoosh.fields.TEXT(stored=True),
        audio_compression=whoosh.fields.TEXT(stored=True),
        audio_duration=whoosh.fields.TEXT(stored=True),
        audio_language=whoosh.fields.TEXT(stored=True),
        audio_samplerate=whoosh.fields.TEXT(stored=True),
        audio_title=whoosh.fields.TEXT(stored=True),
        file_album=whoosh.fields.TEXT(stored=True),
        file_artist=whoosh.fields.TEXT(stored=True),
        file_author=whoosh.fields.TEXT(stored=True),
        file_bitrate=whoosh.fields.TEXT(stored=True),
        file_channel=whoosh.fields.TEXT(stored=True),
        file_comment=whoosh.fields.TEXT(stored=True),
        file_compression_rate=whoosh.fields.TEXT(stored=True),
        file_compression=whoosh.fields.TEXT(stored=True),
        file_duration=whoosh.fields.TEXT(stored=True),
        file_endianness=whoosh.fields.TEXT(stored=True),
        file_height=whoosh.fields.TEXT(stored=True),
        file_producer=whoosh.fields.TEXT(stored=True),
        file_samplerate=whoosh.fields.TEXT(stored=True),
        file_title=whoosh.fields.TEXT(stored=True),
        file_width=whoosh.fields.TEXT(stored=True),
        subtitle_compression=whoosh.fields.TEXT(stored=True),
        subtitle_language=whoosh.fields.TEXT(stored=True),
        subtitle_title=whoosh.fields.TEXT(stored=True),
        video_compression=whoosh.fields.TEXT(stored=True),
        video_duration=whoosh.fields.TEXT(stored=True),
        video_framerate=whoosh.fields.TEXT(stored=True),
        video_height=whoosh.fields.TEXT(stored=True),
        video_language=whoosh.fields.TEXT(stored=True),
        video_title=whoosh.fields.TEXT(stored=True),
        video_width=whoosh.fields.TEXT(stored=True),
    )

    def __init__(self, logger, index_base='/fileindexer'):
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

    def query(self, query, page=1, pagelen=10):
        results = {
            'documents': [],
            'hits': 0
        }
        q = self.qparser.parse(query)
        with self.idx.searcher() as s:
            r = s.search_page(q, page, pagelen=pagelen)
            for (docid, raw_doc) in enumerate(r):
                rank = raw_doc.rank
                score = raw_doc.score
                raw_doc = dict(raw_doc)
                raw_doc['rank'] = rank
                raw_doc['score'] = score
                results['documents'].append(raw_doc)
                results['hits'] += 1
            results['pagenum'] = r.pagenum
            results['pagecount'] = r.pagecount
            results['result_start'] = r.offset + 1
            results['result_end'] = r.offset + r.pagelen + 1
            results['result_total'] = len(r)

        return results
