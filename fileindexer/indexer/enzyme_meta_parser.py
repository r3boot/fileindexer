import os
import pprint
import sys

sys.path.append('/people/r3boot/fileindexer')

import enzyme

from fileindexer.indexer.parser_utils import *

enzyme_mimes = [
    'video/x-matroska',
    'application/vnd.rn-realmedia',
    'application/vnd.rn-realmedia-secure',
    'application/vnd.rn-realmedia-vbr',
    'application/x-pn-realmedia',
    'audio/vnd.rn-realvideo',
    'audio/vnd.rrn-realvideo',
    'audio/x-pn-realvideo',
    'video/vnd.rn-realvideo',
    'video/vnd.rn-realvideo-secure',
    'video/vnd-rn-realvideo',
    'video/x-pn-realvideo',
    'video/x-pn-realvideo-plugin',
    'video/x-msvideo',
    'application/futuresplash',
    'application/x-shockwave-flash',
    'application/x-shockwave-flash2-preview',
    'video/vnd.sealed.swf',
    'application/wmf',
    'application/x-msmetafile',
    'application/x-wmf',
    'image/wmf',
    'image/x-win-metafile',
    'image/x-wmf',
    'zz-application/zz-winassoc-wmf',
    'application/vnd.ms-asf',
    'application/x-mplayer2',
    'video/x-ms-asf',
    'video/x-la-asf',
    'video/x-ms-asf',
    'video/x-ms-asf-plugin',
    'video/x-ms-wm',
    'video/x-ms-wmx',
    'video/x-flv',
    'image/mov',
    'video/quicktime',
    'video/sgi-movie',
    'video/vnd.sealedmedia.softseal.mov',
    'video/x-quicktime',
    'video/x-sgi-movie',
]

class EnzymeMetadataParser:
    _allowed_stream_keys = ['audio', 'video', 'chapters', 'subtitles', 'mime', 'title']
    _ignored_stream_keys = ['corrupt', 'title', 'length']

    _key_remapper = {
        'aspect':    'aspectratio',
        'timestamp': 'date',
        'type':      'container',
    }

    _key_categories = {
        'container':    'release',
        'date':         'release',
        'mime':         'file',
    }

    _ignored_tags = ['delay', 'mime', 'codec_private', 'default', 'enabled', 'id', 'pos']

    _subcategories = [
        'audio',
        'chapters',
        'subtitles',
        'video',
    ]

    def _remove_useless(self, cat_meta):
        all_items = []
        for stream_meta in cat_meta:
            stream_keys = stream_meta.keys()
            if 'codec' in stream_keys:
                all_items.append(stream_meta)
            elif 'channels' in stream_keys:
                all_items.append(stream_meta)
            else:
                print('UNKNOWN USELESS STREAM KEY: %s' % stream_keys)
                continue
        return all_items

    def remove_empty_values(self, raw_meta):
        result = {}
        for key, value in raw_meta.items():
            if value is None:
                continue
            elif key in self._subcategories:
                subcat_result = []
                for item in raw_meta[key]:
                    tmp_item = {}
                    for subkey, subvalue in item.items():
                        if subvalue is None:
                            continue
                        elif subkey in ['tags']:
                            continue
                        tmp_item[subkey] = subvalue
                    subcat_result.append(tmp_item)
                result[key] = subcat_result
            else:
                result[key] = value
        return result

    def extract(self, full_path):
        meta = {
            'audio':   [],
            'file':    {},
            'release': {},
            'video':   [],
        }
        try:
            raw_meta = None
            raw_meta = enzyme.parse(full_path)
        except enzyme.exceptions.ParseError:
            error('Failed to parse %s' % full_path)
            return {}
        except enzyme.exceptions.NoParserError:
            error('No parser found for %s' % full_path)
            return {}
        except ValueError, errmsg:
            error('Failed to parse %s: %s' % (full_path, errmsg))
            return {}
        except TypeError, errmsg:
            error('Failed to parse %s: %s' % (full_path, errmsg))
            return {}
        except IndexError, errmsg:
            error('Failed to parse %s: %s' % (full_path, errmsg))
            return {}

        raw_values = self.remove_empty_values(raw_meta.convert())

        for stream_key, stream_value in raw_values.items():

            if not stream_value:
                continue

            if stream_key in self._ignored_stream_keys:
                continue

            if stream_key in self._key_remapper.keys():
                stream_key = self._key_remapper[stream_key]

            default_cat = None
            if stream_key in ['audio']:
                default_cat = stream_key
            elif stream_key in ['video', 'chapters', 'subtitles']:
                default_cat = 'video'
            elif stream_key in self._key_categories.keys():
                default_cat = self._key_categories[stream_key]
            else:
                print('UNKNOWN DEFAULT CAT: %s: %s->%s' % (full_path, stream_key, stream_value))
                continue

            if stream_key in self._subcategories:
                id = 0

                for stream_obj in stream_value:
                    stream_meta = { 'stream_id': id }
                    for s_key, s_value in stream_obj.items():
                        if s_key in self._ignored_tags:
                            continue

                        if s_key in self._key_remapper.keys():
                            s_key = self._key_remapper[s_key]

                        stream_meta[s_key] = s_value

                    meta[default_cat] = merge_av_meta_dict(meta[default_cat], [stream_meta])
            else:
                meta[default_cat][stream_key] = stream_value

        return meta

if __name__ == '__main__':
    dirs = ['/export/series']

    emp = EnzymeMetadataParser()
    for d in dirs:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                print("==> %s/%s" % (path, f))
                r = emp.extract('%s/%s' % (path, f))
                if r:
                    pprint.pprint(r)
