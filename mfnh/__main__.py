from pathlib import Path
import argparse

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='mfnh')
    parser.add_argument('dir')
    subparsers = parser.add_subparsers(dest='command')

    scan = subparsers.add_parser('scan', help="scan the directory for movies")
    cleandb = subparsers.add_parser('cleandb', help="clean the database")
    cleandir = subparsers.add_parser('cleandir', help="clean movies directory")
    images = subparsers.add_parser('images', help="download posters and backdrops for the movies in your library")
    static = subparsers.add_parser('static', help="generate static website with movie collection")
    static.add_argument('target_dir', help="target directory, will create if necessary")

    args = parser.parse_args()
    root = Path(args.dir)

    sess = Session()

    if args.command == 'scan':
        tasks.scan_root(root, sess)
    elif args.command == 'cleandb':
        tasks.clean_database(root, sess)
    elif args.command == 'cleandir':
        # clean_root(root, sess)
        pass
    elif args.command == 'images':
        tasks.download_images(root, sess)
    elif args.command == 'static':
        tasks.generate_static(root, sess, args.target_dir)
