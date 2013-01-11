
import json
import os
import time

class FilesystemQueue:
    def __init__(self, name, prefix_dir='/fileindexer/queues', preserve=True):
        self.__preserve = preserve

        self.__dir = os.path.join(prefix_dir, name)

        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)

        if not preserve:
            self.__cleanup_spool()

    def __destroy__(self):
        if not self.__preserve:
            self.__cleanup_spool()
            os.rmdir(self.__dir)

    def __cleanup_spool(self):
        oldcwd = os.getcwd()
        os.chdir(self.__dir)
        map(os.unlink, os.listdir(self.__dir))
        os.chdir(oldcwd)

    def clear(self):
        self.__cleanup_spool()

    def get(self, timeout=0):
        idx = os.listdir(self.__dir)
        idx.sort()
        queue_file = '%s/%s' % (self.__dir, idx[0])
        if len(idx) > 0:
            item = json.loads(open(queue_file, 'r').read())
            os.unlink(queue_file)
            return item

    def put(self, item, timeout=0):
        open('%s/%.06f' % (self.__dir, time.time()), 'w').write(json.dumps(item))

    def qsize(self):
        return len(os.listdir(self.__dir))

    def empty(self):
        return self.qsize() == 0

if __name__ == '__main__':
    fsq = FilesystemQueue("testing")
    for i in xrange(10):
        fsq.put(i)

    while not fsq.empty():
        print(fsq.get())
