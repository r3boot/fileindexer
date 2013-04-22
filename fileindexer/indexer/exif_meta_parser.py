import datetime
import time
import os
import pprint
import sys

sys.path.append('/people/r3boot/fileindexer')


from fileindexer.indexer.safe_unicode import safe_unicode
from fileindexer.external.exif import EXIF

exif_mimes = [
    'image/bmp',
    'image/ms-bmp',
    'image/vnd.wap.wbmp',
    'image/x-bitmap',
    'image/x-bmp',
    'image/x-ms-bmp',
    'image/x-win-bitmap',
    'image/x-windows-bmp',
    'image/x-xbitmap',
    'image/gi_',
    'image/gif',
    'image/vnd.sealedmedia.softseal.gif',
    'image/ico',
    'image/x-icon',
    'image/jpe_',
    'image/jpeg',
    'image/jpeg2000',
    'image/jpeg2000-image',
    'image/jpg',
    'image/pjpeg',
    'image/vnd.sealedmedia.softseal.jpeg',
    'image/vnd.swiftview-jpeg',
    'image/x-jpeg2000-image',
    'image/pcx',
    'image/vnd.swiftview-pcx',
    'image/x-pc-paintbrush',
    'image/x-pcx',
    'image/png',
    'image/vnd.sealed.png',
    'image/photoshop',
    'image/psd',
    'image/x-photoshop',
    'image/targa',
    'image/x-targa',
    'image/tga',
    'image/x-tga',
    'image/tiff',
    'image/x-tiff',
    'image/wmf',
    'image/x-win-metafile',
    'image/x-wmf',
    'image/xcf',
    'image/x-xcf',
]

class ExifMetadataParser:
    _ignored_tags = [
        'EXIF CompressedBitsPerPixel',
        'EXIF CustomRendered',
        'EXIF CVAPattern',
        'EXIF FocalPlaneResolutionUnit',
        'EXIF FocalPlaneXResolution',
        'EXIF FocalPlaneYResolution',
        'EXIF GainControl',
        'EXIF InteroperabilityOffset',
        'EXIF MakerNote',
        'EXIF SubSecTimeDigitized',
        'EXIF SubSecTimeOriginal',
        'EXIF Tag 0x',
        'MakerNote',
        'Filename',
        'Image ExifOffset',
        'Image ResolutionUnit',
        'Image Tag',
        'Image WhitePoint',
        'Image XResolution',
        'Image YResolution',
        'JPEGThumbnail',
        'TIFFThumbnail',
        'Thumbnail',
        'Camera focal',
        'Camera exposure',
        'Camera aperture',
        'EXIF ComponentsConfiguration',
        'EXIF ApertureValue',
        'EXIF Contrast',
        'EXIF DigitalZoomRatio',
        'EXIF ExposureBiasValue',
        'EXIF ExposureMode',
        'EXIF ExposureTime',
        'EXIF FileSource',
        'EXIF FlashPixVersion',
        'EXIF Flash',
        'EXIF FNumber',
        'EXIF ExifVersion',
        'EXIF FocalLength',
        'EXIF ISOSpeedRatings'
        'EXIF LightSource',
        'EXIF MaxApertureValue',
        'EXIF MeteringMode',
        'EXIF Saturation',
        'EXIF SceneCaptureType',
        'EXIF SceneType',
        'EXIF SensingMethod',
        'EXIF Sharpness',
        'EXIF ShutterSpeedValue',
        'EXIF SubjectDistance',
        'EXIF SubjectDistanceRange',
        'EXIF WhiteBalance',
        'Image YCbCrPositioning',
        'Image Padding',
        'EXIF Gamma',
        'Image YCbCrCoefficients',
        'EXIF SubSecTime',
        'EXIF Padding',
        'Image PrimaryChromaticities',
        'Image XPAuthor',
        'EXIF ISOSpeedRatings',
        'Image BitsPerSample',
        'Image SamplesPerPixel',
        'EXIF LightSource',
        'GPS GPSVersionID',
        'Image GPSInfo',
        'Image PhotometricInterpretation',
        'Image XPTitle',
        'Image XPKeywords',
        'Image XPSubject',
        'Image XPComment',
        'Image PlanarConfiguration',
        'Image DocumentName',
        'Image StripByteCounts',
        'Image RowsPerStrip',
        'Image StripOffsets',
        'Image FillOrder',
        'EXIF DeviceSettingDescription',
        'Image DeviceSettingDescription',
        'Image ReferenceBlackWhite',
        'Image WhiteBalance',
        'Image SceneCaptureType',
        'Image ExposureMode',
        'Image CustomRendered',
        'Image Rating',
        'EXIF BrightnessValue',
        'Image MakerNote',
        'GPS GPSTimeStamp',
        'EXIF ExposureIndex',
        'Image PrintIM',
        'EXIF JPEGInterchangeFormat',
        'EXIF JPEGInterchangeFormatLength',
        'Image Sharpness',
        'Image Saturation',
        'Image SubjectDistanceRange',
        'Image FocalLengthIn35mmFilm',
        'Image GainControl',
        'Image Contrast',
        'Image DigitalZoomRatio',
        'EXIF PrintIM',
        'Image PageName',
        'EXIF OECF',
        'Image Gamma',
        'Image InterColorProfile',
        'Image IPTC/NAA',
    ]

    _remapped_tags = {
        'Image Artist':                     'artist',
        'EXIF ColorSpace':                  'colorspace',
        'EXIF DateTimeDigitized':           'date',
        'EXIF DateTimeOriginal':            'date',
        'EXIF DateTime':                    'date',
        'EXIF ExifVersion':                 'exif_version',
        'EXIF ExifImageLength':             'height',
        'EXIF ExifImageWidth':              'width',
        'EXIF UserComment':                 'comment',
        'EXIF ExposureProgram':             'orientation',
        'Image DateTime':                   'date',
        'Image ImageDescription':           'description',
        'Image Make':                       'hwvendor',
        'Image Compression':                'compressor',
        'Image Model':                      'hwmodel',
        'Image Orientation':                'orientation',
        'Image Software':                   'software',
        'Image ExifImageLength':            'height',
        'Image ExifImageWidth':             'width',
        'Image ImageLength':                'height',
        'Image ImageWidth':                 'width',
        'Image Copyright':                  'copyright',
        'GPS GPSDate':                      'date',
        'GPS GPSLatitudeRef':               'latref',
        'GPS GPSLatitude':                  'lat',
        'GPS GPSLongitudeRef':              'lonref',
        'GPS GPSLongitude':                 'lon',
    }

    _key_categories = {
        'date':             'release',
        'exif_version':     'release',
        'hwvendor':         'release',
        'hwmodel':          'release',
        'software':         'release',
        'copyright':        'release',
    }

    _string_fields = [
        'artist',
        'comment',
        'description',
        'hwmodel',
        'hwendor',
        'software',
        'lat',
        'latref',
        'lon',
        'lonref',
    ]

    _int_fields = [
        'exif_version',
        'width',
        'height',
    ]

    _bool_fields = [
    ]

    _datetime_fields = [
        'date',
    ]

    _time_formats = [
        '%Y:%m:%d %H:%M:%S',
        '%d %b %Y %H:%M:%S',
        '%Y:%m:%d'
    ]

    def extract(self, full_path):
        meta = {
            'image': {}
        }
        filename = full_path
        try:
            fd = open(filename, 'rb')
        except IOError, e:
            print(e)
            print('Failed to open %s' % filename)
            return

        try:
            raw_meta = EXIF.process_file(fd, details=True, strict=False, debug=False)
        except MemoryError:
            print('Out-Of-Memory during EXIF.process_file')
            fd.close()
            return {}
        fd.close()

        for k,v in raw_meta.items():
            ignore_tag = False
            for i in self._ignored_tags:
                if k.startswith(i):
                    ignore_tag = True
                    break
            if ignore_tag:
                continue

            if not k in self._remapped_tags.keys():
                print('UNKNOWN TAG: %s (%s)' % (k, repr(v)))
                continue
            k = self._remapped_tags[k]

            k = safe_unicode(k.strip())
            if not k:
                continue
            try:
                k = k.split(' ')[1]
            except IndexError:
                pass

            try:
                v = safe_unicode(str(v).strip())
                if not v:
                    continue
            except TypeError:
                #print('CANNOT STRINGIFY VALUE: %s (%s)' % (k, repr(v)))
                continue

            if k in self._key_categories.keys():
                if self._key_categories[k] not in meta.keys():
                    meta[self._key_categories[k]] = {}
                category = self._key_categories[k]
            else:
                category = 'image'

            if k in self._string_fields:
                pass
            elif k in self._int_fields:
                try:
                    v = int(v)
                except ValueError, e:
                    print("ERROR int(v): %s -> %s" % (k, v))
                    print(e)
                    continue
            elif k in self._datetime_fields:
                if ': ' in v:
                    v = v.replace(': ', ':0')

                time_struct = None
                for fmt in self._time_formats:
                    try:
                        time_struct = time.strptime(v, fmt)
                    except ValueError, e:
                        pass

                if time_struct:
                    v = datetime.datetime.fromtimestamp(time.mktime(time_struct)).isoformat()
                else:
                    print('NO FMT: %s' % v)

            meta[category][k] = v

        for category in meta.keys():
            if len(meta[category]) == 0:
                del(meta[category])

        return meta

if __name__ == '__main__':
    dirs = ['/export']

    emp = ExifMetadataParser()
    for d in dirs:
        for (path, dirs, files) in os.walk(d):
            for f in files:
                r = emp.extract('%s/%s' % (path, f))
                if r:
                    pprint.pprint(r)
