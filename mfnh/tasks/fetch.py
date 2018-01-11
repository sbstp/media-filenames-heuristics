import requests

from sqlalchemy.orm import joinedload

from ..db import File, Movie
from ..providers import tmdb
from ..util import printlnf


def _download_and_save_image(sess, root, path, image_path):
    url = 'https://image.tmdb.org/t/p/original/{}'.format(image_path)
    resp = requests.get(url)
    if resp.status_code == 200:
        path.write_bytes(resp.content)
        file = File(path, root)
        sess.add(file)
        return file
    return None


def download_images(sess):
    movies = sess.query(Movie).options(joinedload(Movie.poster)
                                       ).options(joinedload(Movie.backdrop)).all()
    for m in movies:
        if not m.backdrop or not m.poster:
            root = m.file.root
            parent = m.file.get_abspath().parent
            backdrop_path = parent / 'backdrop.jpg'
            poster_path = parent / 'poster.jpg'

            if backdrop_path.exists():
                file = File(backdrop_path, root)
                sess.add(file)
                m.backdrop = file

            if poster_path.exists():
                file = File(poster_path, root)
                sess.add(file)
                m.poster = file

            if not m.backdrop or not m.poster:
                printlnf('Downloading images for {} ({})', m.title, m.year)

                info = tmdb.lookup(m)

                backdrop = info['backdrop_path']
                poster = info['poster_path']

                if not m.backdrop and backdrop:
                    file = _download_and_save_image(sess, m.file.root, backdrop_path, backdrop)
                    if file:
                        m.backdrop = file

                if not m.poster and poster:
                    file = _download_and_save_image(sess, m.file.root, poster_path, poster)
                    if file:
                        m.poster = file

            sess.add(m)
            sess.commit()
