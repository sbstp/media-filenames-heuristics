import json
import shutil
from pathlib import Path

from sqlalchemy.orm import joinedload

from ..db import Movie


def generate_static(sess, target):
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
                shutil.copy(str(m.backdrop.get_abspath()), str(target))

        if m.poster:
            poster = '{}_poster.jpg'.format(m.tmdb_id)
            target = image_dir / poster
            if not target.exists():
                shutil.copy(str(m.poster.get_abspath()), str(target))

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
