import mimetypes

from .util import as_path
from .parser import tokenize


_SUBTITLE_SUFFIXES = set(('.srt', '.sub', '.idx', '.usf', '.smi'))


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

    def siblings(self):
        if self.parent:
            return (child for child in self.parent.children if child != self)

    def is_subtitle(self):
        return self.is_file() and self.suffix.lower() in _SUBTITLE_SUFFIXES

    def is_video(self):
        if self.is_file():
            kind, _ = mimetypes.guess_type(self.abspath.as_uri(), strict=False)
            if kind and kind.startswith("video/"):
                return True
        return False

    def tokenize(self):
        s = self.name if self.is_dir() else self.stem
        return tokenize(s)


class Directory(File):

    def __init__(self, path, parent=None):
        super().__init__(path, parent)
        self._children = []

    def _add_child(self, child):
        child._set_parent(self)
        self._children.append(child)

    def is_file(self):
        return False

    def is_dir(self):
        return True

    @property
    def children(self):
        return iter(self._children)

    def children_rec(self):
        for child in self.children:
            yield child
            if child.is_dir():
                yield from child.children_rec()
