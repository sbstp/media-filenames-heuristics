import re

from .. import languages, metadata_tokens, fs
from ..util import min, as_path

_RE_YEAR = re.compile(r'^(\d{4})$')

# 200 MB is a good size to separate movie files from other video files like samples
# MIN_MOVIE_SIZE = 200 * 1024 * 1024


def _extract_title_year(file):
    # type: (Path,) -> Tuple[str, Optional[int]]
    """
    Usually, the title is placed before the year. However, sometimes
    the title contains a year. If multiple candidates for the year are
    found, the right most one is chosen, since the year usually follows
    the title. In the case where nothing precedes the year found, such
    as the string '2011', it is assumed to be the movie's name.

    If metadata is found before the year, everything before the first
    piece of metadata will be used instead of the year.
    """
    tokens = list(file.tokenize())
    years = []
    metadata_idx = None

    # Collect candidates for years and first metadata position.
    for idx, token in enumerate(tokens):
        m = _RE_YEAR.match(token)
        if m:
            years.append((idx, token))

        if not metadata_idx and token.lower() in metadata_tokens.ALL:
            metadata_idx = idx

    year = None
    year_idx = None
    if years:
        year_idx, year = years[-1]
        year = int(year)

    try:
        idx = min(year_idx, metadata_idx)
        title = tokens[:idx]
        if not title and year:
            title = [str(year)]
            year = None
    except ValueError:
        title = tokens[:]

    if not title:
        raise ValueError("could not find any piece of valuable information")

    return ' '.join(title), year


class MovieResult:

    def __init__(self, *, path, parent, subs, backdrop=None, poster=None):
        self.path = path  # type: Path
        self.title = _extract_title_year(path)  # type: Tuple[str, Optional[int]]
        self.parent = parent  # type: Optional[Path]
        self.parent_title = None  # type: Optional[Tuple[str, Optional[Int]]]
        if parent:
            self.parent_title = _extract_title_year(parent)
        self.size = path.stat().st_size  # type: int
        self.subs = subs
        self.backdrop = backdrop
        self.poster = poster


def _scan_for_subs(parent, file):
    for child in parent.children:
        # Scan for files named like the movie file but with a subtitle extension
        if child.is_subtitle() and child.name.startswith(file.stem):
            yield child
        # Scan for folders named subs/ or subtitles/ and take any subtitle file inside
        elif child.is_dir() and child.name.lower() in ('subs', 'subtitles'):
            for subchild in child.iterdir():
                if subchild.is_subtitle():
                    yield subchild


def _sub_id_language(subfile):
    for token in reversed(list(subfile.tokenize())):
        if token.lower() in metadata_tokens.ALL_WITHOUT_LANGUAGES:
            break
        try:
            lang = languages.lookup(token)
            return lang
        except:
            pass
    return None


def _scan_for_images(movie_file):
    backdrop = None
    poster = None
    for sibling in movie_file.siblings():
        if sibling.name.lower() == 'backdrop.jpg':
            backdrop = sibling
        elif sibling.name.lower() == 'poster.jpg':
            poster = sibling
    return backdrop, poster


def _find_movies(parent, root):
    # type: (Path, Path) -> Generator[MovieResult, None, None]
    for child in parent.children:
        if child.is_video():
            subs = [(sub, _sub_id_language(sub)) for sub in _scan_for_subs(parent, child)]
            backdrop, poster = _scan_for_images(child)
            # yield MovieResult(child, None if parent == root else parent, subs, backdrop, poster)
            yield MovieResult(path=child, parent=parent, subs=subs, backdrop=backdrop, poster=poster)
        if child.is_dir():
            yield from _find_movies(child, root)


def find_movies(root):
    # type: (Union[str, Path]) -> Generator[MovieResult, None, None]
    """
    For each movie file found from the root, yield the movie file's path as well as its parent
    directory's path.

    Sometimes the movie file itself has no useful information while its parent directory has
    some. Elements directly under the root yield None for their parent.
    """
    root = as_path(root)
    root_dir = fs.walk(root)
    return _find_movies(root_dir, root_dir)
