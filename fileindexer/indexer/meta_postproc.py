import os

class MetadataPostProcessor:
    _text_mimes = [
        'application/msword',
        'application/pdf',
        'application/postscript',
        'application/vnd.oasis.opendocument.text',
        'application/x-info',
        'application/x-texinfo',
        'application/xml',
        'chemical/x-chemdraw'
    ]

    _archive_mimes = [
        'application/mac-binhex40',
        'application/rar',
        'application/x-7z-compressed',
        'application/x-apple-diskimage',
        'application/x-bittorrent',
        'application/x-stuffit',
        'application/x-tar',
        'application/x-wingz',
        'application/zip'
    ]

    _iso_mimes = ['application/x-iso9660-image']

    _code_mimes = [
        'application/x-tex-pk',
        'application/x-troff',
        'application/x-wais-source',
        'chemical/x-molconn-Z',
        'chemical/x-vamas-iso14976',
        'text/css',
        'text/x-c++src',
        'text/x-chdr',
        'text/x-csrc',
        'text/x-diff',
        'text/x-dsrc',
        'text/x-pascal',
        'text/x-perl',
        'text/x-python',
        'text/x-sh'
    ]

    _binary_mimes = [
        'application/octet-stream',
        'application/x-font',
        'application/x-ns-proxy-autoconfig'
    ]

    _checksum_mimes = [
        'application/pgp-keys',
        'application/pgp-signature',
        'application/x-md5',
        'application/x-sha1'
    ]

    _playlist_mimes = ['application/x-mpegURL']

    _executable_mimes = ['application/x-msdos-program']

    _text_exts = [
        '1st',
        '2nd',
        'AUX',
        'NFO',
        'README',
        'accurip',
        'aux',
        'changes',
        'cisco',
        'cnf',
        'compilation_problems',
        'conf',
        'contrib',
        'decw$book',
        'delivery',
        'diz',
        'dos',
        'examples',
        'guide',
        'help',
        'hlp',
        'inf',
        'ini',
        'int',
        'log',
        'message',
        'mms',
        'msg',
        'nfo',
        'nfo~',
        'package_name',
        'pc',
        'projects',
        'sub',
        'text',
        'title_page',
        'tpu',
        'tpu$section',
        'url',
        'vest_me',
        'xml_stuff'
    ]

    _binary_exts = [
        'IMA',
        'XB',
        'XM',
        'card',
        'db',
        'e',
        'fdl',
        'idx',
        'ipf_obj',
        'mar',
        'mem',
        'olb',
        'smc'
    ]

    _iso_exts = ['CUE', 'IMG', 'cue', 'mdf', 'mds']

    _audio_exts = ['ac3', 'ass', 'mp3-missing']

    _video_exts = ['BUP', 'IFO', 'M4V', 'VOB', 'f4v', 'img', 'mp7', 'ogm', 'vob']

    _checksum_exts = ['pem', 'sha256', 'sha512']

    _executable_exts = [
        'alpha_exe',
        'alpha_map',
        'alpha_obj',
        'alpha_olb',
        'axp_exe',
        'com_orig',
        'exe_alp_v72',
        'exe_alp_v721',
        'exe_alp_v732',
        'exe_alp_v82',
        'exe_alpha',
        'exe_axp',
        'exe_axp_v62',
        'exe_axp_v72',
        'exe_axp_v721',
        'exe_axp_v731',
        'exe_axp_v732',
        'exe_axp_v82',
        'exe_i64_v82',
        'exe_i64_v821',
        'exe_v62',
        'exe_v71',
        'exe_v72',
        'exe_v721',
        'exe_v73',
        'exe_v732',
        'exe_vax',
        'i64_exe',
        'ia64_exe',
        'ia64_obj',
        'int_img',
        'int_img_axp',
        'ipf_exe',
        'ipf_map',
        'ipf_olb',
        'itanium_exe',
        'itanium_obj',
        'obj_alpha',
        'obj_ia64',
        'obj_vax',
        'olb_alpha',
        'vax_exe',
        'vax_map',
        'vax_obj',
        'vax_olb',
        'vax_vaxc_exe'
    ]

    _code_exts = [
        '1_preformatted',
        'ac',
        'ad',
        'adb',
        'ads',
        'am',
        'asm',
        'awk',
        'b32',
        'bas',
        'blc',
        'bor',
        'build',
        'c_orig',
        'cld',
        'clp',
        'cob',
        'com_source',
        'cpl',
        'dcl',
        'def',
        'dj2',
        'djg',
        'dsm',
        'dsp',
        'dsw',
        'emx',
        'filter',
        'for',
        'gcc',
        'gnm',
        'gpr',
        'guess',
        'h_example',
        'h_in',
        'h_orig',
        'h_txt',
        'h_vms',
        'hlb',
        'icc',
        'icc',
        'in',
        'in_h',
        'inc',
        'iss',
        'jnl',
        'l',
        'lis',
        'm4',
        'macro',
        'macros',
        'main',
        'mak',
        'mbu',
        'mcl',
        'miff',
        'mlb',
        'msc',
        'nsi',
        'nt',
        'odl',
        'oldstyle',
        'opt',
        'opts',
        'os2',
        'pam',
        'postinst',
        'pov',
        'prj',
        'pup',
        'tab',
        'tab_c',
        'tab_h',
        'tbl',
        'tc',
        'tlb',
        'vc',
        'version',
        'vms_bash',
        'wavelet',
        'wnt',
        'xs',
        'y',
        'yy_c',
        'yy_c2',
        'yy_cc'
    ]

    _archive_exts = [
        '1_gz',
        'BCK',
        'ace',
        'bck',
        'bz2',
        'cckd',
        'depot',
        'gz',
        'lsm',
        'nzb',
        'par2',
        'pcsi',
        'pcsi$compressed',
        'qpg',
        'srr',
        'srs',
        'tar-bz2',
        'tar-gz',
        'tif-gz',
        'tif_gz'
    ]

    def parse_filetype(self, fname, v):
        meta = {}
        meta['is_text'] = False
        meta['is_iso'] = False
        meta['is_archive'] = False
        meta['is_binary'] = False
        meta['is_code'] = False
        meta['is_picture'] = False
        meta['is_audio'] = False
        meta['is_video'] = False
        meta['is_checksum'] = False
        meta['is_playlist'] = False
        meta['is_executable'] = False

        ## Begin with mimetype based parsing, and finish off with extension
        ## based parsing
        if v in self._text_mimes:
            meta['is_text'] = True
        elif v in self._archive_mimes:
            meta['is_archive'] = True
        elif v in self._iso_mimes:
            meta['is_iso'] = True
        elif v in self._code_mimes:
            meta['is_code'] = True
            meta['is_text'] = True
        elif v in self._binary_mimes:
            meta['is_binary'] = True
        elif v in self._checksum_mimes:
            meta['is_checksum'] = True
        elif v in self._playlist_mimes:
            meta['is_playlist'] = True
        elif v in self._executable_mimes:
            meta['is_executable'] = True
            meta['is_binary'] = True
        elif v.startswith('text/'):
            meta['is_text'] = True
        elif v.startswith('audio/'):
            meta['is_audio'] = True
        elif v.startswith('video/'):
            meta['is_video'] = True
        elif v.startswith('image/'):
            meta['is_picture'] = True

        elif v in self._text_exts:
            meta['is_text'] = True
        elif v in self._binary_exts:
            meta['is_binary'] = True
        elif v in self._iso_exts:
            meta['is_iso'] = True
        elif v in self._audio_exts:
            meta['is_audio'] = True
        elif v in self._video_exts:
            meta['is_video'] = True
        elif v in self._checksum_exts:
            meta['is_checksum'] = True
        elif v in self._executable_exts:
            meta['is_executable'] = True
            meta['is_binary'] = True
        elif v in self._code_exts:
            meta['is_code'] = True
            meta['is_text'] = True
        elif v in self._archive_exts:
            meta['is_archive'] = True
        elif v.startswith('r') or v.startswith('s'):
            try:
                int(v[1:])
                meta['is_archive'] = True
            except ValueError:
                pass
        elif v.endswith('_wavelet'):
            meta['is_code'] = True
            meta['is_text'] = True
        elif v == '':
            pass

        else:
            try:
                int(v)
                meta['is_binary'] = True
            except ValueError:
                pass
        return meta

    def parse_bitrate(self, k, v):
        meta = {}

        if k == 'bitrate':
            prefix = 'video'
        elif k == 'audio_bitrate':
            prefix = 'audio'
        elif k == 'file_bitrate':
            prefix = 'audio'
        elif k == 'video_bitrate':
            prefix = 'video'
        else:
            return meta

        if '(Variable bit rate)' in v:
            meta['vbr'] = True
        else:
            meta['vbr'] = False

        t = v.split()
        if t[1] == 'bit/s':
            meta['%s_bitrate' % prefix] = float(t[0])
        elif t[1] == 'Kbit/sec':
            meta['%s_bitrate' % prefix] = float(t[0])*1024
        elif t[1] == 'Mbit/sec':
            meta['%s_bitrate' % prefix] = float(t[0])*1024*1024
        elif t[1] == 'Gbit/sec':
            meta['%s_bitrate' % prefix] = float(t[0])*1024*1024*1024

        return meta

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

        #if meta != {}:
        #    meta['keyword'] = k

        return meta

    def parse_compression_rate(self, v):
        return float(v.replace('x', ''))

    def parse_title(self, k, v):
        meta = {}

        if k == 'file_title':
            prefix = 'audio'
        elif k == 'audio_title':
            prefix = 'audio'
        elif k == 'video_title':
            prefix = 'video'
        elif k == 'title':
            prefix = 'video'
        else:
            return meta

        meta['%s_title' % prefix] = v
        return meta

    def parse_channel(self, v):
        meta = {}
        if v in ['mono', 'Single channel']:
            meta['stereo'] = False
            meta['channels'] = 1
        elif v in ['Stereo', 'Joint stereo', 'Dual channel', 'stereo']:
            meta['stereo'] = True
            meta['channels'] = 2
        else:
            try:
                channels = int(v)
                meta['stereo'] = True
                meta['channels'] = channels
            except:
                pass

        return meta

    def parse_endianness(self, v):
        meta = {}
        if v in ['Little endian']:
            meta['endianness'] = 'little'
        elif v in ['Big endian']:
            meta['endianness'] = 'big'
        return meta

    def parse_samplerate(self, v):
        if isinstance(v, int) or isinstance(v, float):
            return {'samplerate': v}
        else:
            return {'samplerate': float(v.split()[0])}

    def parse_duration(self, k, v):
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

        return {'duration': total}

    def parse_language(self, k, v):
        if k == 'file_language':
            k = 'audio_language'
        return {k: v}

    def parse_framerate(self, v):
        return {'framerate': int(v.split('.')[0])}

    def process(self, raw_meta):
        meta = {}
        meta['filetype'] = os.path.splitext(raw_meta['filename'])[1][1:]

        if raw_meta.has_key('mime'):
            meta.update(self.parse_filetype(raw_meta['filename'], raw_meta['mime']))
        else:
            meta.update(self.parse_filetype(raw_meta['filename'], meta['filetype']))

        for k,v in raw_meta.items():
            if 'height' in k:
                meta['height'] = self.parse_length(v)
            elif 'width' in k:
                meta['width'] = self.parse_length(v)
            elif 'bitrate' in k:
                meta.update(self.parse_bitrate(k, v))
            elif 'compression' in k and not '_rate' in k:
                meta.update(self.parse_compression(k, v))
            elif 'compression_rate' in k:
                meta['compression_rate'] = self.parse_compression_rate(v)
            elif 'artist' in k:
                meta['artist'] = v
            elif 'album' in k:
                meta['album'] = v
            elif 'author' in k:
                meta['author'] = v
            elif 'producer' in k:
                meta['producer'] = v
            elif 'title' in k and not 'language' in k:
                meta.update(self.parse_title(k, v))
            elif 'comment' in k:
                meta['comment'] = v
            elif 'channel' in k:
                meta.update(self.parse_channel(v))
            elif 'endian' in k:
                meta.update(self.parse_endianness(v))
            elif 'samplerate' in k:
                meta.update(self.parse_samplerate(v))
            elif 'duration' in k:
                if isinstance(v, int) or isinstance(v, float):
                    continue
                meta.update(self.parse_duration(k, v))
            elif 'language' in k:
                meta.update(self.parse_language(k, v))
            elif 'framerate' in k:
                if not 'framerate' in meta.keys():
                    meta.update(self.parse_framerate(v))
            elif k == 'file':
                pass
            elif k in ['uid', 'checksum', 'ctime', 'filename', 'gid', 'mode', 'mtime', 'is_dir', 'atime', 'full_path', 'size', 'mime']:
                meta[k] = v

        keys = meta.keys()
        if not meta['is_dir'] and meta['is_video'] and 'width' in keys and 'height' in keys:
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
        return meta
