import pathlib

import pytest

from mfnh.movies import _extract_title_year, _tokens
from mfnh.parser.tv import _season_episode


class Path(type(pathlib.Path())):

    def is_file(self):
        return True


def test_tokenization():
    assert list(_tokens('a.b-c_d e(f)[g]')) == ['a', 'b', 'c', 'd', 'e', 'f', 'g']


def short(s):
    return _extract_title_year(Path(s))


def test_clean_title():
    assert short('The Matrix (2009)') == ('The Matrix', 2009)


def test_simple_extract():
    assert short('The.Matrix.2009.H264.1080p.mp4') == ('The Matrix', 2009)


def test_ambiguous_year():
    assert short('2001 space odyssey (1968).avi') == ('2001 space odyssey', 1968)


def test_ambiguous_year_title():
    assert short('2001.mp4') == ('2001', None)


def test_missing_year():
    assert short('Twelve Monkeys 1080p') == ('Twelve Monkeys', None)


def test_year_after_metadata():
    assert short('Truman Show 1080p 1998.mkv') == ('Truman Show', 1998)


def test_year_nothing_extractable():
    with pytest.raises(ValueError):
        assert short('H264')


def test_season_episode():
    assert _season_episode('simpsons s01e02') == (1, 2)
    assert _season_episode('SIMPSONs 05x03') == (5, 3)
