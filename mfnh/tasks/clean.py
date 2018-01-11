from ..db import File, Movie, Root
from .. import fs
from ..util import printlnf


def clean_database(sess, duplicate=True):
    for movie in sess.query(Movie).all():
        if not movie.file.get_abspath().exists():
            printlnf('Removing movie {} because movie file is missing: {}',
                     movie.title, movie.file.get_abspath())
            sess.delete(movie)
        else:
            for sub in movie.subtitles:
                if not sub.file.get_abspath().exists():
                    printlnf('Removing reference to subtitle {}', sub.file.get_abspath())
                    sess.delete(sub)
            if movie.backdrop and not movie.backdrop.get_abspath().exists():
                printlnf('Removing reference to image {}', movie.backdrop.get_abspath())
                sess.delete(movie.backdrop)
                movie.backdrop = None
                sess.add(movie)
            if movie.poster and not movie.poster.get_abspath().exists():
                printlnf('Removing reference to image {}', movie.poster.get_abspath())
                sess.delete(movie.poster)
                movie.poster = None
                sess.add(movie)

        sess.commit()


def clean_roots(sess, dry_run):
    for root in sess.query(Root).all():
        root_path = root.get_path()
        known_files = set(f.get_abspath() for f in sess.query(File).filter(File.root == root).all())
        children = list(fs.walk(root_path).children_rec())
        for file in children:
            if file.is_file() and file.abspath not in known_files:
                printlnf("Removing file {}", file.abspath)
                file.remove(unlink=not dry_run)
        for file in children:
            if file.is_dir() and file.empty():
                printlnf("Removing directory {}", file.abspath)
                file.remove(unlink=not dry_run)
