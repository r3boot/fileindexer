#!/usr/bin/env python

import ast
import datetime
import os
import re
import sys
import time

import pprint

import mutagen
import mutagen.apev2
import mutagen.asf
import mutagen.flac
import mutagen.m4a
import mutagen.monkeysaudio
import mutagen.mp3
import mutagen.mp4
import mutagen.musepack
import mutagen.ogg
import mutagen.oggflac
import mutagen.oggspeex
import mutagen.oggtheora
import mutagen.oggvorbis
import mutagen.optimfrog
import mutagen.trueaudio
import mutagen.wavpack

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.indexer.safe_unicode import safe_unicode

mutagen_mimes = [
    'audio/asf',
    'audio/flac',
    'audio/x-mpegaudio',
    'audio/mpeg',
    'audio/ogg',
    'audio/x-ogg',
]

class AudioMetaParser:
    def __init__(self):
        pass

    def _get_meta(self, fname):
        meta = None
        ext = os.path.splitext(fname)[1][1:].lower()
        if ext in ['m3u', 'nfo', 'sfv', 'jpg', 'gz', 'JPG', 'html', 'cue', '']:
            return meta

        try:
            if ext in ['asf']:
                meta = mutagen.asf.ASF(fname)
            elif ext in ['flac']:
                meta = mutagen.flac.FLAC(fname)
            elif ext in ['m4a']:
                meta = mutagen.m4a.M4A(fname)
            elif ext in ['mp3']:
                meta = mutagen.mp3.MP3(fname)
            elif ext in ['ogg']:
                meta = mutagen.oggvorbis.OggVorbis(fname)
        except:
            pass

        return meta

    def extract(self, fname):
        meta = self._get_meta(fname)
        if meta:
            return meta

class MutagenMetadataParser:
    _ignored_keys = [
        'APIC',
        'USLT',
        'TXXX',
        'WXXX',
        'PRIV',
        'UFID',
        'MCDI',
        'GEOB',
        'PCNT',
        'POPM',
        'TFLT',
        'TIT3',
        'TPE2',
        'TKEY',
        'TOLY',
        'TOWN',
        'TOPE',
        'TRSN',
        'TSOA',
        'TSOT',
        'WCOM',
        'unknown0',
        'WOAF',
        'WOAR',
        'WOAS',
        'WPUB',
        'asin',
        'buycdurl',
        'cdtoc',
        'TDTG',
        'h2_',
        'musicbrainz_nonalbum',
        'performer',
        'related',
        'rip',
        'rip date',
        'retail date',
        'script',
        'setnumber',
        'settotal',
        'url',
        'venue',
        'www',
        'musicbrainz_',
        'accuraterip',
        'encodedby',
        'replaygain_',
        'related',
        'titlesort',
        'rip',
        'rip date',
        'discid',
        'musicip_',
        'codinghistory',
        'encoding',
        'transcoded',
        'TOFN',
        'orig_filename',
        'producer',
        'engineer',
        'remixed by',
        'track_modified_by',
        'remixer',
        'info',
        'version',
        'encodedon',
        'TDON',
        'releaser2',
        'logfile',
        'itunes_cddb_1',
        'dd mm yyyy',
        'pwn',
        'TCMP',
        'USLT',
        'TXXX:Album Artist',
        'TDRC',
        'recording_time',
        'albumartistsort',
        'artistsort',
        'rating',
        'limited edition',
        'albumsort',
        'origtime',
        'TPE4',
        'TDEN',
        'original logfile',
        'LINK',
        'mediafoundationversion',
        'wm/provider',
        'TSOA',
        'WORS',
        'tool version',
        'disc name',
        'tool name',
        'album artist',
        'albumartist',
        'band',
        'origartist',
        'originalartist',
        'taggedon',
        'totaldiscs',
        'track_band',
        'track_lead_performer',
        'track_performer',
        'discogs_release_id',
        'replaygain_track_peak',
        'discogs_release_id',
        'discogs_release_month',
        'replaygain_album_gain',
        'replaygain_track_gain',
        'gracenote',
        'barcode',
        'compilation',
    ]

    _key_remapper = {
        'catalog':                          'catalogno',
        'catalognr':                        'catalogno',
        'catalognumber':                    'catalogno',
        'cat#':                             'catalogno',
        'catalog#':                         'catalogno',
        'catalogue #':                      'catalogno',
        'discogs_catalog':                  'catalogno',
        'discogs_country':                  'country',
        'discogs_label':                    'label',
        'discnumber':                       'setno',
        'disctotal':                        'settot',
        'encoded-by':                       'encoder',
        'encoded by':                       'encoder',
        'encodedby':                        'encoder',
        'format':                           'medium',
        'isrc':                             'isrc',
        'label':                            'label',
        'style':                            'genre',
        'labelno':                          'catalogno',
        'media':                            'medium',
        'notes':                            'encoder',
        'organization':                     'label',
        'origdate':                         'date',
        'originator':                       'label',
        'origreference':                    'catalogno',
        'publisher':                        'label',
        'release type':                     'type',
        'releasecountry':                   'country',
        'releasedon':                       'date',
        'releasestatus':                    'status',
        'releasetype':                      'type',
        'releaseyear':                      'date',
        'source':                           'medium',
        'sourcemedia':                      'medium',
        'timereference':                    'duration',
        'totaldiscs':                       'settot',
        'totaltracks':                      'tracktot',
        'track':                            'trackno',
        'tracknumber':                      'trackno',
        'tracktotal':                       'tracktot',
        'upc':                              'catalogno',
        'discogs_artist_link':              'artist',
        'discogs_label_link':               'label',
        'discogs_released':                 'date',
        'discogs_original_track_number':    'trackno',
        'version':                          'release.version',
        'year':                             'date',
        'TPE1':                             'artist',
        'TPE3':                             'artist',
        'TIT2':                             'title',
        'TALB':                             'title',
        'TBPM':                             'bpm',
        'TCON':                             'genre',
        'TPUB':                             'label',
        'TRCK':                             'trackno',
        'TCOM':                             'composer',
        'COMM':                             'comment',
        'TENC':                             'encoder',
        'TLAN':                             'language',
        'TSSE':                             'encoder',
        'WCOP':                             'copyright',
        'TCOP':                             'copyright',
        'TSOP':                             'artist',
        'TDRL':                             'date',
        'TIT1':                             'genre',
        'TDOR':                             'date',
        'TOAL':                             'title',
        'TSRC':                             'isrc',
        'TEXT':                             'comment',
        'TPOS':                             'setno',
        'TMED':                             'medium',
        'TLEN':                             'duration',
    }

    _key_categories = {
        'catalogno':    'release',
        'country':      'release',
        'date':         'release',
        'label':        'release',
        'language':     'release',
        'encoder':      'release',
        'medium':       'release',
        'isrc':         'release',
        'type':         'release',
        'status':       'release',
        'copyright':    'release',
    }

    _mediums = {
      'DIG': 'Other digital media',
      'DIG/A': 'Analogue transfer from media',
      'ANA': 'Other analogue media',
      'ANA/WAC': 'Wax cylinder',
      'ANA/8CA': '8-track tape cassette',
      'CD': 'CD',
      'CD/A': 'CD Analogue transfer from media',
      'CD/DD': 'CD DDD',
      'CD/AD': 'CD ADD',
      'CD/AA': 'CD AAD',
      'LD': 'Laserdisc',
      'TT': 'Turntable records',
      'TT/33': 'Turntable records, 33.33 rpm',
      'TT/45': 'Turntable records, 45 rpm',
      'TT/71': 'Turntable records, 71.29 rpm',
      'TT/76': 'Turntable records, 76.59 rpm',
      'TT/78': 'Turntable records, 78.26 rpm',
      'TT/80': 'Turntable records, 80 rpm',
      'MD': 'MiniDisc',
      'MD/A': 'MiniDisc, Analogue transfer from media',
      'DAT': 'DAT',
      'DAT/A': 'DAT, Analogue transfer from media',
      'DAT/1': 'DAT, standard, 48 kHz/16 bits, linear',
      'DAT/2': 'DAT, mode 2, 32 kHz/16 bits, linear',
      'DAT/3': 'DAT, mode 3, 32 kHz/12 bits, non-linear, low speed',
      'DAT/4': 'DAT, mode 4, 32 kHz/12 bits, 4 channels',
      'DAT/5': 'DAT, mode 5, 44.1 kHz/16 bits, linear',
      'DAT/6': 'DAT, mode 6, 44.1 kHz/16 bits, wide track play',
      'DCC': 'DCC',
      'DCC/A': 'DCC, Analogue transfer from media',
      'DVD': 'DVD',
      'DVD/A': 'DVD, Analogue transfer from media',
      'TV': 'Television',
      'TV/PAL': 'Television, PAL',
      'TV/NTSC': 'Television, NTSC',
      'TV/SECAM': 'Television, SECAM',
      'VID': 'Video',
      'VID/PAL': 'Video, PAL',
      'VID/NTSC': 'Video, NTSC',
      'VID/SECAM': 'Video, SECAM',
      'VID/VHS': 'Video, VHS',
      'VID/SVHS': 'Video, S-VHS',
      'VID/BETA': 'Video, BETAMAX',
      'RAD': 'Radio',
      'RAD/FM': 'Radio, FM',
      'RAD/AM': 'Radio, AM',
      'RAD/LW': 'Radio, LW',
      'RAD/MW': 'Radio, MW',
      'TEL': 'Telephone',
      'TEL/I': 'Telephone, ISDN',
      'MC': 'MC (normal cassette)',
      'MC/4': 'MC, 4.75 cm/s (normal speed for a two sided cassette)',
      'MC/9': 'MC,  9.5 cm/s',
      'MC/I': 'MC, Type I cassette (ferric/normal)',
      'MC/II': 'MC, Type II cassette (chrome)',
      'MC/III': 'MC, Type III cassette (ferric chrome)',
      'MC/IV': 'MC, Type IV cassette (metal)',
      'REE': 'Reel',
      'REE/9': 'Reel, 9.5 cm/s',
      'REE/19': 'Reel, 19 cm/s',
      'REE/38': 'Reel, 38 cm/s',
      'REE/76': 'Reel, 76 cm/s',
      'REE/I': 'Reel, Type I cassette (ferric/normal)',
      'REE/II': 'Reel, Type II cassette (chrome)',
      'REE/III': 'Reel, Type III cassette (ferric chrome)',
      'REE/IV': 'Reel, Type IV cassette (metal)',
      'MIX': 'Mix Tape',
      'mixtape': 'Mix Tape',
      'unknown': 'Unknown'
    }

    _mediums_remapper = {
        'CD (CD)': 'CD',
        '(CD/DD)': 'CD/DD',
        'CDDA': 'CD',
        'CD, Maxi-Single': 'CD',
        'CD (Lossless)': 'CD',
        'Vinyl, 12"': 'TT',
        'Vinyl': 'TT',
        '12 Vinyl': 'TT',
        ' 24bits 96KHz by VINYL LAB': 'TT',
        'LIN': 'unknown',
        'MIX': 'mixtape',
    }

    _string_fields = [
        'album',
        'artist',
        'comment',
        'composer',
        'copyright',
        'description',
        'encoder',
        'ensemble',
        'genre',
        'language',
        'catalogno',
        'country',
        'isrc',
        'label',
        'status',
        'type',
        'style',
        'title'
        ]

    _int_fields = ['trackno', 'tracktot', 'setno', 'settot']

    _float_fields = ['bpm']

    _datetime_fields = ['date']

    _track_fields = ['trackno', 'setno']

    _medium_fields = ['medium']

    _duration_fields = ['duration']

    _re_encoded_field = re.compile('^[a-zA-Z]{4}(\(encoding=[01], .*\))$')

    _numbers = [str(i) for i in xrange(10)]

    _re_datetime_1 = re.compile('^([12][0-9]{3})-([0-9]{2})-([0-9]{2})$')
    _re_datetime_2 = re.compile('^([12][0-9]{3})$')
    _re_datetime_3 = re.compile('^([0-9]{2}) ([A-Za-z]{3}) ([12][0-9]{3})$')

    def __init__(self):
        self.amp = AudioMetaParser()

    def parse_encoded_field(self, value):
        value = str(value)
        if not 'encoding=' in value:
            return value

        for item in value[4:][1:][:-1].split(','):
            item = item.strip()
            if item.startswith('text='):
                return item[6:len(item)-1]
        return value

    def parse_track_field(self, v):
        v = self.parse_encoded_field(v)
        meta = {}
        if '/' in v:
            t = str(v).split('/')
            if not t[0].isdigit() or not t[1].isdigit():
                return v
            meta['trackno'] = self.parse_int_field(t[0])
            meta['tracktot'] = self.parse_int_field(t[1])
        else:
            meta['trackno'] = self.parse_int_field(v)
        return meta

    def parse_medium_field(self, v):
        v = str(v)
        if v in self._mediums_remapper:
            v = self._mediums_remapper[v]
        try:
            medium = safe_unicode(self._mediums[v])
            if medium:
                return medium
        except KeyError:
            print('Medium %s not found' % v)

    def parse_duration_field(self, v):
        try:
            v = float(v)
            return int(round(v / 1000))
        except ValueError:
            return None
        except TypeError:
            return None

    def parse_string_field(self, value):
        value = self.parse_encoded_field(value)
        value = value.strip()
        return safe_unicode(value)

    def parse_float_field(self, value):
        if not str(value).isdigit():
            tmp_value = ''
            for i in value:
                if i in self._numbers:
                    tmp_value += i
            if len(tmp_value) == 0 and len(value) == 1:
                tmp_value = ord(value.lower()) - 96
            if not tmp_value:
                return

            value = tmp_value

        try:
            return float(value)
        except:
            return float(str(value))

    def parse_int_field(self, value):
        result = self.parse_float_field(value)
        return int(round(result))

    def parse_datetime_field(self, value):
        if not isinstance(value, str):
            value = str(value)
        time_struct = None
        match = self._re_datetime_1.search(value)
        if match:
            time_struct = time.strptime(value, '%Y-%M-%d')

        match = self._re_datetime_2.search(value)
        if match:
            time_struct = time.strptime(value, '%Y')

        match = self._re_datetime_3.search(value)
        if match:
            time_struct = time.strptime(value, '%d %b %Y')

        if time_struct:
            return datetime.datetime.fromtimestamp(time.mktime(time_struct)).isoformat()
        else:
            return value

    def parse_value(self, key, value):
        for q in ['\'', '"']:
            if value.startswith(q):
                value = value[1:]
            elif value.endswith(q):
                value = value[:len(value)-1]

        for q in ['\x00']:
            if value.endswith(q):
                value = value.replace(q, '')

        if key in self._string_fields:
            value = self.parse_string_field(value)
            if not value:
                return

        elif key in self._int_fields:
            value = self.parse_int_field(value)

        elif key in self._float_fields:
            value = self.parse_float_field(value)

        elif key in self._datetime_fields:
            value = self.parse_datetime_field(value)

        elif key in self._track_fields:
            result = self.parse_track_field(value)
            if not isinstance(result, dict):
                print('WARNING: %s is not a dict' % value)
                return

            for k, v in result.items():
                if category == 'audio':
                    meta[category][0][k] = v
                else:
                    meta[category][k] = v
            return

        elif key in self._medium_fields:
            value = self.parse_medium_field(value)
            if not value:
                print('FAILED TO PARSE MEDIUM FIELD: %s' % value)
                return

        elif key in self._duration_fields:
            value = self.parse_duration_field(value)
            if not value:
                print('FAILED TO PARSE MEDIUM FIELD: %s' % value)
                return

        else:
            print('UNKNOWN FIELD: %s %s' % (key, value))
            return

        return value

    def extract(self, full_path):
        raw_meta = self.amp.extract(full_path)
        if not raw_meta:
            return {}

        print("==> %s" % full_path)
        meta = {
            'audio': [{}]
        }

        for key, value in raw_meta.items():
            #print('K: %s; V; %s' % (key, value))

            key = key.strip()

            if ':' in key:
                key = key.split(':')[0]

            if not isinstance(key, str):
                key = str(key)
            key = safe_unicode(key)

            if not isinstance(value, list):
                tmp = [value]
                value = tmp

            for q in ['\'', '"']:
                if key.startswith(q):
                    key = key[1:]
                elif key.endswith(q):
                    key = key[len(k)-1]

            ignore_key = False
            for t in self._ignored_keys:
                if key.startswith(t):
                    ignore_key = True
                    break
            if ignore_key:
                continue

            #print('K: %s; V; %s' % (key, value))
            if key in self._key_remapper.keys():
                key = self._key_remapper[key]

            if key in self._key_categories.keys():
                category = self._key_categories[key]
                if not self._key_categories[key] in meta.keys():
                    meta[self._key_categories[key]] = {}
            else:
                category = 'audio'

            for item in value:
                if not isinstance(item, str):
                    item = repr(item)
                result = self.parse_value(key, item)
                if not result:
                    continue

                if category == 'audio':
                    if key == 'genre':
                        if key not in meta[category][0].keys():
                            meta[category][0][key] = []
                        meta[category][0][key].append({"name": result})
                    else:
                        meta[category][0][key] = result
                else:
                    meta[category][key] = result

        if meta.has_key('release') and len(meta['release']) == 0:
            del(meta['release'])

        return meta

if __name__ == '__main__':
    dirs = ['/export/music/mp3/by-artist']

    mmp = MutagenMetadataParser()
    for d in dirs:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                r = mmp.extract('%s/%s' % (path, f))
                if r:
                    pprint.pprint(r)
