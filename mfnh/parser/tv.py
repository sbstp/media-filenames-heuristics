import re
from enum import Enum
from collections import OrderedDict, deque

from .. import fs, metadata_tokens
from ..util import as_path


_RE_YEAR = re.compile(r'^(\d{4})$')
_RE_SEASON_EPISODE = [
    re.compile(r'^s(\d\d?)e(\d\d?)$', re.IGNORECASE),
    re.compile(r'^(\d\d?)x(\d\d?)$', re.IGNORECASE),
]
_RE_SEASON = re.compile(r'^s(\d\d?)$', re.IGNORECASE)
_RE_EPISODE = re.compile(r'^(:?e|ep)(\d\d?)$', re.IGNORECASE)
_RE_DIGIT = re.compile(r'^(\d\d?)$')
_RE_SEARCH_DIGIT = re.compile(r'(\d\d)')
_SEASON_SET = set(('season', 'saison'))
_EPISODE_SET = set(('episode', 'ep'))


class TokenKind(Enum):
    TEXT = 1
    YEAR = 2
    METADATA = 3
    SEASON = 4
    EPISODE = 5


def _re_match_many(regex_list, token):
    for regex in regex_list:
        m = regex.match(token)
        if m:
            return m
    return None


def _lexer(file):
    tokens = deque(file.tokenize())
    while len(tokens) > 0:
        token = tokens.popleft().lower()

        if _RE_YEAR.match(token):
            yield (TokenKind.YEAR, token)
            continue
        elif token in metadata_tokens.ALL:
            yield (TokenKind.METADATA, token)
            continue

        m = _re_match_many(_RE_SEASON_EPISODE, token)
        if m:
            yield (TokenKind.SEASON, m.group(1))
            yield (TokenKind.EPISODE, m.group(2))
            continue

        m = _RE_SEASON.match(token)
        if m:
            yield (TokenKind.SEASON, m.group(1))
            continue

        m = _RE_EPISODE.match(token)
        if m:
            yield (TokenKind.EPISODE, m.group(2))
            continue

        if token in _SEASON_SET and tokens and _RE_DIGIT.match(tokens[0]):
            yield (TokenKind.SEASON, tokens.popleft())
            continue

        if token in _EPISODE_SET and tokens and _RE_DIGIT.match(tokens[0]):
            yield (TokenKind.EPISODE, tokens.popleft())
            continue

        # two digits tokens next to each other
        m = _RE_DIGIT.match(token)
        if m and tokens and _RE_DIGIT.match(tokens[0]):
            yield (TokenKind.SEASON, token)
            yield (TokenKind.EPISODE, tokens.popleft())

        yield (TokenKind.TEXT, token)


def _parser(file):
    ep = TvEpisode()
    parent = file
    while parent is not None and not parent.is_root():
        title = []
        skip_text = False
        for (kind, token) in _lexer(parent):
            if kind == TokenKind.METADATA:
                skip_text = True
            elif kind == TokenKind.YEAR:
                skip_text = True
            elif kind == TokenKind.SEASON:
                ep.set_season(int(token))
                skip_text = True
            elif kind == TokenKind.EPISODE:
                ep.set_episode(int(token))
                skip_text = True
            elif kind == TokenKind.TEXT:
                if not skip_text:
                    title.append(token)

        if not ep.episode and parent.is_file():
            # last resort, try to find a digit in the title
            m = _RE_SEARCH_DIGIT.search(file.name)
            if m:
                ep.set_episode(int(m.group(1)))
            else:
                ep.add_title_candidate(' '.join(title))
        else:
            ep.add_title_candidate(' '.join(title))

        parent = parent.parent
    print(ep.title_candidates, ep.season, ep.episode)
    if not ep.title_candidates or ep.season is None or ep.episode is None:
        return None
    return ep


class TvEpisode:

    def __init__(self):
        self.title_candidates = OrderedDict()
        self.season = None
        self.episode = None

    def add_title_candidate(self, candidate):
        if candidate:
            candidate = candidate.strip().lower()
            self.title_candidates[candidate] = None

    def set_season(self, season):
        if season is not None:
            if self.season is None:
                self.season = season
            else:
                if self.season != season:
                    print('season assert', self, self.season, season)

    def set_episode(self, episode):
        if episode is not None:
            if self.episode is None:
                self.episode = episode
            else:
                if self.episode != episode:
                    print('episode assert', self, self.episode, episode)

    def __repr__(self):
        def f(x):
            if x is None:
                return '-'
            else:
                return '{:02}'.format(x)
        return 'S{}E{}: ({})'.format(f(self.season), f(self.episode), ', '.join(self.title_candidates.keys()))


def _find_tv(parent, root):
    for child in parent.children:
        if child.is_video():
            print(child.name)
            print(_parser(child))
            print('----')
        elif child.is_dir() and child.name.lower() not in ('extras', 'sample', 'samples'):
            _find_tv(child, root)


def find_tv(root):
    root = as_path(root)
    root_dir = fs.walk(root)
    return _find_tv(root_dir, root_dir)
