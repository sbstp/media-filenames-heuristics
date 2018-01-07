from .. import languages
from ..db import File, Movie, Subtitle
from ..util import filter_filename


def _subtitle_rename(movie_name, subpath, lang):
        if lang:
            return '{}.{}{}'.format(movie_name, languages.get_code(lang), subpath.suffix)
        else:
            return '{}{}'.format(movie_name, subpath.suffix)


def _rename_with_info(root, scanned_movie, db_movie, sess):
    # TODO detect duplicate movies
    name = '{} ({})'.format(filter_filename(db_movie.title), db_movie.year)

    db_movie.file = File(original_path=str(scanned_movie.path.relative_to(root)))

    new_parent = root / name
    new_path = new_parent / (name + scanned_movie.path.suffix)
    new_parent.mkdir(exist_ok=True)
    scanned_movie.path.rename(new_path)

    db_movie.file.path = str(new_path.relative_to(root))
    sess.add(db_movie.file)

    # TODO detect subs collision
    for (subpath, lang) in scanned_movie.subs:
        file = File(original_path=str(subpath.relative_to(root)))

        new_path = new_parent / _subtitle_rename(name, subpath, lang)
        subpath.rename(new_path)

        file.path = str(new_path.relative_to(root))

        sess.add(file)

        sub = Subtitle(
            lang=languages.get_code(lang),
            file=file,
        )

        sess.add(sub)

        db_movie.subtitles.append(sub)


def rename(sess):
    for db_movie in sess.query(Movie).all():
        pass
