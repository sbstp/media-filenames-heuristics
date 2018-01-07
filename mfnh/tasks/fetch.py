import requests

from sqlalchemy.orm import joinedload

from ..db import File, Movie
from ..providers import tmdb
from ..util import printlnf, str_rel_path


def _download_and_save_image(sess, root, path, image_path):
    url = 'https://image.tmdb.org/t/p/original/{}'.format(image_path)
    resp = requests.get(url)
    if resp.status_code == 200:
        path.write_bytes(resp.content)
        file = File(path=str_rel_path(path, root.path), root=root)
        sess.add(file)
        return file
    return None


def download_images(sess):
    movies = sess.query(Movie).options(joinedload(Movie.poster)).options(joinedload(Movie.backdrop)).all()
    for m in movies:
        if not m.backdrop or not m.poster:
            printlnf('Downloading images for {} ({})', m.title, m.year)
            parent = m.file.abspath.parent
            info = tmdb.lookup(m)

            backdrop = info['backdrop_path']
            poster = info['poster_path']

            if not m.backdrop and backdrop:
                file = _download_and_save_image(sess, m.file.root, parent / 'backdrop.jpg', backdrop)
                if file:
                    m.backdrop = file

            if not m.poster and poster:
                file = _download_and_save_image(sess, m.file.root, parent / 'poster.jpg', poster)
                if file:
                    m.poster = file

            sess.add(m)
            sess.commit()
