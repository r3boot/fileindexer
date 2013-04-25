"""
parser_utils.py -- Various utilities for parsing single elements
"""

import sys

__description__ = 'Various utilities used for parsing single elements'
__author__      = 'Lex van Roon <r3boot@r3blog.nl>'

MSGPREFIX = {
    'info':     '[*]',
    'warning':  '[W]',
    'error':    '[E]',
    'debug':    '[D]',
}

def info(message):
    """
    Generates an informal message

    * accepts:
    caller:     Function or class generating the message
    message:    Message to be displayed

    * returns:
    None
    """
    print('{0} {1}'.format(MSGPREFIX['info'], message))

def warning(message):
    """
    Generates a warning message

    * accepts:
    caller:     Function or class generating the message
    message:    Message to be displayed

    * returns:
    None
    """
    print('{0} {1}'.format(MSGPREFIX['warning'], message))

def error(message):
    """
    Generates an error message

    * accepts:
    caller:     Function or class generating the message
    message:    Message to be displayed

    * returns:
    None
    """
    print('{0} {1}'.format(MSGPREFIX['error'], message))

def debug(message):
    """
    Generates a debug message

    * accepts:
    caller:     Function or class generating the message
    message:    Message to be displayed

    * returns:
    None
    """
    print('{0} {1}'.format(MSGPREFIX['debug'], message))

def safe_unicode(string):
    """
    Convert a string to unicode

    * accepts:
    string: String to be converted to unicode

    * returns:
    Unicode encoded string if possible
    None if encoding failed
    """

    if isinstance(string, unicode):
        return string

    result = None
    if not isinstance(string, unicode) and not isinstance(string, str):
        try:
            string = str(string)
        except TypeError, errmsg:
            error('safe_unicode: string conversion failed: {0}'.format(errmsg))
            return None

    try:
        result = unicode(string, 'utf8')
    except TypeError, errmsg:
        error('safe_unicode: unicode conversion failed: {0}'.format(errmsg))
        return None
    except UnicodeDecodeError:
        error('safe_unicode: unicode conversion failed: {0}'.format(errmsg))
        return None
    except:
        error('safe_unicode: unicode conversion unknown error: {0}'.format(
            sys.exc_info()[0])
        )

    return result

def get_stream_metadata(stream_list, stream_id):
    """
    Get the metadata for a stream by stream_id

    * accepts:
    stream_list:    List of dictionaries containing stream metadata
    stream_id:      Stream ID being requested

    * returns:
    Dictionary containing the stream metadata or
    None if no stream is found
    """
    for stream in stream_list:
        if stream['stream_id'] == stream_id:
            return stream

def merge_av_meta_dict(parent, additional):
    """
    Merge two A/V metadata lists. We need to match on stream_id for
    proper merging

    * accepts:
    parent:     List containing parent streams
    additional: List containing additional streams

    * returns:
    List containing parent/additional merged
    """
    updated_streams = []

    debug(parent)
    debug(additional)
    parent_ids = [s['stream_id'] for s in parent]
    additional_ids = [s['stream_id'] for s in additional]

    ## First add all new dictionaries
    for stream_id in set(parent_ids) ^ set(additional_ids):
        stream_list = None
        if stream_id in parent_ids:
            stream_list = parent
        elif stream_id in additional_ids:
            stream_list = additional
        else:
            error('merge_meta_dict: Unknown stream_id')
            continue

        updated_streams.append(get_stream_metadata(
            stream_list, stream_id
        ))

    ## Then, merge the rest of the dictionaries
    for stream_id in set(parent_ids) & set(additional_ids):
        parent_meta = get_stream_metadata(parent, stream_id)
        additional_meta = get_stream_metadata(additional, stream_id)
        parent_meta.update(additional_meta)
        updated_streams.append(parent_meta)

    return updated_streams

def merge_meta_dict(parent, additional):
    """
    Update the parent meta dictionary with additional metadata

    * accepts:
    parent:     Master metadata dictionary
    additional: Additional metadata dictionary

    * returns:
    Merged metadata dictionary or
    Master metadata dictionary on error
    """

    debug('parent: {0}'.format(parent))
    debug('additional: {0}'.format(additional))

    for category, data in additional.items():
        if category in ['audio', 'video']:
            if category not in parent.keys():
                parent[category] = data
                continue

            parent[category] = merge_av_meta_dict(
                                   parent[category], additional[category]
                               )
        else:
            if not category in parent.keys():
                parent[category] = {}
            parent[category].update(data)

    return parent
