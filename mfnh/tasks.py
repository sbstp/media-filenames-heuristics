from pathlib import Path
import json
import shutil

from sqlalchemy.orm import joinedload
import jinja2
import requests

from . import languages
from .db import File, Movie, Subtitle
from .providers import tmdb
from .movies import find_movies
from .util import printlnf, format_title_tuple, filter_filename

_FILE_TYPE_MOVIE = 1
_FILE_TYPE_SUBTITLE = 2


def _filter_out_known_files(root, sess, movies):
    known_files = {root / f.path: f for f in sess.query(File).all()}
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


def scan_root(root, sess):
    scanned_movies = list(find_movies(root))
    # generate_scan_report(root, scanned_movies)
    scanned_movies.sort(key=lambda m: m.title[0])

    for item in _filter_out_known_files(root, sess, scanned_movies):
        kind = item[0]
        if kind == _FILE_TYPE_MOVIE:
            _, scanned_movie = item
            printlnf("Found movie: {} -> ",
                     format_title_tuple(scanned_movie.title),
                     str(scanned_movie.path.relative_to(root)))

            db_movie = tmdb.search(scanned_movie)
            if not db_movie:
                if scanned_movie.parent:
                    printlnf('Could not find {} / {} on themoviedb.org'.format(
                        format_title_tuple(scanned_movie.title)), format_title_tuple(scanned_movie.parent_title))
                else:
                    printlnf('Could not find {} on themoviedb.org'.format(
                        format_title_tuple(scanned_movie.title)))
                continue

            _rename_with_info(root, scanned_movie, db_movie, sess)
            # TODO: warn on duplicate movie
            sess.add(db_movie)

        elif kind == _FILE_TYPE_SUBTITLE:
            _, scanned_movie, sub, db_movie_file = item
            # TODO: new subtitles

        sess.commit()


def clean_database(root, sess, duplicate=True):
    for movie in sess.query(Movie).all():
        path = root / movie.file.path
        if not path.exists():
            printlnf('Missing movie file: {}', movie.file.path)
            sess.delete(movie)
            printlnf('Removing movie: "{}" from database', movie.title)
        dupes = sess.query(Movie).filter_by(tmdb_id=movie.tmdb_id).all()
        if len(dupes) > 1:
            printlnf('Duplicate movie: "{}"\n', movie.title)
    sess.commit()


def _download_and_save_image(root, sess, path, image_path):
    url = 'https://image.tmdb.org/t/p/original/{}'.format(image_path)
    resp = requests.get(url)
    if resp.status_code == 200:
        path.write_bytes(resp.content)
        file = File(path=str(path.relative_to(root)), original_path=None)
        sess.add(file)
        return file
    return None


def download_images(root, sess):
    movies = sess.query(Movie).options(joinedload(Movie.poster)).options(joinedload(Movie.backdrop)).all()
    for m in movies:
        if not m.backdrop or not m.poster:
            printlnf('Downloading images for {} ({})', m.title, m.year)
            parent = (root / m.file.path).parent
            info = tmdb.lookup(m)

            backdrop = info['backdrop_path']
            poster = info['poster_path']

            if not m.backdrop and backdrop:
                file = _download_and_save_image(root, sess, parent / 'backdrop.jpg', backdrop)
                if file:
                    m.backdrop = file

            if not m.poster and poster:
                file = _download_and_save_image(root, sess, parent / 'poster.jpg', poster)
                if file:
                    m.poster = file

            sess.add(m)
            sess.commit()


def generate_static(root, sess, target):
    target = Path(target)
    movies = sess.query(Movie).options(joinedload(Movie.poster)).options(joinedload(Movie.backdrop)).all()

    image_dir = target / 'images'
    image_dir.mkdir(parents=True, exist_ok=True)

    def to_json(m):
        backdrop = poster = None

        if m.backdrop:
            backdrop = '{}_backdrop.jpg'.format(m.tmdb_id)
            target = image_dir / backdrop
            if not target.exists():
                shutil.copy(str(root / m.backdrop.path), str(target))

        if m.poster:
            poster = '{}_poster.jpg'.format(m.tmdb_id)
            target = image_dir / poster
            if not target.exists():
                shutil.copy(str(root / m.poster.path), str(target))

        return dict(
            tmdb_id=m.tmdb_id,
            title=m.title,
            original_title=m.original_title,
            overview=m.overview,
            year=m.year,
            backdrop=backdrop,
            poster=poster,
        )

    data = list(map(to_json, movies))

    shutil.copy('assets/style.css', str(target / 'style.css'))
    tpl = Path('assets/index.html').read_text()
    target = (target / 'index.html')
    target.write_text(tpl.replace('$$JSON_DATA$$', json.dumps(data)))
