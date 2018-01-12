import re
from pathlib import Path


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs), end='')


def printlnf(fmt, *args, **kwargs):
    print(fmt.format(*args, **kwargs))


def format_title_tuple(title):
    if title[1]:
        return '{} ({})'.format(title[0], title[1])
    else:
        return '{}'.format(title[0])


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


def str_rel_path(path, rel_to):
    return str(path.relative_to(rel_to))


def as_path(obj):
    if isinstance(obj, Path):
        return obj
    elif isinstance(obj, str):
        return Path(obj)
    else:
        raise ValueError
