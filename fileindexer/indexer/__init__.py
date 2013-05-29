"""
Wrapper class for all available parsers
"""
import mimetypes

import pprint

from fileindexer.indexer.file_meta_parser import FileMetadataParser
from fileindexer.indexer.hachoir_meta_parser import HachoirMetadataParser, hachoir_mapper
from fileindexer.indexer.enzyme_meta_parser import EnzymeMetadataParser, enzyme_mimes
from fileindexer.indexer.mutagen_meta_parser import MutagenMetadataParser, mutagen_mimes
from fileindexer.indexer.exif_meta_parser import ExifMetadataParser, exif_mimes
from fileindexer.indexer.parser_utils import *

class MetadataParser():
    """
    This class wraps around all available parsers, and has functions
    to massage this data into a single dictionary suitable for ES usage
    """
    def __init__(self):
        """
        Initialize all available classes, and bind them to local variables
        * accepts: None
        * returns: None
        """
        self.__fmp = FileMetadataParser()
        self.__hmp = HachoirMetadataParser()
        self.__emp = EnzymeMetadataParser()
        self.__mmp = MutagenMetadataParser()
        self.__xmp = ExifMetadataParser()

    def _update(self, meta, xtra_meta):
        for key, value in xtra_meta.items():
            if key in ['audio', 'video']:
                meta[key] = merge_av_meta_dict(meta[key], xtra_meta[key])
            else:
                meta[key].update(xtra_meta[key])
        return meta

    def extract(self, meta, full_path):
        """
        Extract metadata from a file

        * accepts:
        meta:       Dictionary with already available metadata
        full_path:  Full path to the file from which to extract metadata

        * returns:
        Merged metadata dictionary or
        meta on error
        """
        types = None
        types = mimetypes.guess_type(full_path)
        if types and types[0] != None:
            meta['file']['mime'] = types[0]
        else:
            return meta


        xtra_meta = {}

        xtra_meta = self.__fmp.extract(full_path)
        if xtra_meta:
            meta = self._update(meta, xtra_meta)

        if meta['file']['mime'] in enzyme_mimes:
            print('emp')
            xtra_meta = self.__emp.extract(full_path)

        elif meta['file']['mime'] in mutagen_mimes:
            xtra_meta = self.__mmp.extract(full_path)

        elif meta['file']['mime'] in exif_mimes:
            xtra_meta = self.__xmp.extract(full_path)

        if not xtra_meta and meta['file']['mime'] in hachoir_mapper.keys():
            print('hmp')
            xtra_meta = self.__hmp.extract(
                full_path, 0.5, hachoir_mapper[meta['file']['mime']]
            )

        if xtra_meta:
            meta = self._update(meta, xtra_meta)

        return meta
