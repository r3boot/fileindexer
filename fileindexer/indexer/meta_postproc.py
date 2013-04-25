import os

import pprint

from fileindexer.constants import category_types, mimes, extensions

class MetadataPostProcessor:
    def parse_filetype(self, fname, hint):
        result = 'unknown'

        for name, mimetypes in mimes.items():
            if hint in mimetypes:
                return category_types[name]

        if hint.startswith('text/'):
            return category_types['text']
        elif hint.startswith('audio/'):
            return category_types['audio']
        elif hint.startswith('video/'):
            return category_types['video']
        elif hint.startswith('image/'):
            result = category_types['picture']

        for name, extlist in extensions.items():
            if hint in extlist:
                return category_types[name]

        if hint.startswith('r') or hint.startswith('s'):
            try:
                int(hint[1:])
                return category_types['archive']
            except ValueError:
                pass
        elif hint.endswith('_wavelet'):
            return category_types['code']

        return result

    def parse_length(self, v):
        if isinstance(v, int) or isinstance(v, float):
            return v
        else:
            return int(v.split()[0])

    def parse_compression(self, k, v):
        remapper = {
            'deflate': ['deflate'],
            'lzw': ['LZW'],
            'jpeg': ['JPEG (Baseline)', 'JPEG (Progressive)'],
            'null': ['Uncompressed', '(empty) (fourcc:"")'],
            'ac3': ['A_AC3', 'AC3', 'AC3 (fourcc:"\\1")'],
            'aac': ['A_AAC', 'A_AAC/MPEG4/LC/SBR', 'A_AAC/MPEG2/LC/SBR', 'A_AAC/MPEG2/LC', 'A_AAC/MPEG4/LC'],
            'dts': ['A_DTS'],
            'text': ['S_TEXT/UTF8', 'S_TEXT/SSA', 'S_TEXT/ASS', 'S_VOBSUB', 'S_HDMV/PGS'],
            'vcm': ['V_MS/VFW/FOURCC'],
            'mpeg': ['V_MPEG4/ISO/AVC', 'A_MPEG/L3', 'Microsoft MPEG-4 (fast-motion)', 'Microsoft MPEG-4 (fast-motion) (fourcc:"MP43")', 'Microsoft MPEG', 'Microsoft MPEG-4 (fast-motion) (fourcc:"mp43")', 'Microsoft MPEG-4 (low-motion) (fourcc:"mp42")', 'Microsoft MPEG (fourcc:"\\1")', 'FMP4" (fourcc:"FMP4")', 'Microsoft MPEG-4 (low-motion) (fourcc:"MP42")', '"FMP4" (fourcc:"FMP4")', 'YVU12 Planar (fourcc:"yv12")'],
            'vorbis': ['A_VORBIS'],
            'divx': ['DivX v4 (fourcc:"DIVX")', 'DivX v4 (fourcc:"divx")', 'XviD MPEG-4 (fourcc:"xvid")', 'XviD MPEG-4 (fourcc:"XVID")', 'DivX v3 MPEG-4 Low-Motion (fourcc:"div3")', 'DivX v3 MPEG-4 Fast-Motion (fourcc:"div4")', 'dvx4" (fourcc:"dvx4")', 'DivX v3 MPEG-4 Fast-Motion (fourcc:"DIV4")', 'XviD MPEG-4 (fourcc:"XviD")', 'DivX v5 (fourcc:"DX50")', 'DivX v3 MPEG-4 Low-Motion (fourcc:"DIV3")', '"dx52" (fourcc:"dx52")', '"dvx4" (fourcc:"dvx4")'],
            'wma': ['Windows Media Audio V7 / V8 / V9', 'Windows Media Audio Professional V9'],
            'wmv': ['Windows Media Video V9', 'Windows Media Video V8', 'Windows Media Video V9 (fourcc:"WMV3")', 'Windows Media Video V9 (fourcc:"wmv3")'],
            'mp3': ['MPEG Layer 3', 'MPEG Layer 3 (fourcc:"\\1")', 'MPEG Layer 3 (fourcc:"U")'],
            'h264': ['Intel ITU H.264 Videoconferencing (fourcc:"h264")', 'Intel ITU H.264 Videoconferencing (fourcc:"H264")'],
            'pcm': ['Microsoft Pulse Code Modulation (PCM)', 'Microsoft ADPCM'],
            'cvid': ['Radius Cinepak (fourcc:"cvid")']
        }

        meta = {}
        for s,l in remapper.items():
            for item in l:
                if v == item:
                    meta['compression'] = s
                    meta['compressor'] = v

        if meta == {}:
            v_l = v.lower()
            if 'ac3' in v_l:
                meta['compression'] = 'ac3'
            elif 'deflate' in v_l:
                meta['compression'] = 'deflate'
            elif 'lzw' in v_l:
                meta['compression'] = 'lzw'
            elif 'jpeg' in v_l or 'jpg' in v_l:
                meta['compression'] = 'jpeg'
            elif 'aac' in v_l:
                meta['compression'] = 'aac'
            elif 'dts' in v_l:
                meta['compression'] = 'dts'
            elif 'microsoft mpeg' in v_l:
                meta['compression'] = 'mpeg'
            elif 'divx ' in v_l or 'xvid ' in v_l:
                meta['compression'] = 'divx'
            elif 'windows media audio' in v_l:
                meta['compression'] = 'wma'
            elif 'windows media video' in v_l:
                meta['compression'] = 'wmv'
            elif 'mpeg layer 3' in v_l:
                meta['compression'] = 'mp3'
            elif 'h.264' in v_l or 'h264' in v_l:
                meta['compression'] = 'h264'
            elif 'pcm' in v_l:
                meta['compression'] = 'pcm'
            elif 'cinepak' in v_l:
                meta['compression'] = 'cvid'
            elif 'uncompressed' in v_l:
                meta['compression'] = 'null'

            if meta.has_key('compression'):
                meta['compressor'] = v

        return meta

    """
    def parse_video_meta(self, meta):
        keys = meta['video'].keys()
        if meta['category'] == category_types['video']:
            if not 'width' in keys and 'height'
            if meta['width'] <= 720 and meta['height'] <= 480:
                meta['video_format'] = 'vga'
                meta['aspect_ratio'] = '4:3'
                meta['hd'] = False
            elif meta['width'] <= 768 and meta['height'] <= 576:
                meta['video_format'] = 'pal'
                meta['aspect_ratio'] = '4:3'
                meta['hd'] = False
            elif meta['width'] <= 1024 and meta['height'] <= 768:
                meta['video_format'] = 'xga'
                meta['aspect_ratio'] = '4:3'
                meta['hd'] = False
            elif meta['width'] <= 1280 and meta['height'] <= 720:
                meta['video_format'] = '720p'
                meta['aspect_ratio'] = '16:9'
                meta['hd'] = True
            elif meta['width'] <= 1920 and meta['height'] <= 1080:
                meta['video_format'] = '1080p'
                meta['aspect_ratio'] = '16:9'
                meta['hd'] = True
    """

    def process(self, meta):

        meta['file']['type'] = os.path.splitext(meta['file']['name'])[1][1:]

        if meta.has_key('category') and meta['category'] == category_types['dir']:
            return meta

        if meta['file'].has_key('mime'):
            meta['category'] = self.parse_filetype(meta['file']['name'], meta['file']['mime'])
        else:
            meta['category'] = self.parse_filetype(meta['file']['name'], meta['file']['type'])

        return meta
