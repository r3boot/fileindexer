
def safe_unicode(s):
    result = None
    if not isinstance(s, unicode) and not isinstance(s, str):
        try:
            s = str(s)
        except:
            return None

    try:
        result = unicode(s, 'utf8')
    except TypeError, e:
        if str(e) != 'decoding Unicode is not supported':
            print('safe_unicode: %s (%s)' % (e, s))
        else:
            result = s
    except UnicodeDecodeError:
        print('Cannot encode %s to unicode' % s)

    return result
