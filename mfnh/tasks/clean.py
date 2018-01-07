from ..db import Movie
from ..util import printlnf


def clean_database(sess, duplicate=True):
    for movie in sess.query(Movie).all():
        if not movie.file.abspath.exists():
            printlnf('Removing movie {} because movie file is missing: {}', movie.title, movie.file.abspath)
            sess.delete(movie)
        else:
            for sub in movie.subtitles:
                if not sub.file.abspath.exists():
                    printlnf('Removing reference to subtitle {}', sub.file.abspath)
                    sess.delete(sub)
            if not movie.backdrop.abspath.exists():
                printlnf('Removing reference to image {}', movie.backdrop.abspath)
                sess.delete(movie.backdrop)
                movie.backdrop = None
                sess.add(movie)
            if not movie.poster.abspath.exists():
                printlnf('Removing reference to image {}', movie.poster.abspath)
                sess.delete(movie.poster)
                movie.poster = None
                sess.add(movie)

        sess.commit()
