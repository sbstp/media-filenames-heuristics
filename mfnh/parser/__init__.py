import re

_RE_SPLIT = re.compile(r"""
\(([^\)]+)\)| # (parens)
\[([^\]]+)\]| # [square]
([^\-\_\.\s\(\[]+) # Sep.ara.ted
""", re.VERBOSE)


def tokenize(s):
    for m in _RE_SPLIT.finditer(s):
        token = m.group(1) or m.group(2) or m.group(3)
        if token:
            yield token
