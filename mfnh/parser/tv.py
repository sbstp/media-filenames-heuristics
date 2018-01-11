import re


def compile(pattern):
    return re.compile(pattern, re.IGNORECASE)


a = compile(r's(\d\d)[\.\_]?e(\d\d)')
b = compile(r'(\d+)x(\d+)')
res = [a, b]


def _season_episode(s):
    for r in res:
        m = r.search(s)
        if m:
            return (int(m.group(1)), int(m.group(2)))
    return None
