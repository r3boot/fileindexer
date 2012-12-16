import bottle
import gevent
import gevent.queue
import time

from fileindexer.api.backend import BackendAPI as API
from fileindexer.workers.writer import Writer

class QueueFiller(gevent.Greenlet):
    def __init__(self, logger, g_writeq_out, g_writeq_in):
        gevent.Greenlet.__init__(self)
        self.__l = logger
        self.__wqo = g_writeq_out
        self.__wqi = g_writeq_in
        self.stop = False
        self.start()

    def __destroy__(self):
        self.stop = True

    def _run(self):
        self.__l.debug('[backend_api greenlet] starting QueueFiller')
        while not self.stop:
            #self.__l.debug('[QueueFiller]: g_writeq size: %s' % self.__wqo.qsize())
            #self.__l.debug('[QueueFiller]: p_writeq size: %s' % self.__wqi.qsize())
            if self.__wqo.qsize() > 0:
                while not self.__wqo.empty():
                    meta = self.__wqo.get()
                    try:
                        self.__wqi.put(meta)
                    except gevent.queue.Full:
                        self.__l.error('[QueueFiller]: Queue is full')
            else:
                time.sleep(0.1)
        self.__l.debug('[backend_api greenlet] QueueFiller stopped')

def backend_api(logger, listen_ip, listen_port, p_writeq):
    logger.debug('[backend_api process]: Starting process')

    workers = []
    g_writeq_in = gevent.queue.Queue()
    g_writeq_out = gevent.queue.Queue()

    qf_worker = QueueFiller(logger, g_writeq_out, g_writeq_in)
    workers.append(qf_worker)

    writer_worker = Writer(logger, g_writeq_in)
    workers.append(writer_worker)

    api = API(logger, listen_ip, listen_port, g_writeq_out)

    ## API
    bottle.route('/ping',  method='GET')    (api.ping)
    bottle.route('/auth',  method='GET')    (api.test_authentication)
    bottle.route('/users', method='GET')    (api.get_users)
    bottle.route('/users', method='POST')   (api.add_user)
    bottle.route('/users', method='DELETE') (api.remove_user)
    bottle.route('/user',  method='GET')    (api.get_user)
    bottle.route('/user',  method='POST')   (api.update_user)
    bottle.route('/idx',   method='POST')   (api.add_document)
    bottle.route('/q',     method='POST')   (api.query)

    try:
        api.run()
    except KeyboardInterrupt, e:
        logger.warn(e)

    gevent.joinall(workers)
    logger.debug('[backend_api process]: Process stopping')
