from ..db import Movie
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
            if not movie.backdrop.get_abspath().exists():
                printlnf('Removing reference to image {}', movie.backdrop.get_abspath())
                sess.delete(movie.backdrop)
                movie.backdrop = None
                sess.add(movie)
            if not movie.poster.get_abspath().exists():
                printlnf('Removing reference to image {}', movie.poster.get_abspath())
                sess.delete(movie.poster)
                movie.poster = None
                sess.add(movie)

        sess.commit()
