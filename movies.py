import re

RE_SPLIT = re.compile(r"""
\(([^\)]+)\)| # (parens)
\[([^\]]+)\]| # [square]
([^\.\s\(\[]+) # Sep.ara.ted
""", re.VERBOSE)
RE_YEAR = re.compile(r'^(\d{4})$')

# TODO more filters
FILTER = set(('-',))

# TODO more metadata tokens
METADATA = set(('1080p', '720p', '480p', 'dvdrip', 'bluray', 'director', "director's",
                "directors", "cut", "extended", "french"))


def tokens(line):
    for m in RE_SPLIT.finditer(line):
        yield m.group(1) or m.group(2) or m.group(3)


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


def relevant(tokens):
    """
    Usually, the title is placed before the year. However, sometimes
    the title contains a year. If multiple candidates for the year are
    found, the right most one is chosen, since the year usually follows
    the title. In the case where nothing precedes the year found, such
    as the string '2011', it is assumed to be the movie's name.

    If metadata is found before the year, everything before the first
    piece of metadata will be used instead of the year.
    """
    tokens = [t for t in tokens if t not in FILTER]
    years = []
    metadata_idx = None

    # Collect candidates for years and first metadata position.
    for idx, token in enumerate(tokens):
        m = RE_YEAR.match(token)
        if m:
            years.append((idx, token))

        if not metadata_idx and token.lower() in METADATA:
            metadata_idx = idx
            break

    year = None
    year_idx = None
    if years:
        year_idx, year = years[-1]
        year = int(year)

    try:
        idx = min(year_idx, metadata_idx)
        title = tokens[:idx]
        if not title:
            title = [year]
    except ValueError:
        title = tokens[:]

    return ' '.join(title), year


if __name__ == '__main__':
    with open('dataset-movies.txt') as f:
        for line in f.read().splitlines():
            print(line)
            print(relevant(tokens(line)))
            print()
