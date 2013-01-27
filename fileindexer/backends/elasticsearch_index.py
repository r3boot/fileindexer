
import pyes

class ElasticSearchIndex:
    def __init__(self, host='127.0.0.1', port=9200, index_name='fileindexer'):
        self.__ES_instance = '%s:%s' % (host, port)
        self.__ES_index_name = index_name
        self.__conn = None

    def connect(self):
        self.__conn = pyes.ES(self.__ES_instance)

    def create_index(self):
        try:
            self.__conn.indices.create_index(self.__ES_index_name)
        except pyes.exceptions.IndexAlreadyExistsException:
            pass

    def index(self, meta):
        self.__conn.index(meta, self.__ES_index_name, 'none')

    def query(self, query):
        pass
