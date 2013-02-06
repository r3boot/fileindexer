
import mimetypes

from fileindexer.indexer.file_meta_parser import FileMetadataParser
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.enzyme_meta_parser import EnzymeMetadataParser, enzyme_mimes
from fileindexer.indexer.mutagen_meta_parser import MutagenMetadataParser, mutagen_mimes
from fileindexer.indexer.exif_meta_parser import ExifMetadataParser, exif_mimes

class MetadataParser():
    def __init__(self):
        self.__fmp = FileMetadataParser()
        self.__hmp = HachoirMetadataParser(None)
        self.__emp = EnzymeMetadataParser()
        self.__mmp = MutagenMetadataParser()
        self.__xmp = ExifMetadataParser()

    def extract(self, full_path):
        meta = {}
        types = None
        types = mimetypes.guess_type(full_path)
        if types and types[0] != None:
            meta['mime'] = types[0]
        else:
            return {}

        if meta['mime'] in enzyme_mimes:
            emp_meta = None
            emp_meta = self.__emp.extract({'full_path': full_path})
            if emp_meta:
                meta.update(emp_meta)
            else:
                hmp_meta = None
                hmp_meta = self.__hmp.extract({'full_path': full_path}, 0.5,  hachoir_mapper[meta['mime']])
                if hmp_meta:
                    meta.update(hmp_meta)

        elif meta['mime'] in mutagen_mimes:
            mmp_meta = None
            mmp_meta = self.__mmp.extract({'full_path': full_path})
            if mmp_meta:
                meta.update(mmp_meta)
            else:
                hmp_meta = None
                hmp_meta = self.__hmp.extract({'full_path': full_path}, 0.5,  hachoir_mapper[meta['mime']])
                if hmp_meta:
                    meta.update(hmp_meta)

        elif meta['mime'] in exif_mimes:
            xmp_meta = None
            xmp_meta = self.__xmp.extract({'full_path': full_path})
            if mmp_meta:
                meta.update(xmp_meta)
            else:
                hmp_meta = None
                hmp_meta = self.__hmp.extract({'full_path': full_path}, 0.5,  hachoir_mapper[meta['mime']])
                if hmp_meta:
                    meta.update(hmp_meta)
