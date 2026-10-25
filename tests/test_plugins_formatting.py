"""Coverage for the formatting plugins: strikethrough, mark, insert,
superscript and subscript (mistune.plugins.formatting).

All expected HTML was produced by running the real parser first; the
tests pin that behaviour, including the quirks noted below.
"""

import mistune
from mistune.plugins.formatting import (
    render_insert,
    render_mark,
    render_strikethrough,
    render_subscript,
    render_superscript,
)


def fmt_md():
    return mistune.create_markdown(
        plugins=["strikethrough", "mark", "insert", "superscript", "subscript"]
    )


# --- each marker in isolation -------------------------------------------------

def test_strikethrough():
    assert fmt_md()("~~struck~~\n") == "<p><del>struck</del></p>\n"


def test_mark():
    assert fmt_md()("==marked==\n") == "<p><mark>marked</mark></p>\n"


def test_insert():
    assert fmt_md()("^^inserted^^\n") == "<p><ins>inserted</ins></p>\n"


def test_superscript():
    assert fmt_md()("x^2^\n") == "<p>x<sup>2</sup></p>\n"


def test_subscript():
    assert fmt_md()("H~2~O\n") == "<p>H<sub>2</sub>O</p>\n"


def test_superscript_multi_char_and_subscript_together():
    assert fmt_md()("x^2^ and y~3~\n") == (
        "<p>x<sup>2</sup> and y<sub>3</sub></p>\n"
    )


def test_superscript_multi_digit():
    assert fmt_md()("x^10^\n") == "<p>x<sup>10</sup></p>\n"


# --- unclosed / empty / whitespace markers stay literal -----------------------

def test_strikethrough_unclosed_stays_literal():
    assert fmt_md()("~~unclosed\n") == "<p>~~unclosed</p>\n"


def test_strikethrough_space_after_opener_stays_literal():
    assert fmt_md()("~~ ~~ empty\n") == "<p>~~ ~~ empty</p>\n"


def test_mark_unclosed_stays_literal():
    assert fmt_md()("==unclosed\n") == "<p>==unclosed</p>\n"


def test_insert_unclosed_stays_literal():
    assert fmt_md()("^^unclosed\n") == "<p>^^unclosed</p>\n"


# --- first-close-wins pairing --------------------------------------------------

def test_mark_pairs_with_first_closing_marker():
    # Quirk (current behaviour): pairing is greedy on the first close,
    # so the second "==" pair is left literal.
    assert fmt_md()("==a ==b== c==\n") == "<p><mark>a ==b</mark> c==</p>\n"


def test_insert_pairs_with_first_closing_marker():
    assert fmt_md()("^^a ^^b^^ c^^\n") == "<p><ins>a ^^b</ins> c^^</p>\n"


def test_strikethrough_repeats_pair_independently():
    assert fmt_md()("~~a~~b~~c~~\n") == "<p><del>a</del>b<del>c</del></p>\n"


# --- inline markup inside formatted spans --------------------------------------

def test_strikethrough_wraps_bold():
    assert fmt_md()("~~**bold**~~\n") == "<p><del><strong>bold</strong></del></p>\n"


def test_mark_wraps_emphasis():
    assert fmt_md()("==*em*==\n") == "<p><mark><em>em</em></mark></p>\n"


# --- superscript / subscript pattern quirks ------------------------------------

def test_superscript_content_cannot_contain_plain_space():
    # Quirk: a plain space inside ^...^ breaks the match entirely.
    assert fmt_md()("x^a b^ y\n") == "<p>x^a b^ y</p>\n"
    assert fmt_md()("a^b c^d\n") == "<p>a^b c^d</p>\n"


def test_superscript_escaped_space_is_allowed():
    assert fmt_md()("x^a\\ b^ y\n") == "<p>x<sup>a b</sup> y</p>\n"


def test_superscript_escaped_caret_is_content():
    assert fmt_md()("x^\\^^ y\n") == "<p>x<sup>^</sup> y</p>\n"


def test_superscript_double_caret_is_not_superscript():
    # "^^" belongs to the insert plugin; a lone "a^^b" matches neither.
    assert fmt_md()("a^^b\n") == "<p>a^^b</p>\n"


def test_subscript_single_tilde_word():
    assert fmt_md()("~tilde~\n") == "<p><sub>tilde</sub></p>\n"


def test_subscript_content_with_space():
    # Quirk (current behaviour): subscript is pattern-based like
    # superscript, so a plain space inside breaks the match entirely.
    assert fmt_md()("H~2 O~ here\n") == "<p>H~2 O~ here</p>\n"


def test_mark_escaped_equals_unescaped_one_level():
    # Two literal backslashes in the source survive as one backslash
    # each inside the mark; a single backslash escape would be consumed
    # completely and render as bare "==".
    assert fmt_md()("==mark \\\\=\\\\= equal==\n") == (
        "<p><mark>mark \\=\\= equal</mark></p>\n"
    )


# --- direct renderers ----------------------------------------------------------

def test_render_strikethrough():
    assert render_strikethrough(None, "x") == "<del>x</del>"


def test_render_mark():
    assert render_mark(None, "x") == "<mark>x</mark>"


def test_render_insert():
    assert render_insert(None, "x") == "<ins>x</ins>"


def test_render_superscript():
    assert render_superscript(None, "2") == "<sup>2</sup>"


def test_render_subscript():
    assert render_subscript(None, "2") == "<sub>2</sub>"
