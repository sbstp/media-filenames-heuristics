from .db import File, Movie
from .util import printf


def _walk_files(parent):
    for item in parent.iterdir():
        if item.is_file():
            yield item
        elif item.is_dir():
            yield from _walk_files(item)


def _walk_dirs(parent):
    for item in parent.iterdir():
        if item.is_dir():
            yield from _walk_dirs(item)
            yield item


def locate_garbage(root, sess):
    good_files = set(root / f.path for f in sess.query(File).all())
    files = list(_walk_files(root))
    bad_files = set(item for item in files if item not in good_files)
    yield from iter(bad_files)
    for item in root.iterdir():
        if item.is_dir():
            if len([file for file in _walk_files(item) if file not in bad_files]) == 0:
                yield from _walk_dirs(item)
                yield item
