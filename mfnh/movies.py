from typing import Optional, Tuple
import re

from . import metadata_tokens
from .util import min

RE_SPLIT = re.compile(r"""
\(([^\)]+)\)| # (parens)
\[([^\]]+)\]| # [square]
([^\-\_\.\s\(\[]+) # Sep.ara.ted
""", re.VERBOSE)
RE_YEAR = re.compile(r'^(\d{4})$')


def _tokens(line):
    for m in RE_SPLIT.finditer(line):
        yield m.group(1) or m.group(2) or m.group(3)


def extract_title_year(filename: str) -> Tuple[str, Optional[int]]:
    """
    Usually, the title is placed before the year. However, sometimes
    the title contains a year. If multiple candidates for the year are
    found, the right most one is chosen, since the year usually follows
    the title. In the case where nothing precedes the year found, such
    as the string '2011', it is assumed to be the movie's name.

    If metadata is found before the year, everything before the first
    piece of metadata will be used instead of the year.
    """
    tokens = list(_tokens(filename))
    years = []
    metadata_idx = None

    # Collect candidates for years and first metadata position.
    for idx, token in enumerate(tokens):
        m = RE_YEAR.match(token)
        if m:
            years.append((idx, token))

        if not metadata_idx and token.lower() in metadata_tokens.ALL:
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
