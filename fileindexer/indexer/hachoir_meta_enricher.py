import os

class HachoirMetaEnricher:
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
        if v in ['application/pdf', 'chemical/x-chemdraw', 'application/vnd.oasis.opendocument.text', 'application/postscript', 'application/xml', 'application/msword', 'application/x-texinfo', 'application/x-info']:
            meta['is_text'] = True
        elif v in ['application/zip', 'application/rar', 'application/x-wingz', 'application/x-tar', 'application/x-bittorrent', 'application/x-stuffit', 'application/x-7z-compressed', 'application/x-apple-diskimage', 'application/mac-binhex40']:
            meta['is_archive'] = True
        elif v in ['application/x-iso9660-image']:
            meta['is_iso'] = True
        elif v in ['text/x-python', 'text/x-csrc', 'text/x-diff', 'application/x-troff', 'chemical/x-vamas-iso14976', 'text/x-chdr', 'text/x-c++src', 'chemical/x-molconn-Z', 'text/css', 'text/x-perl', 'text/x-sh', 'text/x-pascal', 'text/x-dsrc', 'application/x-wais-source', 'application/x-tex-pk']:
            meta['is_code'] = True
            meta['is_text'] = True
        elif v in ['application/octet-stream', 'application/x-ns-proxy-autoconfig', 'application/x-font']:
            meta['is_binary'] = True
        elif v in ['application/x-md5', 'application/x-sha1', 'application/pgp-signature', 'application/pgp-keys']:
            meta['is_checksum'] = True
        elif v in ['application/x-mpegURL']:
            meta['is_playlist'] = True
        elif v in ['application/x-msdos-program']:
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

        elif v in ['nfo', 'nfo~', 'diz', 'log', 'message', 'NFO', 'ini', 'sub', 'accurip', 'url', 'README', 'AUX', 'aux', 'help', 'changes', 'dos', '2nd', 'hlp', 'mms', 'msg', 'compilation_problems', 'xml_stuff', '1st', 'cnf', 'conf', 'int', 'tpu', 'decw$book', 'package_name', 'vest_me', 'title_page', 'guide', 'delivery', 'inf', 'tpu$section', 'pc', 'projects', 'examples', 'contrib', 'text', 'cisco']:
            meta['is_text'] = True
        elif v in ['db', 'smc', 'idx', 'IMA', 'XM', 'XB', 'mem', 'card', 'mar', 'ipf_obj', 'olb', 'fdl', 'e']:
            meta['is_binary'] = True
        elif v in ['cue', 'mds', 'mdf', 'CUE', 'IMG']:
            meta['is_iso'] = True
        elif v in ['ass', 'mp3-missing', 'ac3']:
            meta['is_audio'] = True
        elif v in ['ogm', 'f4v', 'img', 'vob', 'mp7', 'VOB', 'M4V', 'IFO', 'BUP']:
            meta['is_video'] = True
        elif v in ['sha256', 'sha512', 'pem']:
            meta['is_checksum'] = True
        elif v in ['alpha_exe', 'alpha_obj', 'vax_exe', 'vax_obj', 'ia64_exe', 'ia64_obj', 'com_orig', 'alpha_olb', 'alpha_map', 'ipf_exe', 'ipf_map', 'ipf_olb', 'vax_olb', 'vax_map', 'itanium_obj', 'exe_axp', 'exe_v721', 'exe_v73', 'exe_v72', 'axp_exe', 'i64_exe', 'exe_axp_v72', 'exe_axp_v721', 'exe_axp_v732', 'exe_i64_v821', 'exe_axp_v82', 'exe_v62', 'exe_v732', 'exe_axp_v62', 'exe_axp_v731', 'exe_i64_v82', 'exe_vax', 'exe_alpha', 'int_img', 'int_img_axp', 'exe_v71', 'exe_alp_v72', 'exe_alp_v721', 'exe_alp_v732', 'exe_alp_v82', 'obj_alpha', 'obj_ia64', 'obj_vax', 'itanium_exe', 'vax_vaxc_exe', 'olb_alpha']:
            meta['is_executable'] = True
            meta['is_binary'] = True
        elif v in ['vms_bash', 'for', 'c_orig', 'version', 'opt', 'inc', 'cld', 'hlb', 'h_orig', '1_preformatted', 'def', 'dsp', 'msc', 'mlb', 'bas', 'macros', 'm4', 'gcc', 'h_in', 'in', 'am', 'prj', 'opts', 'os2', 'h_txt', 'guess', 'ac', 'dcl', 'cob', 'tlb', 'h_vms', 'nt', 'vc', 'macro', 'l', 'tab_h', 'y', 'h_example', 'com_source', 'asm', 'bor', 'djg', 'cpl', 'jnl', 'xs', 'pov', 'miff', 'gnm', 'pam', 'b32', 'wavelet', 'mcl', 'blc', 'icc', 'wnt', 'mak', 'awk', 'emx', 'icc', 'ad', 'iss', 'nsi', 'dsm', 'dsw', 'odl', 'in_h', 'pup', 'adb', 'clp', 'build', 'postinst', 'dj2', 'tc', 'ads', 'gpr', 'lis', 'tab', 'main', 'mbu', 'tbl', 'filter', 'yy_c', 'yy_cc', 'yy_c2', 'oldstyle', 'tab_c']:
            meta['is_code'] = True
            meta['is_text'] = True
        elif v in ['par2', 'nzb', 'gz', 'ace', 'lsm', 'pcsi', 'bz2', 'cckd', 'depot', 'srr', 'srs', 'pcsi$compressed', 'tar-gz', 'bck', 'tif_gz', 'tif-gz', '1_gz', 'BCK', 'qpg', 'tar-bz2']:
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

        if meta != {}:
            meta['keyword'] = k

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
            meta[' endianness'] = 'big'
        return meta

    def parse_samplerate(self, v):
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

    def enrich(self, raw_meta):
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
