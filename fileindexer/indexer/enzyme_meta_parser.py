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
    _ignored_tags = ['delay', 'mime', 'codec_private', 'default', 'enabled', 'id', 'pos']

    _remapped_tags = {
        'type': 'release.container',
        'progressive': 'video.progressive',
        'copyright': 'release.copyright',
        'samplerate': 'video.samplerate',
        'fourcc': 'encoder.fourcc',
        'codec': 'video.format',
        'bitrate': 'bitrate',
    }
    def extract(self, raw_meta):
        meta = {}
        fname = raw_meta['full_path']
        try:
            raw_meta = None
            raw_meta = enzyme.parse(fname)
        except enzyme.exceptions.ParseError:
            print('[E] Failed to parse %s' % fname)
            return {}
        except enzyme.exceptions.NoParserError:
            #print('[E] No parser found for %s' % fname)
            return {}
        except ValueError, e:
            print('[E] Failed to parse %s: %s' % (fname, e))
            return {}
        except TypeError, e:
            print('[E] Failed to parse %s: %s' % (fname, e))
            return {}
        except IndexError, e:
            print('[E] Failed to parse %s: %s' % (fname, e))
            return {}

        for k,v in dict(raw_meta).items():
            if v:
                if k in ['audio', 'video', 'chapters', 'subtitles']:
                    j = 0
                    for i in v:
                        tmp = dict(i)
                        for k_tmp, v_tmp in tmp.items():
                            if k_tmp in self._ignored_tags:
                                continue
                            if not v_tmp:
                                continue
                            key = '%s.%s.%s' % (k, j, k_tmp)
                            meta[key] = v_tmp
                        j += 1
                else:
                    meta[k] = v
        return meta
