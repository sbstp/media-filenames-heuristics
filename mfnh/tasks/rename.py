from pathlib import Path

from .. import languages
from ..db import Movie
from ..util import filter_filename, printlnf


def _format_subtitle(movie_name, subpath, lang):
    if lang:
        return '{}.{}{}'.format(movie_name, languages.get_code(lang), subpath.suffix)
    else:
        return '{}{}'.format(movie_name, subpath.suffix)


def _format_name(db_movie: Movie):
    return '{} ({})'.format(filter_filename(db_movie.title), db_movie.year)


def _move_file(root, file, new_path):
    current = file.get_abspath()
    current.rename(new_path)
    file.set_path(new_path, root)


def rename(sess):
    for db_movie in sess.query(Movie).all():
        name = _format_name(db_movie)
        new_path = Path(db_movie.file.root.path) / name / (name + db_movie.file.get_path().suffix)

        if db_movie.file.get_abspath() != new_path:
            printlnf("Renaming {} ({})", db_movie.title, db_movie.year)

            root = db_movie.file.root
            parent = new_path.parent
            parent.mkdir(exist_ok=True)
            # rename movie file
            _move_file(root, db_movie.file, new_path)

            # rename subtitles
            for sub in db_movie.subtitles:
                new_path = parent / _format_subtitle(name, sub.file.get_path(), sub.lang)
                _move_file(root, sub.file, new_path)
                sess.add(sub)

            if db_movie.backdrop:
                _move_file(root, db_movie.backdrop, parent / "backdrop.jpg")

            if db_movie.poster:
                _move_file(root, db_movie.poster, parent / "poster.jpg")

            sess.add(db_movie)
            sess.commit()
