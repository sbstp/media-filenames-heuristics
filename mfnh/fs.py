from .util import as_path
from .parser import tokenize


_SUBTITLE_SUFFIXES = set(('.srt', '.sub', '.idx', '.usf', '.smi'))
_VIDEO_SUFFIXES = set(('.mkv', '.mp4', '.m4v', '.avi', '.webm', '.flv', '.vob', '.mov', '.wmv', '.ogg', '.ogv'))


def _walk(root, parent=None):
    if root.is_file():
        return File(root)
    elif root.is_dir():
        dir = Directory(root)
        for item in root.iterdir():
            dir._add_child(walk(item))
        return dir
    else:
        raise ValueError


def walk(root):
    root = as_path(root)
    return _walk(root)


class File:

    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent

    def _set_parent(self, parent):
        self._parent = parent

    # Little hack to sort of inherit from Path
    def __getattr__(self, name):
        return getattr(self.path, name)

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self is other or self.path == other

    @property
    def path(self):
        return self._path

    @property
    def abspath(self):
        return self._path.absolute()

    @property
    def parent(self):
        return self._parent

    def is_file(self):
        return True

    def is_dir(self):
        return False

    def is_root(self):
        return self.parent is None

    def siblings(self):
        if self.parent:
            return (child for child in self.parent.children if child != self)

    def is_subtitle(self):
        return self.is_file() and self.suffix.lower() in _SUBTITLE_SUFFIXES

    def is_video(self, min_size=1024*1024*10):
        return self.is_file() and self.suffix.lower() in _VIDEO_SUFFIXES and self.stat().st_size >= min_size

    def tokenize(self):
        s = self.name if self.is_dir() else self.stem
        return tokenize(s)

    def remove(self, unlink=False):
        if unlink:
            self.abspath.unlink()
        self.parent._remove_child(self)


class Directory(File):

    def __init__(self, path, parent=None):
        super().__init__(path, parent)
        self._children = []

    def _add_child(self, child):
        child._set_parent(self)
        self._children.append(child)

    def _remove_child(self, child):
        child._set_parent(None)
        self._children.remove(child)

    def is_file(self):
        return False

    def is_dir(self):
        return True

    def empty(self):
        return len(self._children) == 0

    @property
    def children(self):
        return iter(self._children)

    def children_rec(self):
        for child in self.children:
            if child.is_dir():
                yield from child.children_rec()
            yield child

    def remove(self, unlink=False):
        if unlink:
            self.abspath.rmdir()
        self.parent._remove_child(self)
