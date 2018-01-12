import re

from .. import fs
from ..util import as_path


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


def _find_tv(parent, root):
    for child in parent.children:
        pass


def find_tv(root):
    root = as_path(root)
    root_dir = fs.walk(root)
    return _find_tv(root_dir, root_dir)
