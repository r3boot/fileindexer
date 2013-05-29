import datetime
import os
import re
import sys

import pprint

import guessit

sys.path.append('/people/r3boot/fileindexer')

from fileindexer.indexer.parser_utils import *
from fileindexer.indexer.enzyme_meta_parser import enzyme_mimes
from fileindexer.indexer.mutagen_meta_parser import mutagen_mimes
from fileindexer.indexer.exif_meta_parser import exif_mimes

class FileMetadataParser:
    _re_release_dir = re.compile('.*[-.][a-zA-Z0-9]*\-([a-zA-Z0-9]*)$')

    _ignored_tags = [
        'extension',
        'other',
        'type',
        'website',
    ]

    _tag_remapper = {
        'audioChannels':    'channels',
        'audioCodec':       'codec',
        'cdNumber':         'discno',
        'episodeNumber':    'number',
        'mimetype':         'mime',
        'releaseGroup':     'group',
        'screenSize':       'screensize',
        'videoCodec':       'codec',
    }

    _guess_categories = [
        'channels',
        'codec',
        'container',
        'title',
    ]

    _tag_categories = {
        'country':      'release',
        'date':         'release',
        'discno':       'release',
        'edition':      'release',
        'episode':      'episode',
        'format':       'release',
        'group':        'release',
        'mime':         'file',
        'number':       'episode',
        'screensize':   'release',
        'season':       'episode',
        'series':       'episode',
        'year':         'release',
    }

    def parse_screensize_to_hd(self, value):
        if value in ['720p', '1080p']:
            return True
        else:
            return False

    def parse_language(self, value):
        return str(value[0])

    def parse_year(self, value):
        return datetime.datetime(int(value), 1, 1, 0, 0, 0).isoformat()

    def extract(self, full_path):
        meta = {
            'audio':   {},
            'episode': {},
            'file':    {},
            'release': {},
            'video':   {},
        }
        full_path = safe_unicode(full_path)
        meta['file']['name'] = os.path.basename(full_path)
        release_dir = os.path.basename(os.path.dirname(full_path))
        match = self._re_release_dir.search(release_dir)
        if match:
            meta['release']['name'] = release_dir
            meta['release']['group'] = match.group(1)

        raw_meta = None
        try:
            raw_meta = guessit.guess_file_info(full_path, 'autodetect')
        except UnicodeDecodeError:
            pass
        except KeyError:
            pass

        if not raw_meta:
            try:
                raw_meta = guessit.guess_file_info(release_dir, 'autodetect')
            except UnicodeDecodeError:
                pass
            except KeyError:
                pass
        if not raw_meta:
            return None

        default_cat = None
        if raw_meta['type'] in ['movie', 'episode', 'moviesubtitle']:
            default_cat = 'video'
        elif raw_meta.has_key('episodeNumber'):
            default_cat = 'video'
        elif raw_meta.has_key('mimetype'):
            if raw_meta['mimetype'] in enzyme_mimes:
                default_cat = 'video'
            elif raw_meta['mimetype'] in mutagen_mimes:
                default_cat = 'audio'
        else:
            print('UNKNOWN DEFAULT CAT: %s' % full_path)
            pprint.pprint(raw_meta)

        for k,v in raw_meta.items():
            k = safe_unicode(k)
            if not k:
                continue
            v = safe_unicode(v)
            if not v:
                continue

            if k in self._ignored_tags:
                continue
            if k in self._tag_remapper.keys():
                k = self._tag_remapper[k]
            dstring = "K: %s; V: %s; T: %s" % (k, v, raw_meta['type'])

            if k in ['language', 'subtitleLanguage']:
                v = self.parse_language(v)
                if not default_cat:
                    print(dstring)
                    print('NO DEFAULT CATEGORY')
                    continue
                meta[default_cat][k] = v
            elif k == 'year':
                meta[self._tag_categories[k]]['date'] = self.parse_year(v)

            elif k in self._guess_categories:
                if not default_cat:
                    print(dstring)
                    print('NO DEFAULT CATEGORY')
                    continue
                meta[default_cat][k] = v

            elif k in self._tag_categories.keys():
                try:
                    cat = self._tag_categories[k]
                except KeyError:
                    if not default_cat:
                        print(dstring)
                        print('NO DEFAULT CATEGORY')
                        continue
                    cat = default_cat

                meta[cat][k] = v
            else:
                print(dstring)
                print('UNKNOWN KEY: %s' % k)
                continue

            """
            if k == 'other':
                meta[k] = v[0]
            elif k == 'date':
                meta[k] = v.isoformat()
            elif k in ['language', 'subtitleLanguage']:
                v = safe_unicode(v)
                if not v:
                    print('UNICODE DECODE FAILED: %s (%s)' % (k, v))
                    continue
                if ',' in v:
                    v = v.split(',')[0]
                v = v[10:]
                v = v[:len(v)-2]
                meta[k] = v
            elif k in ['screenSize']:
                meta['hd'] = self.parse_screensize_to_hd(v)
            else:
                meta[k] = v
            """

        for cat in ['audio', 'episode', 'file', 'release', 'video']:
            if len(meta[cat].keys()) == 0:
                del(meta[cat])

        if len(meta) > 0:
            return meta

if __name__ == '__main__':
    dirs = ['/export/movies']

    fmp = FileMetadataParser()
    for d in dirs:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                r = fmp.extract('%s/%s' % (path, f))
                #if r:
                #    pprint.pprint(fmp.extract('%s/%s' % (path, f)))
