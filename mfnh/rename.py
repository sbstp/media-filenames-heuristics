import time

import tmdbsimple as tmdb

from .db import File, Movie, Subtitle
from .languages import get_code
from .util import filter_filename


ITEM_TYPE_MOVIE = 1
ITEM_TYPE_SUBTITLE = 2


def filter_known_files(root, sess, movies):
    files = {root / f.path: f for f in sess.query(File).all()}
    for m in movies:
        # If the movie file is not known.
        if m.path not in files:
            yield (ITEM_TYPE_MOVIE, m)
            continue
        # Movie is known, look for new subtitles
        for sub in m.subs:
            subpath, _ = sub
            # Unknown subtitle file
            if subpath not in files:
                # Yield: movie scan result, subtitle pair, db.File object of movie
                yield (ITEM_TYPE_SUBTITLE, m, sub, files[m.path])


def _tmdb_lookup_results(title, year):
    search = tmdb.Search()
    try:
        search.movie(query=title, year=year)
    except:
        time.sleep(10)
        search.movie(query=title, year=year)
    return search.results


def tmdb_lookup(scanned_movie):
    results = _tmdb_lookup_results(scanned_movie.title[0], scanned_movie.title[1])
    # No results from the filename itself, try the parent
    if not results:
        results = _tmdb_lookup_results(scanned_movie.parent_title[0], scanned_movie.title[1])

    if not results:
        return None

    res = results[0]

    return Movie(
        title=res['title'],
        original_title=res['original_title'],
        year=int(res['release_date'][:4]),
        overview=res['overview'],
        tmdb_id=res['id'],
    )


def _subtitle_rename(movie_name, subpath, lang):
        if lang:
            return '{}.{}{}'.format(movie_name, get_code(lang), subpath.suffix)
        else:
            return '{}{}'.format(movie_name, subpath.suffix)


def rename_with_info(root, scanned_movie, db_movie, sess):
    name = '{} ({})'.format(filter_filename(db_movie.title), db_movie.year)

    db_movie.file = File(original_path=str(scanned_movie.path.relative_to(root)))

    new_parent = root / name
    new_path = new_parent / (name + scanned_movie.path.suffix)
    new_parent.mkdir(exist_ok=True)
    scanned_movie.path.rename(new_path)

    db_movie.file.path = str(new_path.relative_to(root))
    sess.add(db_movie.file)

    # TODO detect multiple subs
    for (subpath, lang) in scanned_movie.subs:
        file = File(original_path=str(subpath.relative_to(root)))

        new_path = new_parent / _subtitle_rename(name, subpath, lang)
        subpath.rename(new_path)

        file.path = str(new_path.relative_to(root))

        sess.add(file)

        sub = Subtitle(
            lang=get_code(lang),
            file=file,
        )

        sess.add(sub)

        db_movie.subtitles.append(sub)
