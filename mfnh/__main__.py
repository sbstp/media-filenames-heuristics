from pathlib import Path

import click

from .cleanup import locate_garbage
from .db import Session, Movie
from . import tasks


def clean_root(root, sess):
    for item in locate_garbage(root, sess):
        if item.is_file():
            print('Unlinking', item)
            item.unlink()
        elif item.is_dir():
            item.rmdir()
            print('Removing directory', item)
    movies = sess.query(Movie).all()
    for m in movies:
        dupes = sess.query(Movie).filter_by(tmdb_id=m.tmdb_id).all()
        if len(dupes) > 1:
            print(m.title)


sess = Session()


@click.group('merovingian')
def app():
    pass


@app.command(help='add a root directory to the database')
@click.option('--content-type', type=click.Choice(['movies', 'tv']), required=True)
@click.argument('root')
def add(content_type, root):
    tasks.add_root(sess, Path(root), content_type)


@app.command(help='scan the root directories for new content')
def scan():
    tasks.scan(sess)


@app.command(help='rename movies cleanly')
def rename():
    tasks.rename(sess)


@app.command(help='clean the database from removed files')
def cleandb():
    tasks.clean_database(sess)


@app.command('clean-files', help='remove garbage files')
@click.option('--dry-run', default=False, is_flag=True, help="if true, do not remove files")
def clean_files(dry_run):
    tasks.clean_roots(sess, dry_run)


@app.command('fetch-images', help='download images for the content')
def fetch_images():
    tasks.download_images(sess)


@app.command(help='generate a static website using database')
@click.argument('target-dir')
def static(target_dir):
    tasks.generate_static(sess, target_dir)


if __name__ == '__main__':
    app(prog_name='merovingian')
