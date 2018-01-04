import re


def min(a, b):
    """
    Min that allows None values.
    """
    if a is None and b is None:
        raise ValueError
    elif a is None:
        return b
    elif b is None:
        return a
    elif a < b:
        return a
    else:
        return b


_SUFFIX = ('bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')


def humanize_size(size):
    base = 1
    for suffix in _SUFFIX:
        if size < base * 1024:
            return '{:0.2f} {}'.format(size / base, suffix)
        base *= 1024


# Invalid characters in filenames
_RE_FILE_FILTER = re.compile(r'\<\>\:\"\/\\\|\?\*\0\%')


def filter_name(name):
    return _RE_FILE_FILTER.sub('', name)
