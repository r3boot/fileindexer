import os
import pprint

import enzyme

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

    _tag_remapper = {
    }

    def _add_to_subcat(self, meta, default_cat, stream_meta):
        all_items = []
        if len(meta[default_cat]) == 0:
            meta[default_cat] = [stream_meta]
        else:
            has_been_updated = False
            for item in meta[default_cat]:
                if not item.has_key('stream_id'):
                    continue

                if item['stream_id'] == stream_meta['stream_id']:
                    item.update(stream_meta)
                    has_been_updated = True
                all_items.append(item)

            if not has_been_updated:
                all_items.append(stream_meta)

            meta[default_cat] = all_items

        return meta

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
            print('[E] Failed to parse %s' % full_path)
            return {}
        except enzyme.exceptions.NoParserError:
            #print('[E] No parser found for %s' % full_path)
            return {}
        except ValueError, e:
            print('[E] Failed to parse %s: %s' % (full_path, e))
            return {}
        except TypeError, e:
            print('[E] Failed to parse %s: %s' % (full_path, e))
            return {}
        except IndexError, e:
            print('[E] Failed to parse %s: %s' % (full_path, e))
            return {}

        for stream_key, stream_value in dict(raw_meta).items():
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

            try:
                id = 0
                for stream_obj in stream_value:
                    stream_meta = { 'stream_id': id }
                    stream = dict(stream_obj)
                    for s_key, s_value in stream.items():
                        if not s_value:
                            continue
                        if s_key in self._ignored_tags:
                            continue

                        if s_key in self._tag_remapper.keys():
                            s_key = self._tag_remapper[s_key]
                        stream_meta[s_key] = s_value
                    meta = self._add_to_subcat(meta, default_cat, stream_meta)
                    id += 1
            except ValueError:
                meta[default_cat][stream_key] = stream_value.strip()
            except TypeError:
                meta[default_cat][stream_key] = stream_value

        for cat in ['audio', 'video']:
            tmp = self._remove_useless(meta[cat])
            meta[cat] = tmp

        return meta

if __name__ == '__main__':
    dirs = ['/export/series']

    emp = EnzymeMetadataParser()
    for d in dirs:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                r = emp.extract('%s/%s' % (path, f))
                if r:
                    pprint.pprint(r)
