import datetime
import hachoir_core.cmd_line
import hachoir_core.error
import hachoir_core.i18n
import hachoir_core.stream
import hashlib
import mimetypes
import os
import stat
import time

import hachoir_core.config
hachoir_core.config.quiet = True

from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser
from fileindexer.indexer.index_writer import IndexWriter
from fileindexer.logging import get_logger

hachoir_mapper = {
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
    'application/x-zip': 'zip',
    'application/x-zip-compressed': 'zip',
    'multipart/x-zip': 'zip',
    'audio/aiff': 'aiff',
    'audio/x-aiff': 'aiff',
    'audio/x-pn-aiff': 'aiff',
    'sound/aiff': 'aiff',
    'audio/flac': 'flac',
    'audio/x-mpegaudio': 'mpeg_audio',
    'audio/mpeg': 'mpeg_audio',
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

excluded = ['00INDEX', '00SUMS', '00METADATA']

def indexer(args):
    log_level = args[0]
    paths = args[1]
    out_q = args[2]
    do_stat = True
    do_hachoir = True
    hachoir_quality=0.5
    ignore_symlinks=True

    print('here')

    def __to_unicode(s):
        try:
            return unicode(s)
        except UnicodeDecodeError, e:
            logger.warn('Failed to translate %s to unicode' % s)
            logger.warn(e)

    logger = get_logger(log_level)
    hmp = HachoirMetadataParser(logger)
    idxwriter = IndexWriter(logger)

    for path in paths:
        print('path: %s' % path)

        results = {}
        scan_next = []
        results['path'] = path
        results['metadata'] = []
        if not os.access(path, os.R_OK | os.X_OK):
            logger.warn('Failed to access %s' % path)
            return

        for found in os.listdir(path):
            if found in excluded:
                continue
            found = __to_unicode(found)
            if not found:
                continue

            meta = {}
            meta['filename'] = found
            meta['parent'] = path

            full_path = os.path.join(path, found)

            try:
                st = os.stat(full_path)
            except OSError, e:
                logger.error('Failed to stat %s' % path)
                logger.error(e)
                return

            meta['is_dir'] = stat.S_ISDIR(st.st_mode)
            if meta['is_dir']:
                scan_next.append('%s/%s' % (path, found))

            # Naive, but sufficient & fast enough for now
            try:
                meta['checksum'] = hashlib.md5('%s %s' % (found, st.st_size)).hexdigest()
            except UnicodeEncodeError, e:
                logger.warn('Failed to generate checksum')
                logger.warn(e)

            if ignore_symlinks and stat.S_ISLNK(st.st_mode):
                logger.warn('Skipping symlink %s' % path)
                return

            if do_stat:
                meta['mode'] = st.st_mode
                meta['uid'] = st.st_uid
                meta['gid'] = st.st_gid
                meta['size'] = st.st_size
                meta['atime'] = st.st_atime
                meta['mtime'] = st.st_mtime
                meta['ctime'] = st.st_ctime

            if not meta['is_dir'] and do_hachoir:
                types = mimetypes.guess_type(full_path)
                if types[0] != None:
                    meta['mime'] = types[0]
                if types and types[0] != None:
                    t = None
                    for mimetype in types:
                        if mimetype in hachoir_mapper:
                            t = mimetype
                            break
                    if t:
                        hmp_meta = hmp.extract(full_path, hachoir_quality,  hachoir_mapper[t])
                        if hmp_meta:
                            for k,v in hmp_meta.items():
                                meta[k] = v
            results['metadata'].append(meta)

            idxwriter.write_indexes(path, results['metadata'])
        else:
            time.sleep(0.1)

    out_q.put(results)
