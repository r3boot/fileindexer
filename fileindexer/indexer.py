import datetime
import hachoir_core.cmd_line
import hachoir_core.error
import hachoir_core.i18n
import hachoir_core.stream
import hachoir_metadata
import hachoir_parser
import hashlib
import mimetypes
import os
import stat
import threading
import yaml

class HachoirMetadataParser:
    def __init__(self, logger):
        self.__l = logger
        self.charset = hachoir_core.i18n.getTerminalCharset()

    def extract(self, filename, quality):
        """this code comes from processFile in hachoir-metadata"""
        filename, real_filename = hachoir_core.cmd_line.unicodeFilename(filename, self.charset), filename

        # Create parser
        try:
            parser = hachoir_parser.createParser(filename, real_filename=real_filename)
        except hachoir_core.stream.InputStreamError, err:
            self.__l.error('Failed to create parser for %s' % filename)
            self.__l.error(err)
            return False
        if not parser:
            self.__l.error('No parser found for %s' % filename)
            return False

        # Extract metadata
        try:
            metadata = hachoir_metadata.extractMetadata(parser, quality)
        except hachoir_core.error.HachoirError, err:
            self.__l.error('Failed to extract metadata for %s' % filename)
            self.__l.error(err)
            return False
        if not metadata:
            self.__l.error('No metadata found for %s' % filename)
            return False

        # Convert metadata to dictionary
        meta = {}
        cur_k = None
        for line in str(metadata).split('\n'):
            line = unicode(line)
            if line.startswith('-'):
                # this is an attribute
                line = line.replace('- ', '')
                (k, v) = line.split(': ')[:2]
                ## TODO: ugly hack
                try:
                    meta[cur_k][k] = v
                except KeyError:
                    pass
            else:
                # this is a category
                cur_k = line.replace(':', '')
                if not cur_k.startswith('File "'):
                    meta[cur_k] = {}

        return meta

class Indexer(threading.Thread):
    def __init__(self, logger, api, idx, do_stat=True, do_hachoir=True, hachoir_quality=0.5, ignore_symlinks=True):
        threading.Thread.__init__(self)
        self.hmp = HachoirMetadataParser(logger)
        self.__l = logger
        self.api = api
        self.path = idx['path']
        self.do_stat = do_stat
        self.do_hachoir = do_hachoir
        self.ignore_symlinks = ignore_symlinks
        self.hachoir_quality = hachoir_quality
        self.setDaemon(True)
        self.__t_start = datetime.datetime.now()

    def run(self):
        num_files = self.index(self.path)
        t_end = datetime.datetime.now()
        t_total = t_end - self.__t_start
        self.__l.info('Finished indexing %s in %s (%s files)' % (self.path, t_total, num_files))

    def index(self, path):
        num_files = 0
        for (parent, dirs, files) in os.walk(path):
            for f in files:
                num_files += 1
                full_path = '%s/%s' % (parent, f)
                self.add(parent, full_path.encode('UTF-8'))
        return num_files

    def add(self, parent, path):
        meta = {}
        meta['path'] = path
        meta['_id'] = hashlib.sha1(path).hexdigest()
        meta['parent'] = parent

        try:
            st = os.stat(path)
        except OSError, e:
            self.__l.error('Failed to stat %s' % path)
            self.__l.error(e)
            return

        if self.ignore_symlinks and stat.S_ISLNK(st.st_mode):
            return

        if self.do_stat:
            meta['mode'] = st.st_mode
            meta['uid'] = st.st_uid
            meta['gid'] = st.st_gid
            meta['size'] = st.st_size
            meta['atime'] = st.st_atime
            meta['mtime'] = st.st_mtime
            meta['ctime'] = st.st_ctime

        if not stat.S_ISDIR(st.st_mode) and self.do_hachoir:
            #try:
            #    meta['mime'] = mimetypes.guess_type(path)[0]
            #    #if meta['mime'] == None:
            #    #    meta['mime'] = 'unknown'
            #except:
            #    meta['mime'] = 'unknown'
            hmp_meta = self.hmp.extract(path, self.hachoir_quality)
            if hmp_meta:
                for k,v in hmp_meta.items():
                    meta[k] = v
            else:
                mime = mimetypes.guess_type(path)[0]
                self.__l.error('No metadata found for %s (%s)' % (path, mime))

        self.api.add_file(meta)
