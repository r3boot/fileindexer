
import pyes

from fileindexer.constants import category_types

class ElasticSearchIndex:
    def __init__(self, host='127.0.0.1', port=9200, index_name='fileindexer'):
        self.__ES_instance = '%s:%s' % (host, port)
        self.__ES_index_name = index_name
        self.__conn = None
        self.connect()
        self.create_index()

    def connect(self):
        print('Connecting to ES at %s' % self.__ES_instance)
        self.__conn = pyes.ES(self.__ES_instance)

    def create_index(self):
        try:
            self.__conn.indices.create_index(self.__ES_index_name)
        except pyes.exceptions.IndexAlreadyExistsException:
            pass

    def index(self, meta):
        try:
            self.__conn.index(meta, self.__ES_index_name, 'none')
        except pyes.exceptions.ElasticSearchException, e:
            print(meta)
            print(e)

    def query(self, query, page=0, pagelen=10):
        results = {
            'documents': [],
            'hits': 0
        }
        q = pyes.StringQuery(query)
        r = self.__conn.search(query=q, indices=self.__ES_index_name, start=page, size=pagelen)
        for raw_doc in r:
            doc = dict(raw_doc)
            doc['score'] = 0                ## TODO
            doc['rank'] = raw_doc.position
            results['documents'].append(doc)
            results['hits'] += 1

        results['pagenum'] = page
        results['pagecount'] = r.total / pagelen
        if page == 0:
            results['result_start'] = page
        elif page == 1:
            results['result_start'] = pagelen
        else:
            results['result_start'] = pagelen * ( page - 1 )
        results['result_end'] = results['result_start'] + pagelen
        results['result_total'] = r.total

        return results
