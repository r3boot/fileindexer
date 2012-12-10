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

class HachoirMetadataParser:
    #__unparseable = ['nfo', 'cue', 'diz', 'message', 'log', 'lsm', 'com', 'int', 'sub', 'mar', 'idx', 'bin', 'def', 'for', 'in', '1', 'l', 'str', 'nzb', 'obj', 'CUE']

    def __init__(self, logger):
        self.__l = logger
        self.charset = hachoir_core.i18n.getTerminalCharset()

    def extract(self, filename, quality, decoder):
        """this code comes from processFile in hachoir-metadata"""
        #fn, ext = os.path.splitext(filename)
        #if ext in self.__unparseable:
        #    return False

        filename, real_filename = hachoir_core.cmd_line.unicodeFilename(filename, self.charset), filename

        # Create parser
        try:
            if decoder:
                tags = [ ("id", decoder), None ]
            else:
                tags = None
            parser = hachoir_parser.createParser(filename, real_filename=real_filename, tags=tags)
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
    _hachoir_mapper = {
        'application/bzip2': 'bzip2',
        'vnd.ms-cab-compressed': 'cab',
        'application/gzip': 'gzip',
        'application/gzip-compressed': 'gzip',
        'application/gzipped': 'gzip',
        'application/x-gzip': 'gzip',
        'gzip/document': 'gzip',
        'application/x-gzip-compressed': 'gzip',
        'application/tar': 'tar',
        'application/x-gtar': 'tar',
        'application/x-gtar': 'tar',
        'applicaton/x-gtar': 'tar',
        'application/x-lzip': 'zip',
        'application/x-winzip': 'zip',
        'application/x-zip-compressed': 'zip',
        'application/zip': 'zip',
        'application/x-zip': 'zip',
        'application/x-zip-compressed': 'zip',
        'multipart/x-zip': 'zip',
        'audio/aiff': 'aiff',
        'audio/x-aiff': 'aiff',
        'audio/x-pn-aiff': 'aiff',
        'sound/aiff': 'aiff',
        'audio/flac': 'flac',
        'audio/x-mpegaudio': 'mpeg_audio',
        'audio/vnd.rn-realaudio': 'real_audio',
        'audio/vnd.rn-realaudio-secure': 'real_audio',
        'audio/x-pm-realaudio-plugin': 'real_audio',
        'audio/x-pn-realaudio': 'real_audio',
        'audio/x-pnrealaudio-plugin': 'real_audio',
        'audio/x-pn-realaudio-plugin': 'real_audio',
        'audio/x-realaudio': 'real_audio',
        'audio/x-realaudio-secure': 'real_audio',
        'audio/basic': 'sun_next_snd',
        'video/x-matroska': 'matroska',
        'application/ogg': 'ogg',
        'audio/ogg': 'ogg',
        'audio/x-ogg': 'ogg',
        'application/x-ogg': 'ogg',
        'application/vnd.rn-realmedia': 'real_media',
        'application/vnd.rn-realmedia-secure': 'real_media',
        'application/vnd.rn-realmedia-vbr': 'real_media',
        'application/x-pn-realmedia': 'real_media',
        'audio/vnd.rn-realvideo': 'real_media',
        'audio/vnd.rrn-realvideo': 'real_media',
        'audio/x-pn-realvideo': 'real_media',
        'video/vnd.rn-realvideo': 'real_media',
        'video/vnd.rn-realvideo-secure': 'real_media',
        'video/vnd-rn-realvideo': 'real_media',
        'video/x-pn-realvideo': 'real_media',
        'video/x-pn-realvideo-plugin': 'real_media',
        'audio/avi': 'riff',
        'image/avi': 'riff',
        'video/avi': 'riff',
        'video/msvideo': 'riff',
        'video/x-msvideo': 'riff',
        'application/futuresplash': 'swf',
        'application/x-shockwave-flash': 'swf',
        'application/x-shockwave-flash2-preview': 'swf',
        'video/vnd.sealed.swf': 'swf',
        'application/x-iso9660-image': 'iso9660',
        'application/bmp': 'bmp',
        'application/preview': 'bmp',
        'application/x-bmp': 'bmp',
        'application/x-win-bitmap': 'bmp',
        'image/bmp': 'bmp',
        'image/ms-bmp': 'bmp',
        'image/vnd.wap.wbmp': 'bmp',
        'image/x-bitmap': 'bmp',
        'image/x-bmp': 'bmp',
        'image/x-ms-bmp': 'bmp',
        'image/x-win-bitmap': 'bmp',
        'image/x-windows-bmp': 'bmp',
        'image/x-xbitmap': 'bmp',
        'image/gi_': 'gif',
        'image/gif': 'gif',
        'image/vnd.sealedmedia.softseal.gif ': 'gif',
        'application/ico': 'ico',
        'application/x-ico': 'ico',
        'application/x-iconware': 'ico',
        'image/ico': 'ico',
        'image/x-icon': 'ico',
        'image/jpe_': 'jpeg',
        'image/jpeg': 'jpeg',
        'image/jpeg2000': 'jpeg',
        'image/jpeg2000-image': 'jpeg',
        'image/jpg': 'jpeg',
        'image/pjpeg': 'jpeg',
        'image/vnd.sealedmedia.softseal.jpeg': 'jpeg',
        'image/vnd.swiftview-jpeg': 'jpeg',
        'image/x-jpeg2000-image': 'jpeg',
        'video/x-motion-jpeg': 'jpeg',
        'application/pcx': 'pcx',
        'application/x-pcx': 'pcx',
        'image/pcx': 'pcx',
        'image/vnd.swiftview-pcx': 'pcx',
        'image/x-pc-paintbrush': 'pcx',
        'image/x-pcx': 'pcx',
        'zz-application/zz-winassoc-pcx': 'pcx',
        'application/png': 'png',
        'application/x-png': 'png',
        'image/png': 'png',
        'image/vnd.sealed.png': 'png',
        'application/psd': 'psd',
        'image/photoshop': 'psd',
        'image/psd': 'psd',
        'image/x-photoshop': 'psd',
        'zz-application/zz-winassoc-psd': 'psd',
        'application/x-targa': 'targa',
        'image/targa': 'targa',
        'image/x-targa': 'targa',
        'application/tga': 'targa',
        'application/x-tga': 'targa',
        'image/tga': 'targa',
        'image/x-tga': 'targa',
        'application/tiff': 'tiff',
        'application/vnd.sealed.tiff': 'tiff',
        'application/x-tiff': 'tiff',
        'image/tiff': 'tiff',
        'image/x-tiff': 'tiff',
        'application/wmf': 'wmf',
        'application/x-msmetafile': 'wmf',
        'application/x-wmf': 'wmf',
        'image/wmf': 'wmf',
        'image/x-win-metafile': 'wmf',
        'image/x-wmf': 'wmf',
        'zz-application/zz-winassoc-wmf': 'wmf',
        'application/xcf': 'xcf',
        'application/x-xcf': 'xcf',
        'image/xcf': 'xcf',
        'image/x-xcf': 'xcf',
        'application/msword': 'ole2',
        'application/x-msword': 'ole2',
        'application/vnd.ms-word': 'ole2',
        'application/vnd.ms-word.document.macroEnabled.12': 'ole2',
        'application/vnd.ms-word.template.macroEnabled.12': 'ole2',
        'application/winword': 'ole2',
        'application/word': 'ole2',
        'application/x-dos_ms_word': 'ole2',
        'application/excel': 'ole2',
        'application/msexcel': 'ole2',
        'application/vnd.msexcel': 'ole2',
        'application/vnd.ms-excel': 'ole2',
        'application/vnd.ms-excel.addin.macroEnabled.12': 'ole2',
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12': 'ole2',
        'application/vnd.ms-excel.sheet.macroEnabled.12 ': 'ole2',
        'application/vnd.ms-excel.template.macroEnabled.12': 'ole2',
        'application/x-dos_ms_excel': 'ole2',
        'application/x-excel': 'ole2',
        'application/x-msexcel': 'ole2',
        'application/x-ms-excel': 'ole2',
        'application/mspowerpoint': 'ole2',
        'application/ms-powerpoint': 'ole2',
        'application/powerpoint': 'ole2',
        'application/vnd.ms-powerpoint': 'ole2',
        'application/vnd.ms-powerpoint': 'ole2',
        'application/vnd.ms-powerpoint.addin.macroEnabled.12': 'ole2',
        'application/vnd.ms-powerpoint.presentation.macroEnabled.12': 'ole2',
        'application/vnd.ms-powerpoint.slideshow.macroEnabled.12': 'ole2',
        'application/vnd-mspowerpoint': 'ole2',
        'application/x-mspowerpoint': 'ole2',
        'application/x-powerpoint': 'ole2',
        'application/x-font-pcf': 'pcf',
        'applications/x-bittorrent': 'torrent',
        'application/x-font-ttf': 'ttf',
        'application/dos-exe': 'exe',
        'application/exe': 'exe',
        'application/msdos-windows': 'exe',
        'application/x-exe': 'exe',
        'application/x-msdos-program': 'exe',
        'application/x-msdownload': 'exe',
        'application/x-winexe': 'exe',
        'application/vnd.ms-asf': 'asf',
        'application/x-mplayer2': 'asf',
        'audio/asf': 'asf',
        'video/x-ms-asf': 'asf',
        'video/x-la-asf': 'asf',
        'video/x-ms-asf': 'asf',
        'video/x-ms-asf-plugin': 'asf',
        'video/x-ms-wm': 'asf',
        'video/x-ms-wmx': 'asf',
        'video/x-flv': 'flv',
        'image/mov': 'mov',
        'video/quicktime': 'mov',
        'video/sgi-movie': 'mov',
        'video/vnd.sealedmedia.softseal.mov': 'mov',
        'video/x-quicktime': 'mov',
        'video/x-sgi-movie': 'mov',
        'application/octet-stream': None
    }

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
        (num_files, num_dirs) = self.index(self.path)
        t_end = datetime.datetime.now()
        t_total = t_end - self.__t_start
        self.__l.info('Finished indexing %s in %s (%s files, %s dirs)' % (self.path, t_total, num_files, num_dirs))

    def index(self, path):
        num_files = 0
        num_dirs = 0
        for (parent, dirs, files) in os.walk(path):
            for f in files:
                num_files += 1
                full_path = os.path.join(parent, f)
                self.add(parent, full_path.encode('UTF-8'))
            for d in dirs:
                num_dirs += 1
                full_path = os.path.join(parent, d)
                self.add(parent, full_path.encode('UTF-8'))
        return (num_files, num_dirs)

    def add(self, parent, path):
        meta = {}
        meta['index'] = self.path
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
            types = mimetypes.guess_type(path)
            if types[0] != None:
                meta['mime'] = types[0]
            if types and types[0] != None:
                t = None
                for mimetype in types:
                    if mimetype in self._hachoir_mapper:
                        t = mimetype
                        break
                if t:
                    hmp_meta = self.hmp.extract(path, self.hachoir_quality,  self._hachoir_mapper[t])
                    if hmp_meta:
                        for k,v in hmp_meta.items():
                            meta[k] = v

        self.api.add_file(meta)
