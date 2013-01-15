
import json
import os
import shutil
import time

class FilesystemQueue:
    def __init__(self, name, prefix_dir='/fileindexer/queues', preserve=True):
        self.__name = name
        self.__preserve = preserve

        self.__dir = os.path.join(prefix_dir, name)

        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)

        if not os.path.exists('%s/zzz' % self.__dir):
            os.mkdir('%s/zzz' % self.__dir)

        if not preserve:
            self.__cleanup_spool()

    def __destroy__(self):
        if not self.__preserve:
            self.__cleanup_spool()

    def __cleanup_spool(self):
        shutil.rmtree(self.__dir)
        os.mkdir(self.__dir)
        os.mkdir('%s/zzz' % self.__dir)

    def clear(self):
        self.__cleanup_spool()

    def get(self, timeout=0):
        while self.qsize() == 0:
            time.sleep(0.25)

        idx = os.listdir(self.__dir)
        idx.sort()
        queue_file = '%s/%s' % (self.__dir, idx[0])
        item = json.loads(open(queue_file, 'r').read())
        os.unlink(queue_file)
        return item

    def put(self, item, timeout=0):
        tmpfile = '%s/zzz/%.06f' % (self.__dir, time.time())
        queue_file = tmpfile.replace('/zzz', '')
        open(tmpfile, 'w').write(json.dumps(item))
        os.rename(tmpfile, queue_file)

    def qsize(self):
        qsize = len(os.listdir(self.__dir)) - 1
        return qsize

    def empty(self):
        qsize = self.qsize()
        return qsize == 0

if __name__ == '__main__':
    fsq = FilesystemQueue("testing")
    for i in xrange(10):
        fsq.put(i)

    while not fsq.empty():
        print(fsq.get())
