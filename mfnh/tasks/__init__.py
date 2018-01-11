from ..db import ContentType, Root
from ..util import printlnf

from .clean import clean_database, clean_roots
from .fetch import download_images
from .rename import rename
from .scan import scan
from .static import generate_static


def add_root(sess, root, content_type):
    resolved = root.resolve()
    if resolved.exists() and resolved.is_dir():
        sess.add(Root(path=str(resolved), content_type=ContentType.from_str(content_type)))
        sess.commit()
        printlnf("Root added {} succesfully", str(resolved))
    else:
        printlnf("The given root is not valid: {}", str(root))


__all__ = ['add_root', 'clean_database', 'clean_roots', 'download_images', 'rename', 'generate_static', 'scan']
