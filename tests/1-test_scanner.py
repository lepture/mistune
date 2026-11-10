import re

import pytest

from mistune.scanner import Scanner


@pytest.fixture
def portable_scanner(monkeypatch):
    if not hasattr(re, 'ASCII'):
        pytest.skip('The capture restriction affects Python 3, not Python 2')

    def reject_captures(self, *args, **kwargs):
        raise ValueError('Cannot use capturing groups in re.Scanner')

    monkeypatch.setattr(re.Scanner, '__init__', reject_captures)
    return Scanner


def tokens(scanner, text):
    return list(scanner.iter(text, {}, lambda text, state: ('text', text)))


def test_portable_scanner_captures_and_backreferences(portable_scanner):
    def capture(match, state):
        return ('pair', match.group(1), match.group(2))

    scanner = portable_scanner([(r'([*_])(\w+)\1', ('pair', capture))])
    assert tokens(scanner, 'a *word* b') == [
        ('text', 'a '), ('pair', '*', 'word'), ('text', ' b'),
    ]


def test_portable_scanner_priority_and_overlapping_candidates(portable_scanner):
    def token(match, state):
        return ('token', match.group())

    scanner = portable_scanner([
        (r'\\!', ('escape', token)),
        (r'!?\[foo\]', ('link', token)),
        (r'\[foo\]', ('later', lambda m, s: ('wrong', m.group()))),
    ])
    assert tokens(scanner, r'\![foo]') == [('token', r'\!'), ('token', '[foo]')]


@pytest.mark.parametrize('flags, expected', [(0, [('text', u'\u00a0')]),
                                          (re.UNICODE, [('space', u'\u00a0')])])
def test_portable_scanner_character_classes(portable_scanner, flags, expected):
    scanner = portable_scanner([(r'\s+', ('space', lambda m, s: ('space', m.group())))], flags)
    assert tokens(scanner, u'\u00a0') == expected


def test_portable_scanner_empty_match_then_nonempty(portable_scanner):
    scanner = portable_scanner([
        (r'|a', ('empty', lambda m, s: ('token', m.group()))),
    ])
    assert tokens(scanner, 'a') == [('token', ''), ('token', 'a'), ('token', '')]


def test_portable_scanner_does_not_hide_other_value_errors(monkeypatch):
    def fail(self, *args, **kwargs):
        raise ValueError('unrelated failure')

    monkeypatch.setattr(re.Scanner, '__init__', fail)
    with pytest.raises(ValueError, match='unrelated failure'):
        Scanner([])


def test_portable_scanner_inherited_scan_contract(portable_scanner):
    scanner = portable_scanner([
        (r'(a+)', lambda scanner, text: ('a', scanner.match.group(1))),
        (r' +', None),
        (r'b+', 'b'),
    ])
    assert scanner.scan('aa bb?aa') == ([('a', 'aa'), 'b'], '?aa')
    assert scanner.scan('?aa') == ([], '?aa')


def test_portable_scanner_scan_stops_at_empty_match(portable_scanner):
    scanner = portable_scanner([(r'|a', 'empty')])
    assert scanner.scan('a') == ([], 'a')
