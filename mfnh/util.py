import re
import sys


def printf(fmt, *args, file=sys.stdout, flush=False):
    print(fmt.format(*args), end='', file=file, flush=flush)


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
_RE_FILENAME_FILTER = re.compile(r'[\<\>\:\"\/\\\|\?\*\0\%]')


def filter_filename(name):
    return _RE_FILENAME_FILTER.sub('_', name)
