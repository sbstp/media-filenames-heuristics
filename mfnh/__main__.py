from pathlib import Path
import argparse
import sys

import tmdbsimple as tmdb

from .cleanup import clean_database, locate_garbage
from .db import Session, Movie
from .generate import generate_scan_report
from .movies import find_movies
from .rename import ITEM_TYPE_MOVIE, ITEM_TYPE_SUBTITLE, filter_known_files, tmdb_lookup, rename_with_info

# Borrowing kodi's API key
# ecbc86c92da237cb9faff6d3ddc4be6d
tmdb.API_KEY = 'ecbc86c92da237cb9faff6d3ddc4be6d'


def scan_root(root, sess):
    scanned_movies = list(find_movies(root))
    generate_scan_report(root, scanned_movies)
    scanned_movies.sort(key=lambda m: m.title[0])

    for item in filter_known_files(root, sess, scanned_movies):
        kind = item[0]
        if kind == ITEM_TYPE_MOVIE:
            _, scanned_movie = item
            print("New movie", scanned_movie.title)
            db_movie = tmdb_lookup(scanned_movie)
            if not db_movie:
                print('Did not find {} on themoviedb.org'.format(scanned_movie.title))
                continue

            rename_with_info(root, scanned_movie, db_movie, sess)
            # TODO: warn on duplicate movie
            sess.add(db_movie)

        elif kind == ITEM_TYPE_SUBTITLE:
            _, scanned_movie, sub, db_movie_file = item
            print('New subtitle')

        sess.commit()


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
    subparsers = parser.add_subparsers(dest='command')

    scan = subparsers.add_parser('scan', help="scan the directory for movies")
    scan.add_argument('dir')
    cleandb = subparsers.add_parser('cleandb', help="clean the database")
    cleandb.add_argument('dir')
    cleandir = subparsers.add_parser('cleandir', help="clean movies directory")
    cleandir.add_argument('dir')

    args = parser.parse_args()
    root = Path(args.dir)

    print(root)

    sess = Session()

    if args.command == 'scan':
        scan_root(root, sess)
    elif args.command == 'cleandb':
        clean_database(root, sess)
    elif args.coomand == 'cleandir':
        clean_root(root, sess)
