import hachoir_core.cmd_line
import hachoir_core.error
import hachoir_core.i18n
import hachoir_core.stream
import json
import os

import hachoir_core.config
hachoir_core.config.quiet = True

class IndexWriter:
    _00index_excluded = ['00INDEX']
    def __init__(self, logger):
        self.__l = logger

    def make_00INDEX(self, parent, files, directories):
        #self.__l.debug('Writing index for %s' % parent)
        idx = os.path.join(parent, '00INDEX')
        if os.path.exists(idx):
            os.unlink(idx)
        fd = open(idx, 'w')
        for directory in directories:
            meta = {}
            for k,v in directory.items():
                if not k in self._00index_excluded:
                    meta[k] = v
            line = '%s\t%s\n' % (directory['filename'], json.dumps(meta))
            line = unicode(line)
            try:
                fd.write(line)
            except UnicodeEncodeError, e:
                self.__l.warn('Failed to convert %s to unicode' % line)
                self.__l.warn(e)
        for file in files:
            meta = {}
            for k,v in file.items():
                if not k in self._00index_excluded:
                    meta[k] = v
            line = '%s\t%s\n' % (file['filename'], json.dumps(meta))
            try:
                fd.write(line)
            except UnicodeEncodeError, e:
                self.__l.warn('Failed to convert %s to unicode' % line)
                self.__l.warn(e)

        fd.close()

    def write_indexes(self, parent, metadata):
        files = []
        directories = []
        for item in metadata:
            if item['is_dir']:
                directories.append(item)
            else:
                files.append(item)
        directories.sort()
        files.sort()
        self.make_00INDEX(parent, files, directories)
