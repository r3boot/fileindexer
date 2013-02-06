import os
import re

import guessit

from fileindexer.indexer.safe_unicode import safe_unicode

class FileMetadataParser:
    _re_release_dir = re.compile('.*[-.][a-zA-Z0-9]*\-([a-zA-Z0-9]*)$')
    _ignored_tags = [
        'audioChannels',
        'audioCodec',
        'bonusNumber',
        'country',
        'edition',
        'extension',
        'filmNumber',
        'filmSeries',
        'height',
        'mimetype',
        'subtitleLanguage',
        'title',
        'type',
        'website',
        'width',
        'year',
    ]

    _remapped_tags = {
        'cdNumber': 'disc.nr',
        'container': 'release.container',
        'episodeNumber': 'episode.nr',
        'format': 'disc.format',
        'other': 'release.other',
        'releaseGroup': 'release.group',
        'season': 'episode.season',
        'series': 'episode.series',
        'videoCodec': 'video.format',
    }

    def parse_screensize_to_hd(self, value):
        if value in ['720p', '1080p']:
            return True
        else:
            return False

    def extract(self, input_meta):
        filename = input_meta['full_path']
        meta = {}
        release_dir = os.path.basename(os.path.dirname(filename))
        match = self._re_release_dir.search(release_dir)
        if match:
            meta['release.name'] = release_dir
            meta['release.group'] = match.group(1)

        try:
            raw_meta = guessit.guess_file_info(filename, 'autodetect')
        except KeyError:
            return meta

        for k,v in raw_meta.items():
            if k in self._ignored_tags:
                continue
            if k in self._remapped_tags.keys():
                k = self._remapped_tags[k]

            if k == 'other':
                meta[k] = v[0]
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

        if len(meta) > 0:
            return meta
