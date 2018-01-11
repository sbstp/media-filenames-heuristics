from pathlib import Path

from .. import languages
from ..db import File, Subtitle, Root
from ..parser.movies import find_movies
from ..providers import tmdb
from ..util import format_title_tuple, printlnf, str_rel_path


_FILE_TYPE_MOVIE = 1
_FILE_TYPE_SUBTITLE = 2


def _filter_out_known_files(sess, root: Root, movies):
    root_path = Path(root.path)
    known_files = {root_path / f.path: f for f in sess.query(File).filter(File.root == root).all()}
    for m in movies:
        # If the movie file is not known.
        if m.path not in known_files:
            yield (_FILE_TYPE_MOVIE, m)
            continue
        # Movie is known, look for new subtitles
        for sub in m.subs:
            subpath, _ = sub
            # Unknown subtitle file
            if subpath not in known_files:
                # Yield: movie scan result, subtitle pair, db.File object of movie
                yield (_FILE_TYPE_SUBTITLE, m, sub, known_files[m.path])


def scan_root(sess, root: Root):
    root_path = Path(root.path)
    scanned_movies = list(find_movies(root_path))
    scanned_movies.sort(key=lambda m: m.title[0])

    for item in _filter_out_known_files(sess, root, scanned_movies):
        kind = item[0]
        if kind == _FILE_TYPE_MOVIE:
            _, scanned_movie = item
            printlnf("Found movie: {} -> {}",
                     format_title_tuple(scanned_movie.title),
                     str_rel_path(scanned_movie.path, root_path))

            db_movie = tmdb.search(scanned_movie)
            if not db_movie:
                if scanned_movie.parent:
                    printlnf('Could not find {} / {} on themoviedb.org'.format(
                        format_title_tuple(scanned_movie.title)), format_title_tuple(scanned_movie.parent_title))
                else:
                    printlnf('Could not find {} on themoviedb.org'.format(
                        format_title_tuple(scanned_movie.title)))
                continue

            movie_file = File(scanned_movie.path, root)
            db_movie.file = movie_file

            if scanned_movie.backdrop:
                img_file = File(scanned_movie.backdrop, root)
                db_movie.backdrop = img_file
                sess.add(img_file)

            if scanned_movie.poster:
                img_file = File(scanned_movie.poster, root)
                db_movie.poster = img_file
                sess.add(img_file)

            for (sub_path, lang) in scanned_movie.subs:
                sub_file = File(sub_path, root)
                sub = Subtitle(file=sub_file, lang=languages.get_code(lang))

                db_movie.subtitles.append(sub)

                sess.add(sub_file)
                sess.add(sub)

            # TODO: warn on duplicate movie
            sess.add(movie_file)
            sess.add(db_movie)

        elif kind == _FILE_TYPE_SUBTITLE:
            _, scanned_movie, sub, db_movie_file = item
            # TODO: new subtitles

        sess.commit()
