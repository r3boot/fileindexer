#!/usr/bin/env python

import datetime
import os
import re
import sys
import time

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
    _valid_tags = [
        'accuraterip.crc',
        'accuraterip.id',
        'album',
        'artist',
        'artist.band',
        'artist.orig',
        'artists',
        'barcode',
        'comment',
        'compilation',
        'composer',
        'copyright',
        'description',
        'disc',
        'disc.total',
        'duration',
        'encoder',
        'ensemble',
        'genre',
        'gracenote.extdata',
        'gracenote.fileid',
        'language',
        'medium',
        'musicbrainz.album.id',
        'musicbrainz.artist.id',
        'musicbrainz.track.id',
        'release.catalognr',
        'release.country',
        'release.date',
        'release.isrc',
        'release.label',
        'release.medium',
        'release.status',
        'release.type',
        'releaser',
        'set.nr',
        'set.total',
        'style',
        'title',
        'track.bpm',
        'track.nr',
        'track.total'
    ]

    _ignored_tags_start = ['APIC', 'USLT', 'TXXX', 'WXXX', 'PRIV', 'UFID', 'MCDI', 'GEOB', 'PCNT', 'POPM', 'TFLT', 'TIT3', 'TKEY', 'TOLY', 'TOWN', 'TRSN',' TSOA', 'TSOT', 'WCOM', 'unknown0', 'WOAF', 'WOAR', 'WOAS', 'WPUB', 'asin', 'buycdurl', 'cdtoc', 'TDTG', 'h2_', 'musicbrainz_nonalbum', 'performer', 'related', 'rip', 'rip date', 'retail date', 'script', 'setnumber', 'settotal', 'url', 'venue', 'www', 'musicbrainz_albumartist', 'musicbrainz_albumartistsortname', 'musicbrainz_albumstatus', 'musicbrainz_albumtype', 'musicbrainz_nonalbum', 'musicbrainz_sortname', 'musicbrainz_variousartists', 'musicbrainz_discid', 'accurateriptotal', 'accurateripresult', 'accurateripoffset', 'accurateripdiscid', 'accurateripcountwithoffset', 'accurateripcountalloffsets', 'accurateripcount', 'encodedby', 'replaygain_album_gain', 'replaygain_album_peak', 'replaygain_reference_loudness', 'replaygain_track_gain', 'replaygain_track_peak', 'discogs_artist_id', 'discogs_artist_link', 'discogs_label_link', 'discogs_original_track_number', 'discogs_release_month', 'discogs_released', 'related', 'titlesort', 'rip', 'rip date', 'discid', 'musicip_puid', 'discogs_release_id', 'codinghistory', 'encoding', 'transcoded', 'TOFN', 'orig_filename', 'producer', 'engineer', 'remixed by', 'track_modified_by', 'remixer', 'info', 'version', 'encodedon', 'TDON', 'releaser2', 'logfile', 'itunes_cddb_1', 'dd mm yyyy', 'pwn', 'TCMP', 'USLT', 'TXXX:Album Artist', 'TDRC', 'recording_time', 'albumartistsort', 'artistsort', 'rating', 'limited edition', 'albumsort', 'origtime', 'TPE4', 'TDEN', 'original logfile', 'LINK', 'mediafoundationversion', 'wm/provider', 'TSOA', 'WORS']

    _remapped_tags = {
        'accurateripcrc':                   'accuraterip.crc',
        'accurateripid':                    'accuraterip.id',
        'album artist':                     'artists',
        'albumartist':                      'artists',
        'band':                             'artist.band',
        'bpm':                              'track.bpm',
        'catalog':                          'release.catalognr',
        'catalognr':                        'release.catalognr',
        'catalognumber':                    'release.catalognr',
        'cat#':                             'release.catalognr',
        'catalog#':                         'release.catalognr',
        'catalogue #':                      'release.catalognr',
        'country':                          'release.country',
        'date':                             'release.date',
        'discnumber':                       'disc',
        'discogs_catalog':                  'release.catalognr',
        'discogs_country':                  'release.country',
        'discogs_label':                    'release.label',
        'disctotal':                        'disc.total',
        'encoded-by':                       'encoder',
        'encoded by':                       'encoder',
        'encodedby':                        'encoder',
        'format':                           'release.medium',
        'gracenoteextdata':                 'gracenote.extdata',
        'gracenotefileid':                  'gracenote.fileid',
        'isrc':                             'release.isrc',
        'label':                            'release.label',
        'labelno':                          'release.catalognr',
        'media':                            'release.medium',
        'musicbrainz_albumartistid':        'musicbrainz.artist.id',
        'musicbrainz_albumid':              'musicbrainz.album.id',
        'musicbrainz_artistid':             'musicbrainz.artist.id',
        'musicbrainz_trackid':              'musicbrainz.track.id',
        'notes':                            'encoder',
        'organization':                     'release.label',
        'origartist':                       'artist.orig',
        'origdate':                         'release.date',
        'originalartist':                   'artist.orig',
        'originator':                       'release.label',
        'origreference':                    'release.catalognr',
        'publisher':                        'release.label',
        'release type':                     'release.type',
        'releasecountry':                   'release.country',
        'releasedon':                       'release.date',
        'releasestatus':                    'release.status',
        'releasetype':                      'release.type',
        'releaseyear':                      'release.date',
        'source':                           'release.medium',
        'sourcemedia':                      'release.medium',
        'taggedon':                         'tagged.date',
        'timereference':                    'duration',
        'totaldiscs':                       'disc.total',
        'totaltracks':                      'track.total',
        'track':                            'track.nr',
        'track_band':                       'artist.band',
        'track_lead_performer':             'artist',
        'track_performer':                  'artist',
        'tracknumber':                      'track.nr',
        'tracktotal':                       'track.total',
        'type':                             'release.type',
        'upc':                              'release.catalognr',
        'version':                          'release.version',
        'year':                             'release.date',
        'TPE1':                             'artist',
        'TPE2':                             'artist.band',
        'TPE3':                             'artist',
        'TIT2':                             'title',
        'TALB':                             'title',
        'TBPM':                             'track.bpm',
        'TCON':                             'genre',
        'TPUB':                             'release.label',
        'TRCK':                             'track.nr',
        'TCOM':                             'composer',
        'COMM':                             'comment',
        'TENC':                             'encoder',
        'TLAN':                             'language',
        'TSSE':                             'encoder',
        'WCOP':                             'copyright',
        'TCOP':                             'copyright',
        'TSOP':                             'artist',
        'TDRL':                             'release.date',
        'TOPE':                             'artist.orig',
        'TIT1':                             'genre',
        'TDOR':                             'release.date',
        'TOAL':                             'title',
        'TSRC':                             'release.isrc',
        'TEXT':                             'comment',
        'TPOS':                             'set.nr',
        'TMED':                             'release.medium',
        'TLEN':                             'duration',
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

    _string_fields = ['accuraterip.crc', 'accuraterip.id', 'album', 'artist', 'artist.band', 'artist.orig', 'artists', 'barcode', 'comment', 'composer', 'copyright', 'description', 'encoder', 'ensemble', 'genre', 'gracenote.extdata', 'gracenote.fileid', 'language', 'musicbrainz.album.id', 'musicbrainz.artist.id', 'musicbrainz.track.id', 'release.catalognr', 'release.country', 'release.isrc', 'release.label', 'releaser', 'release.status', 'release.type', 'style', 'title']

    _float_fields = ['compilation', 'disc', 'disc.total', 'track.bpm', 'track.total']

    _datetime_fields = ['release.date']

    _track_fields = ['track.nr', 'set.nr']

    _medium_fields = ['release.medium']

    _duration_fields = ['duration']

    _re_encoded_field = re.compile('^[a-zA-Z]{4}(\(encoding=[01], .*\))$')

    _numbers = [str(i) for i in xrange(10)]

    _re_datetime_1 = re.compile('^([12][0-9]{3})-([0-9]{2})-([0-9]{2})$')
    _re_datetime_2 = re.compile('^([12][0-9]{3})$')

    unknown_tags = []

    def __init__(self):
        self.amp = AudioMetaParser()

    def parse_encoded_field(self, value):
        value = str(value)
        if not 'encoding=' in value:
            return value

        for item in value[4:][1:][:-1].split(','):
            item = item.strip()
            (t, v) = item.split('=')
            if t == 'text':
                return ast.literal_eval(v)[0]

        return value

    def parse_track_field(self, v):
        v = self.parse_encoded_field(v)
        meta = {}
        if '/' in v:
            t = str(v).split('/')
            if not t[0].isdigit() or not t[1].isdigit():
                return v
            meta['nr'] = self.parse_float_field(t[0])
            meta['total'] = self.parse_float_field(t[1])
        else:
            meta['nr'] = self.parse_float_field(v)
        return meta

    def parse_medium_field(self, v):
        v = str(v)
        if v in self._mediums_remapper:
            v = self._mediums_remapper[v]
        try:
            return {'release.medium': self._mediums[v]}
        except KeyError:
            print('Medium %s not found' % v)
            return {}

    def parse_duration_field(self, v):
        try:
            v = float(v)
            return {'duration': int(round(v / 1000))}
        except ValueError:
            return {}
        except TypeError:
            return {}

    def valid_tag(self, tag):
        valid_tag = False
        for k in self._valid_tags:
            if k == tag:
                return True

    def parse_string_field(self, value):
        try:
            return value.encode('UTF-8')
        except UnicodeError:
            return str(value)
        except AttributeError:
            return str(value)

    def parse_float_field(self, value):
        if not str(value).isdigit():
            tmp_value = ''
            for i in value:
                if i in self._numbers:
                    tmp_value += i
            if len(tmp_value) == 0:
                return None
            value = tmp_value

        try:
            return float(value)
        except:
            return float(str(value))

    def parse_datetime_field(self, value):
        if not isinstance(value, str):
            value = str(value)
        match = self._re_datetime_1.search(value)
        if match:
            return time.strptime(value, '%Y-%M-%d')
        match = self._re_datetime_2.search(value)
        if match:
            return time.strptime(value, '%Y')

    def extract(self, meta):
        raw_meta = self.amp.extract(meta['full_path'])
        if not raw_meta:
            return {}

        meta = {}
        self.unknown_tags = []
        for k,v in raw_meta.items():
            k = k.strip()
            if ':' in k:
                k = k.split(':')[0]

            for q in ['\'', '"']:
                if k.startswith(q):
                    k = k[1:]
                elif k.endswith(q):
                    k = k[len(k)-1]

            if isinstance(v, list):
                v = v[0]

            ignore_tag = False
            for t in self._ignored_tags_start:
                if k.startswith(t):
                    ignore_tag = True
                    break
            if ignore_tag:
                continue

            tag = None
            value = None
            if k in self._remapped_tags.keys():
                tag = self._remapped_tags[k]
                value = v
            else:
                tag = k
                value = v

            if not self.valid_tag(tag):
                print('UNKNOWN TAG: %s' % k)
                sys.exit(1)

            if tag in self._string_fields:
                meta[tag] = self.parse_string_field(value)

            elif tag in self._float_fields:
                meta[tag] = self.parse_float_field(value)

            elif tag in self._datetime_fields:
                meta[tag] = self.parse_datetime_field(value)

            elif tag in self._track_fields:
                result = self.parse_track_field(value)
                if not isinstance(result, dict):
                    return 0
                base = tag.split('.')[0]
                for k,v in result.items():
                    meta['%s.%s' % (base, k)] = v

            elif tag in self._medium_fields:
                meta[tag] = self.parse_medium_field(value)

            elif tag in self._duration_fields:
                meta[tag] = self.parse_duration_field(value)

            else:
                print('UNKNOWN FIELD: %s %s' % (tag, value))
                sys.exit(1)

        return meta
