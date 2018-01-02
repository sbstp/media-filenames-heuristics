from pathlib import Path
import mimetypes


def _is_video_file(file):
    kind, _ = mimetypes.guess_type(file.absolute().as_uri(), strict=False)
    return kind and kind.startswith("video/")


def find_movies(src):
    movies = []
    src_dir = Path(src)
    for item in src_dir.iterdir():
        if item.is_file() and _is_video_file(item):
            movies.append(item)
        if item.is_dir():
            subitems = [subitem for subitem in item.iterdir() if subitem.is_file() and _is_video_file(subitem)]
            subitems.sort(key=lambda f: f.stat().st_size)
            if subitems:
                largest_file = subitems[-1]
                movies.append(largest_file)
            else:
                print("no subfile?", item)
    return movies
