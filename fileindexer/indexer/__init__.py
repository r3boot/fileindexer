
import mimetypes

from fileindexer.indexer.file_meta_parser import FileMetadataParser
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.enzyme_meta_parser import EnzymeMetadataParser, enzyme_mimes
from fileindexer.indexer.mutagen_meta_parser import MutagenMetadataParser, mutagen_mimes
from fileindexer.indexer.exif_meta_parser import ExifMetadataParser, exif_mimes

class MetadataParser():
    def __init__(self):
        self.__fmp = FileMetadataParser()
        self.__hmp = HachoirMetadataParser()
        self.__emp = EnzymeMetadataParser()
        self.__mmp = MutagenMetadataParser()
        self.__xmp = ExifMetadataParser()

    def extract(self, full_path):
        meta = {
            'file': {}
        }
        types = None
        types = mimetypes.guess_type(full_path)
        if types and types[0] != None:
            meta['file']['mime'] = types[0]
        else:
            return {}

        xtra_meta = {}

        xtra_meta = self.__fmp.extract({'full_path': full_path})
        if xtra_meta:
            meta.update(xtra_meta)

        if meta['mime'] in enzyme_mimes:
            xtra_meta = self.__emp.extract({'full_path': full_path})

        elif meta['mime'] in mutagen_mimes:
            xtra_meta = self.__mmp.extract({'full_path': full_path})

        elif meta['mime'] in exif_mimes:
            xtra_meta = self.__xmp.extract({'full_path': full_path})

        if not xtra_meta and meta['mime'] in hachoir_mapper.keys():
            xtra_meta = self.__hmp.extract(full_path, 0.5,  hachoir_mapper[meta['mime']])

        if xtra_meta:
            meta.update(xtra_meta)

        return meta
