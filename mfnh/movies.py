from pathlib import Path
import mimetypes
import re

from . import languages, metadata_tokens
from .util import min


RE_SPLIT = re.compile(r"""
\(([^\)]+)\)| # (parens)
\[([^\]]+)\]| # [square]
([^\-\_\.\s\(\[]+) # Sep.ara.ted
""", re.VERBOSE)
RE_YEAR = re.compile(r'^(\d{4})$')

# 200 MB is a good size to separate movie files from other video files like samples
MIN_MOVIE_SIZE = 200 * 1024 * 1024


def _tokens(line):
    for m in RE_SPLIT.finditer(line):
        yield m.group(1) or m.group(2) or m.group(3)


def _extract_title_year(file: Path):
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
    tokens = list(_tokens(file.stem)) if file.is_file() else list(_tokens(file.name))
    years = []
    metadata_idx = None

    # Collect candidates for years and first metadata position.
    for idx, token in enumerate(tokens):
        m = RE_YEAR.match(token)
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
        if not title:
            title = [year]
    except ValueError:
        title = tokens[:]

    return ' '.join(title), year


class MovieResult:

    def __init__(self, path, parent, subs):
        self.path = path  # type: Path
        self.title = _extract_title_year(path)  # type: Tuple[str, Optional[int]]
        self.parent = parent  # type: Optional[Path]
        self.parent_title = None  # type: Optional[Tuple[str, Optional[Int]]]
        if parent:
            self.parent_title = _extract_title_year(parent)
        self.size = path.stat().st_size  # type: int
        self.subs = subs


def _is_movie_file(file):
    # type: (Path,) -> bool
    kind, _ = mimetypes.guess_type(file.absolute().as_uri(), strict=False)
    if kind and kind.startswith("video/"):
        if file.stat().st_size >= MIN_MOVIE_SIZE:
            return True
    return False


def _is_subtitle_file(file):
    return file.suffix.lower() in ('.srt', '.sub', '.idx', '.usf')


def _scan_for_subs(parent, file):
    for item in parent.iterdir():
        # Scan for files named like the movie file but with a subtitle extension
        if item.is_file() and item.name.startswith(file.stem) and _is_subtitle_file(item):
            yield item
        # Scan for folders named subs/ or subtitles/ and take any subtitle file inside
        elif item.is_dir() and item.name.lower() in ('subs', 'subtitles'):
            for subitem in item.iterdir():
                if subitem.is_file() and _is_subtitle_file(subitem):
                    yield subitem


def _sub_id_language(subfile):
    for token in reversed(list(_tokens(subfile.stem))):
        if token.lower() in metadata_tokens.ALL_WITHOUT_LANGUAGES:
            break
        try:
            lang = languages.lookup(token)
            return lang
        except:
            pass
    return None


def _find_movies(parent, root):
    # type: (Path, Path) -> Generator[MovieResult, None, None]
    for item in parent.iterdir():
        if item.is_file() and _is_movie_file(item):
                subs = [(sub, _sub_id_language(sub)) for sub in _scan_for_subs(parent, item)]
                yield MovieResult(item, None if parent == root else parent, subs)
        if item.is_dir():
            yield from _find_movies(item, root)


def find_movies(root):
    # type: (Union[str, Path]) -> Generator[MovieResult, None, None]
    """
    For each movie file found from the root, yield the movie file's path as well as its parent
    directory's path.

    Sometimes the movie file itself has no useful information while its parent directory has
    some. Elements directly under the root yield None for their parent.
    """
    if not isinstance(root, Path):
        root = Path(root)
    return _find_movies(root, root)
