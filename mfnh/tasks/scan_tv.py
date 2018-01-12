from ..parser.tv import find_tv
from ..db import Root
from ..util import as_path


def scan_root(sess, root: Root):
    root_path = as_path(root.path)
    find_tv(root_path)
