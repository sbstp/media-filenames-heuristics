import time

from requests.exceptions import HTTPError
import tmdbsimple as tmdb

from ..db import Movie

# Borrowing kodi's API key
# ecbc86c92da237cb9faff6d3ddc4be6d
tmdb.API_KEY = 'ecbc86c92da237cb9faff6d3ddc4be6d'


def _query_retry(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except HTTPError as e:
        resp = e.response
        if resp.status_code != 429:
            raise
        time.sleep(10)
        return func(*args, **kwargs)


def configuration():
    conf = tmdb.Configuration()
    return _query_retry(conf.info)


def _search(title, year):
    search = tmdb.Search()
    _query_retry(search.movie, query=title, year=year)
    return search.results


def search(scanned_movie):
    results = _search(scanned_movie.title[0], scanned_movie.title[1])
    # No results from the filename itself, try the parent directory's name information
    if not results:
        results = _search(scanned_movie.parent_title[0], scanned_movie.parent_title[1])

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


def lookup(movie):
    id = None
    if isinstance(movie, Movie):
        id = movie.tmdb_id
    elif isinstance(movie, int):
        id = movie
    else:
        raise ValueError

    movie = tmdb.Movies(id)
    return _query_retry(movie.info)
