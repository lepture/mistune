"""Coverage for the ruby and spoiler plugins (mistune.plugins.ruby/spoiler).

All expected HTML was produced by running the real parser first (probe
script); the tests pin that behaviour, including the quirks noted below.
"""

import mistune
from mistune.plugins.ruby import render_ruby
from mistune.plugins.spoiler import render_block_spoiler, render_inline_spoiler


def ruby_md():
    return mistune.create_markdown(plugins=["ruby"])


def spoiler_md():
    return mistune.create_markdown(plugins=["spoiler"])


# --- ruby: rendering through the parser -------------------------------------

def test_ruby_single_annotation():
    assert ruby_md()("[漢字(ㄏㄢˋㄗˋ)]\n") == (
        "<p><ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby></p>\n"
    )


def test_ruby_multiple_annotations_in_one_group():
    assert ruby_md()("[漢(ㄏㄢˋ)字(ㄗˋ)]\n") == (
        "<p><ruby>漢<rt>ㄏㄢˋ</rt></ruby>"
        "<ruby>字<rt>ㄗˋ</rt></ruby></p>\n"
    )


def test_ruby_text_around_annotation_kept():
    assert ruby_md()("[漢字(ㄏㄢˋㄗˋ)] trailing\n") == (
        "<p><ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby> trailing</p>\n"
    )


def test_ruby_plain_brackets_are_not_ruby():
    assert ruby_md()("plain [notruby] text\n") == "<p>plain [notruby] text</p>\n"


def test_ruby_inline_link_wraps_annotation():
    assert ruby_md()('[漢字(ㄏㄢˋㄗˋ)](/url "title")\n') == (
        '<p><a href="/url" title="title">'
        "<ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>\n"
    )


def test_ruby_reference_link_wraps_annotation():
    md = ruby_md()
    assert md("[漢字(ㄏㄢˋㄗˋ)][link]\n\n[link]: /url \"title\"\n") == (
        '<p><a href="/url" title="title">'
        "<ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby></a></p>\n"
    )


def test_ruby_unknown_reference_kept_verbatim_after_annotation():
    # Quirk (current behaviour): an unresolvable [label] is left as
    # literal text after the ruby, not dropped or linked.
    assert ruby_md()("[漢字(ㄏㄢˋㄗˋ)][missing]\n") == (
        "<p><ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby>[missing]</p>\n"
    )


# --- ruby: direct renderer ---------------------------------------------------

def test_render_ruby():
    assert render_ruby(None, "漢字", "ㄏㄢˋㄗˋ") == (
        "<ruby>漢字<rt>ㄏㄢˋㄗˋ</rt></ruby>"
    )


def test_render_ruby_empty_reading_kept():
    assert render_ruby(None, "x", "") == "<ruby>x<rt></rt></ruby>"


# --- spoiler: block level ----------------------------------------------------

def test_block_spoiler_single_line():
    assert spoiler_md()(">! this is spoiler\n") == (
        '<div class="spoiler">\n<p>this is spoiler</p>\n</div>\n'
    )


def test_block_spoiler_blank_separator_line_kept_inside():
    assert spoiler_md()(">! line1\n>!\n>! line2\n") == (
        '<div class="spoiler">\n<p>line1</p>\n<p>line2</p>\n</div>\n'
    )


def test_block_spoiler_blank_line_splits_into_two_spoilers():
    assert spoiler_md()(">! a\n\n>! b\n") == (
        '<div class="spoiler">\n<p>a</p>\n</div>\n'
        '<div class="spoiler">\n<p>b</p>\n</div>\n'
    )


def test_block_spoiler_inline_markup_parsed_inside():
    assert spoiler_md()(">! **bold** inside\n") == (
        '<div class="spoiler">\n<p><strong>bold</strong> inside</p>\n</div>\n'
    )


def test_block_spoiler_mixed_quote_lines_fall_back_to_blockquote():
    # Quirk (current behaviour): if any line of the quote lacks the `!`,
    # the whole block is a plain blockquote and the `!` stays literal.
    assert spoiler_md()(">! spoiled\n> plain quote line\n") == (
        "<blockquote>\n<p>! spoiled\nplain quote line</p>\n</blockquote>\n"
    )


def test_block_spoiler_plain_quote_unaffected():
    assert spoiler_md()("> normal quote\n") == (
        "<blockquote>\n<p>normal quote</p>\n</blockquote>\n"
    )


# --- spoiler: inline level ---------------------------------------------------

def test_inline_spoiler_basic():
    assert spoiler_md()("para >! hide me !< end\n") == (
        '<p>para <span class="spoiler">hide me</span> end</p>\n'
    )


def test_inline_spoiler_empty_content_not_a_spoiler():
    # Quirk: an empty `>!  !<` is left literal (escaped) instead of
    # producing an empty spoiler span.
    assert spoiler_md()("para >!  !< end\n") == (
        "<p>para &gt;!  !&lt; end</p>\n"
    )


def test_inline_spoiler_unclosed_not_a_spoiler():
    assert spoiler_md()("para >! unclosed end\n") == (
        "<p>para &gt;! unclosed end</p>\n"
    )


def test_inline_spoiler_cannot_span_lines():
    assert spoiler_md()("para >! multi\nline !< end\n") == (
        "<p>para &gt;! multi\nline !&lt; end</p>\n"
    )


# --- spoiler: direct renderers ----------------------------------------------

def test_render_block_spoiler():
    assert render_block_spoiler(None, "hi\n") == (
        '<div class="spoiler">\nhi\n</div>\n'
    )


def test_render_inline_spoiler():
    assert render_inline_spoiler(None, "hi") == '<span class="spoiler">hi</span>'
