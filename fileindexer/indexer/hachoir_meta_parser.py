import hachoir_core.cmd_line
import hachoir_core.error
import hachoir_core.i18n
import hachoir_core.stream
import hachoir_metadata
import hachoir_parser

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
    'video/x-ms-asf': 'asf',
    'video/x-la-asf': 'asf',
    'video/x-ms-asf': 'asf',
    'video/x-ms-asf-plugin': 'asf',
    'video/x-ms-wm': 'asf',
    'video/x-ms-wmx': 'asf',
    #'video/x-flv': 'flv',
    'image/mov': 'mov',
    'video/quicktime': 'mov',
    'video/sgi-movie': 'mov',
    'video/vnd.sealedmedia.softseal.mov': 'mov',
    'video/x-quicktime': 'mov',
    'video/x-sgi-movie': 'mov',
    'video/mp4': 'mpeg_video',
    'application/octet-stream': None,
}

class HachoirMetadataParser:
    _remapper = {
        'Duration': 'duration',
        'Image width': 'width',
        'Image height': 'height',
        'Frame rate': 'framerate',
        'Bit rate': 'bitrate',
        'Sample rate': 'samplerate',
        'Comment': 'comment',
        'Endianness': 'endianness',
        'Compression rate': 'compression_rate',
        'Compression': 'compression',
        'Channel': 'channel',
        'Language': 'language',
        'Title': 'title',
        'Author': 'author',
        'Artist': 'artist',
        'Album': 'album',
        'Producer': 'producer',
        'Common': '',
        'Video': 'video',
        'Video stream': 'video',
        'Video stream #1': 'video',
        'Video stream #2': 'video',
        'Video stream #3': 'video',
        'Audio': 'audio',
        'Audio stream': 'audio',
        'Audio stream #1': 'audio',
        'Audio stream #2': 'audio',
        'Audio stream #3': 'audio',
        'Subtitle': 'subtitle',
        'File': 'file',
        'Metadata': 'file',
    }

    def __init__(self, logger):
        self.charset = hachoir_core.i18n.getTerminalCharset()

    def extract(self, sparse_meta, quality, decoder):
        """this code comes from processFile in hachoir-metadata"""
        #fn, ext = os.path.splitext(filename)
        #if ext in self.__unparseable:
        #    return False

        real_filename = None
        try:
            filename, real_filename = hachoir_core.cmd_line.unicodeFilename(sparse_meta['full_path'], self.charset), sparse_meta['full_path']
        except TypeError:
            real_filename = sparse_meta['full_path']

        # Create parser
        try:
            if decoder:
                tags = None
                tags = [ ("id", decoder), None ]
            else:
                tags = None
            parser = None
            parser = hachoir_parser.createParser(sparse_meta['full_path'], real_filename=real_filename, tags=tags)
        except hachoir_core.stream.InputStreamError, err:
            print('Failed to create parser for %s' % sparse_meta['full_path'])
            print(err)
            return False
        if not parser:
            print('No parser found for %s' % sparse_meta['full_path'])
            return False

        # Extract metadata
        results = None
        try:
            results = hachoir_metadata.extractMetadata(parser, quality)
        except hachoir_core.error.HachoirError, err:
            print('Failed to extract metadata for %s' % sparse_meta['full_path'])
            print(err)
            return False
        if not results:
            print('No metadata found for %s' % sparse_meta['full_path'])
            return False

        # Convert metadata to dictionary
        meta = None
        meta = {}
        meta.update(sparse_meta)
   
        cur_k = None
        for line in str(results).split('\n'):
            if line.startswith('File \"'):
                continue

            line = unicode(line)
            if line.startswith('-'):
                # this is an attribute
                line = line.replace('- ', '')
                k = None
                v = None
                (k, v) = line.split(': ')[:2]
                ## TODO: ugly hack
                key = None
                try:
                    if cur_k == '':
                        key = self._remapper[k]
                    else:
                        key = '%s_%s' % (cur_k, self._remapper[k])
                    meta[key] = v
                except KeyError:
                    pass
            else:
                # this is a category
                cur_k = self._remapper[line.replace(':', '')]
        line = None
        return meta
