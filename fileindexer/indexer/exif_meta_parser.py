import datetime
import time

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
    ]

    _remapped_tags = {
        'EXIF ApertureValue': 'img.apeture',
        'EXIF BrightnessValue': 'img.brightness',
        'EXIF ColorSpace': 'img.colorspace',
        'EXIF Contrast': 'img.contrast',
        'EXIF ComponentsConfiguration': 'img.components_config',
        'EXIF DateTimeDigitized': 'img.date.digitized',
        'EXIF DateTimeOriginal': 'img.date.original',
        'EXIF DigitalZoomRatio': 'img.zoom_ratio',
        'EXIF ExifVersion': 'img.exif_version',
        'EXIF ExposureBiasValue': 'img.exposure.bias',
        'EXIF ExposureMode': 'img.exposure.mode',
        'EXIF ExposureProgram': 'img.exposure.program',
        'EXIF ExposureTime': 'img.exposure.time',
        'EXIF FileSource': 'img.file_source',
        'EXIF Flash': 'img.flash',
        'EXIF FlashPixVersion': 'img.flashpix_version',
        'EXIF FNumber': 'img.fnumber',
        'EXIF FocalLength': 'img.focal.length',
        'EXIF FocalLengthIn35mmFilm': 'img.focal.length.35mm',
        'EXIF ExifImageLength': 'img.height',
        'EXIF ExifImageWidth': 'img.width',
        'EXIF ISOSpeedRatings': 'img.iso_speed_rating',
        'EXIF LightSource': 'img.light_source',
        'EXIF MaxApertureValue': 'img.apeture.max',
        'EXIF MeteringMode': 'img.metering_mode',
        'EXIF Saturation': 'img.saturation',
        'EXIF SceneCaptureType': 'img.scene.capture_type',
        'EXIF SceneType': 'img.scene.type',
        'EXIF SensingMethod': 'img.sensing_mode',
        'EXIF Sharpness': 'img.sharpness',
        'EXIF ShutterSpeedValue': 'img.shutter.speed',
        'EXIF SubjectDistance': 'img.subject.distance',
        'EXIF SubjectDistanceRange': 'img.subject.distance.range',
        'EXIF UserComment': 'comment',
        'EXIF WhiteBalance': 'img.whitebalance',
        'Image DateTime': 'img.date',
        'Image ImageDescription': 'description',
        'Image Make': 'img.device_vendor',
        'Image Model': 'img.device_model',
        'Image Orientation': 'img.orientation',
        'Image YCbCrPositioning': 'img.positioning',
        'Image Software': 'img.software',
    }

    _string_fields = [
        'comment',
        'description',
        'img.apeture',
        'img.apeture.max',
        'img.contrast',
        'img.device_model',
        'img.device_vendor',
        'img.exposure.mode',
        'img.exposure.program',
        'img.exposure.time',
        'img.file_source',
        'img.fnumber',
        'img.focal.length',
        'img.light_source',
        'img.metering_mode',
        'img.saturation',
        'img.scene.capture_type',
        'img.scene.type',
        'img.sensing_mode',
        'img.sharpness',
        'img.shutter.speed',
        'img.subject.distance',
        'img.whitebalance',
        'img.software',
    ]

    _int_fields = [
        'img.exif_version',
        'img.exposure.bias',
        'img.focal.length.35mm',
        'img.iso_speed_rating',
        'img.subject.distance.range',
        'img.zoom_ratio',
    ]

    _bool_fields = [
        'img.flash',
    ]

    _datetime_fields = [
        'img.date',
        'img.date.digitized',
    ]

    _time_formats = [
        '%Y:%m:%d %H:%M:%S',
        '%d %b %Y %H:%M:%S'
    ]

    def extract(self, raw_meta):
        meta = {}
        filename = raw_meta['full_path']
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
            return {}

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

            try:
                v = str(v)
            except TypeError:
                print('CANNOT STRINGIFY VALUE: %s (%s)' % (k, repr(v)))
                continue

            if len(v) == 0:
                print('EMPTY VALUE FOR %s' % (k))
                continue

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
            meta[k] = v
        return meta
