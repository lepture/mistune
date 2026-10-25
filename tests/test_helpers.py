"""Coverage for mistune.helpers: link parsing primitives.

Note on call convention (verified by probing): parse_link_text expects
``pos`` to point just past the opening "[" -- callers in the parser pass
the position after the bracket, and the returned position points just
past the closing "]". All expected values below were produced by
running the real functions first.
"""

from mistune import helpers as h


# --- unescape_char ---------------------------------------------------------------

def test_unescape_char_backslash_punctuation():
    assert h.unescape_char("a\\*b") == "a*b"
    assert h.unescape_char("a\\!b\\?c") == "a!b?c"


def test_unescape_char_double_backslash_collapses_one_level():
    assert h.unescape_char("a\\\\b") == "a\\b"


def test_unescape_char_backslash_before_non_punctuation_kept():
    assert h.unescape_char("a\\nb") == "a\\nb"


def test_unescape_char_plain_and_trailing_backslash():
    assert h.unescape_char("plain") == "plain"
    assert h.unescape_char("a\\") == "a\\"


# --- parse_link_text ---------------------------------------------------------------

def test_parse_link_text_simple():
    assert h.parse_link_text("[a]b", 1) == ("a", 3)


def test_parse_link_text_nested_brackets():
    assert h.parse_link_text("[a [b] c] d", 1) == ("a [b] c", 9)


def test_parse_link_text_escaped_close_bracket_is_not_a_close():
    assert h.parse_link_text("[a\\]b] c", 1) == ("a\\]b", 6)


def test_parse_link_text_unclosed_returns_none_with_end_pos():
    # Quirk (current behaviour): on failure it returns (None, pos) where
    # pos is the end of the string, not (None, None).
    assert h.parse_link_text("[unclosed", 1) == (None, 9)


# --- parse_link_label ---------------------------------------------------------------

def test_parse_link_label_simple():
    assert h.parse_link_label("label] rest", 0) == ("label", 6)


def test_parse_link_label_empty():
    assert h.parse_link_label("] rest", 0) == ("", 1)


def test_parse_link_label_escaped_bracket_inside():
    assert h.parse_link_label("a\\]b] rest", 0) == ("a\\]b", 5)


def test_parse_link_label_no_closing_bracket():
    assert h.parse_link_label("no bracket", 0) == (None, None)


def test_parse_link_label_max_length():
    assert h.parse_link_label("x" * 999 + "] rest", 0)[0] == "x" * 999
    # One more character over the 999 limit: no match at all.
    assert h.parse_link_label("x" * 1000 + "] rest", 0) == (None, None)


# --- parse_link_href ---------------------------------------------------------------

def test_parse_link_href_plain():
    assert h.parse_link_href("http://x.com) rest", 0) == ("http://x.com", 12)


def test_parse_link_href_angle_brackets_allow_spaces():
    assert h.parse_link_href("<http://x.com>) rest", 0) == ("http://x.com", 14)
    assert h.parse_link_href("<a b>) rest", 0) == ("a b", 5)


def test_parse_link_href_plain_stops_at_first_space():
    assert h.parse_link_href("a b) rest", 0) == ("a", 1)


def test_parse_link_href_nested_parens_balanced():
    assert h.parse_link_href("(a(b)c) rest", 0) == ("(a(b)c)", 7)
    assert h.parse_link_href("a(b(c)d)e) rest", 0) == ("a(b(c)d)e", 9)


def test_parse_link_href_unbalanced_parens_rejected():
    assert h.parse_link_href("(unclosed rest", 0) == (None, None)


def test_parse_link_href_leading_whitespace_skipped():
    assert h.parse_link_href("  spaced) rest", 0) == ("spaced", 8)


def test_parse_link_href_backslash_only_escapes_punctuation():
    # A backslash before a space is NOT an escape (space is not
    # punctuation), so the href ends at the space.
    assert h.parse_link_href("a\\ b) rest", 0) == ("a\\", 2)


def test_parse_link_href_empty_and_missing():
    assert h.parse_link_href(") rest", 0) == ("", 0)
    assert h.parse_link_href("", 0) == (None, None)


# --- parse_link_title ---------------------------------------------------------------

def test_parse_link_title_double_single_paren_quotes():
    assert h.parse_link_title(' "title")', 0, 9) == ("title", 8)
    assert h.parse_link_title(" 't')", 0, 5) == ("t", 4)
    assert h.parse_link_title(" (t)", 0, 4) == ("t", 4)


def test_parse_link_title_escaped_quote_inside():
    assert h.parse_link_title(' "a\\\\"b")', 0, 8) == ('a"b', 7)


def test_parse_link_title_rejects_unclosed_and_bare_text():
    assert h.parse_link_title(' "unclosed', 0, 10) == (None, None)
    assert h.parse_link_title(" notitle)", 0, 9) == (None, None)


def test_parse_link_title_rejects_blank_line_inside():
    assert h.parse_link_title(' "a\n\nb")', 0, 8) == (None, None)


def test_parse_link_title_rejects_nested_paren_in_paren_title():
    assert h.parse_link_title(" (a(b))", 0, 10) == (None, None)


# --- parse_link (combined) ---------------------------------------------------------------

def test_parse_link_with_title():
    assert h.parse_link('/url "title") rest', 0) == (
        {"url": "/url", "title": "title"}, 13,
)


def test_parse_link_without_title():
    assert h.parse_link("/url) rest", 0) == ({"url": "/url"}, 5)


def test_parse_link_angle_href():
    assert h.parse_link("<http://x.com>) rest", 0) == (
        {"url": "http://x.com"}, 15,
)


def test_parse_link_title_and_trailing_space_before_close():
    assert h.parse_link('/url "t") rest', 0) == (
        {"url": "/url", "title": "t"}, 10,
)


def test_parse_link_missing_close_paren_rejected():
    assert h.parse_link("no-close rest", 0) == (None, None)
    assert h.parse_link("/a\\ b) rest", 0) == (None, None)
