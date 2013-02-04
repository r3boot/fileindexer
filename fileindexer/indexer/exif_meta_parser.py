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
        'EXIF GainControl',
        'EXIF InteroperabilityOffset',
        'EXIF MakerNote',
        'EXIF SubSecTimeDigitized',
        'EXIF SubSecTimeOriginal',
        'EXIF Tag 0x',
        'Filename',
        'Image ExifOffset',
        'Image ResolutionUnit',
        'Image XResolution',
        'Image YResolution',
        'JPEGThumbnail',
        'TIFFThumbnail',
        'Thumbnail',
    ]

    _remapped_tags = {
        'EXIF ApertureValue': 'img.raw.apeture',
        'EXIF BrightnessValue': 'img.raw.brightness',
        'EXIF ColorSpace': 'img.raw.colorspace',
        'EXIF Contrast': 'img.raw.contrast',
        'EXIF ComponentsConfiguration': 'img.raw.components_config',
        'EXIF DateTimeDigitized': 'img.raw.date.digitized',
        'EXIF DateTimeOriginal': 'img.raw.date',
        'EXIF DigitalZoomRatio': 'img.raw.zoom_ratio',
        'EXIF ExifVersion': 'img.raw.exif_version',
        'EXIF ExposureBiasValue': 'img.raw.exposure.bias',
        'EXIF ExposureMode': 'img.raw.exposure.mode',
        'EXIF ExposureProgram': 'img.raw.exposure.program',
        'EXIF ExposureTime': 'img.raw.exposure.time',
        'EXIF FileSource': 'img.raw.file_source',
        'EXIF Flash': 'img.raw.flash',
        'EXIF FlashPixVersion': 'img.raw.flashpix_version',
        'EXIF FNumber': 'img.raw.fnumber',
        'EXIF FocalLength': 'img.raw.focal.length',
        'EXIF FocalLengthIn35mmFilm': 'img.raw.focal.length.35mm',
        'EXIF ExifImageLength': 'img.raw.height',
        'EXIF ExifImageWidth': 'img.raw.width',
        'EXIF ISOSpeedRatings': 'img.raw.iso_speed_rating',
        'EXIF LightSource': 'img.raw.light_source',
        'EXIF MaxApertureValue': 'img.raw.apeture.max',
        'EXIF MeteringMode': 'img.raw.metering_mode',
        'EXIF Saturation': 'img.raw.saturation',
        'EXIF SceneCaptureType': 'img.raw.scene.capture_type',
        'EXIF SceneType': 'img.raw.scene.type',
        'EXIF SensingMethod': 'img.raw.sensing_mode',
        'EXIF Sharpness': 'img.raw.sharpness',
        'EXIF ShutterSpeedValue': 'img.raw.shutter.speed',
        'EXIF SubjectDistance': 'img.raw.subject.distance',
        'EXIF SubjectDistanceRange': 'img.raw.subject.distance.range',
        'EXIF WhiteBalance': 'img.raw.whitebalance',
        'Image DateTime': 'img.date',
        'Image Make': 'img.raw.device_vendor',
        'Image Model': 'img.raw.device_model',
        'Image Orientation': 'img.orientation',
        'Image YCbCrPositioning': 'img.positioning',
        'Image Software': 'img.software',
    }

    _string_fields = [
        'img.raw.apeture',
        'img.raw.contrast',
        'img.raw.device_model',
        'img.raw.device_vendor',
        'img.raw.exposure.mode',
        'img.raw.exposure.program',
        'img.raw.exposure.time',
        'img.raw.file_source',
        'img.raw.fnumber',
        'img.raw.light_source',
        'img.raw.metering_mode',
        'img.raw.saturation',
        'img.raw.scene.capture_type',
        'img.raw.scene.type',
        'img.raw.sensing_mode',
        'img.raw.sharpness',
        'img.raw.shutter.speed',
        'img.raw.subject.distance',
        'img.raw.whitebalance',
        'img.software',
    ]

    _int_fields = [
        'img.raw.apeture.max',
        'img.raw.exif_version',
        'img.raw.exposure.bias',
        'img.raw.focal.length',
        'img.raw.focal.length.35mm',
        'img.raw.iso_speed_rating',
        'img.raw.subject.distance.range',
        'img.raw.zoom_ratio',
    ]

    _bool_fields = [
        'img.raw.flash',
    ]

    _datetime_fields = [
        'img.date',
        'img.raw.date',
        'img.raw.date.digitized',
    ]

    def extract(self, meta):
        meta = {}
        filename = meta['full_path']
        try:
            fd = open(filename, 'rb')
        except IOError, e:
            print(e)
            print('Failed to open %s' % filename)
            return

        raw_meta = EXIF.process_file(fd, details=True, strict=False, debug=False)

        for k,v in raw_meta.items():
            ignore_tag = False
            for i in self._ignored_tags:
                if k.startswith(i):
                    ignore_tag = True
                    break
            if ignore_tag:
                continue

            if not k in self._remapped_tags.keys():
                print('UNKNOWN TAG: %s (%s)' % (k, v))
                continue
            k = self._remapped_tags[k]

            v = str(v)
            if k in self._string_fields:
                pass
            elif k in self._int_fields:
                v = int(v)
            elif k in self._datetime_fields:
                time_struct = time.strptime(v, '%Y:%m:%d %H:%M:%S')
                if time_struct:
                    v = datetime.datetime.fromtimestamp(time.mktime(time_struct)).isoformat()
            meta[k] = v
        return meta
