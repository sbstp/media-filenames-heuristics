import sys
from .movies import extract_title_year
from .fs import find_movies

if __name__ == '__main__':
    for movie in find_movies(sys.argv[1]):
        print(extract_title_year(movie.name))

    # with open(sys.argv[1]) as f:
    #     for filename in f.read().splitlines():
    #         print(extract_title_year(filename))
