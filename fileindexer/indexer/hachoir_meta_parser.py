
import os
import time
import re
import string
import sys
import pprint

import hachoir_core.cmd_line
import hachoir_core.error
import hachoir_core.i18n
import hachoir_core.stream
import hachoir_metadata
import hachoir_parser

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.indexer.parser_utils import *

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
    _ignored_keys = [
        'MIME type',
        'Copyright',
        'Number of colors',
        'File type',
        'File size',
        'File name',
        'File attributes',
        'Nb page',
        'Camera focal',
        'Camera exposure',
        'Camera aperture',
        'Version',
    ]
    _key_remapper = {
        'Duration':             'duration',
        'Image width':          'width',
        'Image height':         'height',
        'Image DPI width':      'width.dpi',
        'Image DPI height':     'height.dpi',
        'Frame rate':           'framerate',
        'Bit rate':             'bitrate',
        'Bits/pixel':           'bits_per_pixel',
        'Bits/sample':          'bits_per_sample',
        'Sample rate':          'samplerate',
        'Comment':              'comment',
        'Endianness':           'endianness',
        'Camera model':         'hwmodel',
        'Camera manufacturer':  'hwvendor',
        'Compression rate':     'compression_rate',
        'Compression':          'compression',
        'Creation date':        'date',
        'Channel':              'channels',
        'Language':             'language',
        'Title':                'title',
        'Author':               'author',
        'Artist':               'artist',
        'Album':                'album',
        'Producer':             'software',
        'Pixel format':         'format',
        'Format version':       'format.version',
        'City':                 'city',
    }

    _key_categories = {
        'bitrate':      'release',
        'comment':      'release',
        'duration':     'release',
        'endianess':    'release',
        'framerate':    'release',
        'software':     'release',
        'width':        'release',
        'height':       'release',
    }

    _int_fields = [
        'height',
        'height.dpi',
        'framerate',
        'width',
        'width.dpi',
        'video.height',
        'video.width'
    ]

    _float_fields = [
        'compression.rate',
    ]

    _bitrate_fields = [
        'bitrate',
        'audio.bitrate',
        'video.bitrate',
    ]

    _duration_fields = [
        'duration',
    ]

    _samplerate_fields = [
        'samplerate',
    ]

    _endianness_fields = [
        'endianness',
    ]

    _channel_fields = [
        'channels'
    ]

    _datetimefields = [
        'date',
    ]

    def __init__(self):
        self.charset = hachoir_core.i18n.getTerminalCharset()
        self._re_categories = [
            [re.compile('^Audio stream:'),                 'audio'],
            [re.compile('^Audio stream #([0-9]{1,2}):$'),   'audio'],
            [re.compile('^Video stream:$'),                 'video'],
            [re.compile('^Video stream #([0-9]{1,2}):$'),   'video'],
        ]

    def _parse_number(self, v, type_of_nr='int'):
        result = 0
        if isinstance(v, int) and type_of_nr == 'float':
            return float(v)
        elif isinstance(v, float) and type_of_nr == 'int':
            return int(round(v))

        if ' ' in v:
            result = v.split(' ')[0]
        elif v.endswith('x'):
            result = v[:len(v)-1]

        if type_of_nr == 'int':
            return int(result.split('.')[0])
        elif type_of_nr == 'float':
            return float(result)

    def parse_float(self, v):
        return self._parse_number(v, 'float')

    def parse_int(self, v):
        return self._parse_number(v, 'int')

    def parse_bitrate(self, v):
        meta = {}

        if '(Variable bit rate)' in v:
            meta['vbr'] = True
        else:
            meta['vbr'] = False

        t = v.split()
        if t[1] == 'bit/s':
            meta['bitrate'] = float(t[0])
        elif t[1] == 'Kbit/sec':
            meta['bitrate'] = float(t[0])*1024
        elif t[1] == 'Mbit/sec':
            meta['bitrate'] = float(t[0])*1024*1024
        elif t[1] == 'Gbit/sec':
            meta['bitrate'] = float(t[0])*1024*1024*1024

        return meta

    def parse_samplerate(self, v):
        result = None
        t = v.split()
        value = t[0].split('.')[0]
        if t[1] == 'Hz':
            result = int(value)
        elif t[1] in ['kHz', 'KHz']:
            result = int(value) * 1000
        elif t[1] in ['mHz', 'MHz']:
            result = int(value) * 1000 * 1000
        elif t[1] in ['gHz', 'GHz']:
            result = int(value) * 1000 * 1000 * 1000

        return result

    def parse_duration(self, v):
        t = v.split()
        total = 0
        cur_val = 0
        for i in xrange(len(t)):
            try:
                cur_val = int(t[i])
            except:
                if t[i] == 'ms':
                    total += cur_val * 0.001
                elif t[i] == 'sec':
                    total += cur_val
                elif t[i] == 'min':
                    total += cur_val * 60
                elif t[i] == 'hour':
                    total += cur_val * 60 * 60
                cur_val = 0

        return total

    def parse_endianness(self, v):
        if v in ['Little endian']:
            return 'little'
        elif v in ['Big endian']:
            return 'big'

    def parse_channel(self, v):
        channels = 0
        if v in ['mono', 'Single channel']:
            channels = 1
        elif v in ['Stereo', 'Joint stereo', 'Dual channel', 'stereo']:
            channels = 2
        else:
            try:
                channels = int(v)
            except:
                pass

        return channels

    def parse_date(self, v):
        try:
            return time.mktime(time.strptime(v, '%Y-%m-%d %H:%M:%S'))
        except:
            return v

    def parse_category(self, line):
        has_match = False
        default_cat = None
        stream_id = None
        for item in self._re_categories:
            [regexp, category] = item
            match = regexp.search(line)
            if match:
                has_match = True
                if match.group(0).isdigit():
                    stream_id = int(match.group(0))
                else:
                    stream_id = 0
                default_cat = category
                break

        if not has_match:
            #print('UNKNOWN CATEGORY: %s' % line)
            default_cat = 'unknown'

        return (default_cat, stream_id)

    def extract(self, fname, quality=0.5, decoder=None):
        """this code comes from processFile in hachoir-metadata"""
        fname = safe_unicode(fname)
        if not fname:
            print('UNICODE FAILED: %s' % fname)
            return {}

        print('==> %s' % fname)
        filename, real_filename = fname, fname

        (f, ext) = os.path.splitext(fname)
        ext = ext.lower()[1:]

        # Create parser
        try:
            if decoder:
                tags = None
                tags = [ ("id", decoder), None ]
            else:
                tags = None
            parser = None
            parser = hachoir_parser.createParser(fname, real_filename=real_filename, tags=tags)
        except hachoir_core.stream.InputStreamError, err:
            print('Failed to create parser for %s' % fname)
            print(err)
            return False
        if not parser:
            print('No parser found for %s' % fname)
            return False

        # Extract metadata
        results = None
        try:
            results = hachoir_metadata.extractMetadata(parser, quality)
        except hachoir_core.error.HachoirError, err:
            print('Failed to extract metadata for %s' % fname)
            print(err)
            return False
        if not results:
            return False

        # Convert metadata to dictionary
        meta = None
        meta = {
            'unknown': {}
        }

        prefix = ''

        default_cat = None
        stream_id = None

        for line in str(results).split('\n'):
            line = line.strip()
            #print('LINE: \'%s\'' % line)

            if line[0] in string.ascii_letters:
                (default_cat, stream_id) = self.parse_category(line)

                if default_cat not in meta.keys():
                    if default_cat in ['audio', 'video']:
                        meta[default_cat] = [{'stream_id': stream_id}]
                    else:
                        meta[default_cat] = {}
                else:
                    if default_cat in ['audio', 'video']:
                        meta[default_cat][stream_id] = {'stream_id': stream_id}

                continue

            line = safe_unicode(line)[2:]
            if not ': ' in line:
                continue

            tokens = line.split(': ')
            key = tokens[0]
            value = ': '.join(tokens[1:])

            #print("K: %s; V: %s; DC: %s; ID: %s" % (key, value, default_cat, stream_id))


            if key in self._ignored_keys:
                continue

            if key in self._key_remapper.keys():
                key = self._key_remapper[key]

            if default_cat is 'unknown' and key in self._key_categories.keys():
                if not self._key_categories[key] in meta.keys():
                    meta[self._key_categories[key]] = {}
                default_cat = self._key_categories[key]

            if key in self._int_fields:
                value = self.parse_int(value)

            elif key in self._float_fields:
                value = self.parse_float(value)

            elif key in self._bitrate_fields:
                bitrate_meta = self.parse_bitrate(value)
                if not bitrate_meta:
                    continue
                if 'vbr' in bitrate_meta.keys() and default_cat in ['audio', 'video']:
                    meta[default_cat][stream_id]['vbr'] = True
                value = bitrate_meta['bitrate']

            elif key in self._duration_fields:
                value = self.parse_duration(value)

            elif key in self._endianness_fields:
                value = self.parse_endianness(value)

            elif key in self._samplerate_fields:
                value = self.parse_samplerate(value)

            elif key in self._channel_fields:
                value = self.parse_channel(value)

            if default_cat in ['audio', 'video']:
                meta[default_cat][stream_id][key] = value
            else:
                meta[default_cat][key] = value

        for category in ['unknown']:
            if len(meta[category]) == 0:
                del(meta[category])

        return meta

if __name__ == '__main__':
    DIRS = ['/export/series']

    HMP = HachoirMetadataParser()
    for d in DIRS:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                r = HMP.extract('%s/%s' % (path, f))
                if r:
                    pprint.pprint(r)
