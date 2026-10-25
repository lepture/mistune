"""Coverage for mistune.toc: render_toc_ul and add_toc_hook.

All expected values were produced by running the real code first; the
tests pin that behaviour, including the quirks noted below.
"""

import mistune
from mistune.toc import add_toc_hook, render_toc_ul


def toc_md(**kwargs):
    md = mistune.create_markdown(renderer="html")
    add_toc_hook(md, **kwargs)
    return md


# --- render_toc_ul --------------------------------------------------------------

def test_render_toc_ul_empty():
    assert render_toc_ul([]) == ""


def test_render_toc_ul_single_item():
    assert render_toc_ul([(1, "a", "Intro")]) == (
        '<ul>\n<li><a href="#a">Intro</a></li>\n</ul>\n'
    )


def test_render_toc_ul_siblings():
    assert render_toc_ul([(1, "a", "A"), (1, "b", "B"), (1, "c", "C")]) == (
        "<ul>\n"
        '<li><a href="#a">A</a></li>\n'
        '<li><a href="#b">B</a></li>\n'
        '<li><a href="#c">C</a></li>\n</ul>\n'
    )


def test_render_toc_ul_nested_then_back():
    assert render_toc_ul(
        [(1, "a", "A"), (2, "b", "B"), (2, "c", "C"), (1, "d", "D")]
    ) == (
        "<ul>\n"
        '<li><a href="#a">A</a>\n<ul>\n'
        '<li><a href="#b">B</a></li>\n'
        '<li><a href="#c">C</a></li>\n</ul>\n</li>\n'
        '<li><a href="#d">D</a></li>\n</ul>\n'
    )


def test_render_toc_ul_level_jump_skips_no_level():
    # A jump from level 1 straight to 3 still nests exactly one <ul>.
    assert render_toc_ul([(1, "a", "A"), (3, "c", "C")]) == (
        "<ul>\n<li><a href=\"#a\">A</a>\n<ul>\n"
        '<li><a href="#c">C</a></li>\n</ul>\n</li>\n</ul>\n'
    )


def test_render_toc_ul_starting_below_level_1():
    assert render_toc_ul([(2, "b", "B"), (1, "a", "A")]) == (
        "<ul>\n<li><a href=\"#b\">B</a></li>\n"
        '<li><a href="#a">A</a></li>\n</ul>\n'
    )


def test_render_toc_ul_deep_nesting_and_return():
    assert render_toc_ul(
        [(1, "a", "A"), (2, "b", "B"), (3, "c", "C"), (2, "d", "D"), (1, "e", "E")]
    ) == (
        "<ul>\n"
        '<li><a href="#a">A</a>\n<ul>\n'
        '<li><a href="#b">B</a></li>\n'
        '<li><a href="#c">C</a></li>\n</ul>\n</li>\n'
        '<li><a href="#d">D</a></li>\n</ul>\n</li>\n'
        '<li><a href="#e">E</a></li>\n</ul>\n'
    )


def test_render_toc_ul_single_deep_item():
    assert render_toc_ul([(3, "c", "C")]) == (
        '<ul>\n<li><a href="#c">C</a></li>\n</ul>\n'
    )


def test_render_toc_ul_id_is_escaped_but_text_is_not():
    # Quirk (current behaviour): the href id goes through escape(), the
    # link text is inserted verbatim -- raw HTML in a title passes through.
    assert render_toc_ul([(1, "a&b", "<b>bold</b>")]) == (
        '<ul>\n<li><a href="#a&amp;b"><b>bold</b></a></li>\n</ul>\n'
    )


# --- add_toc_hook ---------------------------------------------------------------

def test_toc_hook_default_levels_and_ids():
    md = toc_md()
    html, state = md.parse("# One\n## Two\n### Three\n#### Four\n# One\n")
    assert state.env["toc_items"] == [
        (1, "toc_1", "One"),
        (2, "toc_2", "Two"),
        (3, "toc_3", "Three"),
        (1, "toc_4", "One"),
    ]
    # Level 4 is outside the default max_level=3, so it gets no id.
    assert '<h4>Four</h4>' in html
    assert '<h1 id="toc_1">One</h1>' in html
    assert '<h1 id="toc_4">One</h1>' in html


def test_toc_hook_ids_are_index_based_not_text_based():
    # Two identical headings get distinct ids because the id comes from
    # the heading's position, not its text.
    md = toc_md()
    _, state = md.parse("# Same\n# Same\n")
    assert [item[1] for item in state.env["toc_items"]] == ["toc_1", "toc_2"]


def test_toc_hook_min_max_level_filter():
    md = toc_md(min_level=2, max_level=2)
    _, state = md.parse("# One\n## Two\n### Three\n")
    assert state.env["toc_items"] == [(2, "toc_1", "Two")]


def test_toc_hook_custom_heading_id_function():
    md = toc_md(heading_id=lambda tok, i: "custom_" + str(i))
    html, state = md.parse("# A\n# B\n")
    assert state.env["toc_items"] == [(1, "custom_0", "A"), (1, "custom_1", "B")]
    assert '<h1 id="custom_0">A</h1>' in html


def test_toc_hook_custom_ids_are_not_deduplicated():
    # Quirk (current behaviour): with a custom heading_id function the
    # auto-uniqueness pass is off, so duplicate ids are kept as-is.
    md = toc_md(heading_id=lambda tok, i: "same")
    html, state = md.parse("# A\n# B\n# C\n")
    assert state.env["toc_items"] == [
        (1, "same", "A"), (1, "same", "B"), (1, "same", "C"),
    ]
    assert html.count('id="same"') == 3


def test_toc_hook_default_id_avoids_id_already_in_source():
    # The allocator scans the raw source for id="..." attributes, so a
    # toc_1 already present in the document pushes the first heading to
    # toc_1_1 (even though that source id ends up escaped as text).
    md = toc_md()
    html, state = md.parse('<div id="toc_1">x</div>\n\n# A\n# B\n')
    assert state.env["toc_items"] == [(1, "toc_1_1", "A"), (1, "toc_2", "B")]
    assert '<h1 id="toc_1_1">A</h1>' in html


def test_toc_hook_heading_markup_stripped_from_item_text():
    md = toc_md()
    _, state = md.parse("# **Bold** and `code` Title\n")
    assert state.env["toc_items"] == [(1, "toc_1", "Bold and code Title")]


def test_toc_hook_setext_heading_included_with_trailing_newline():
    # Quirk (current behaviour): a setext heading's toc text keeps its
    # trailing newline.
    md = toc_md()
    _, state = md.parse("Setext\n=======\n")
    assert state.env["toc_items"] == [(1, "toc_1", "Setext\n")]


def test_toc_hook_quoted_heading_not_counted():
    md = toc_md()
    _, state = md.parse("> # Quoted heading\n\n# Real\n")
    assert state.env["toc_items"] == [(1, "toc_1", "Real")]


def test_toc_hook_no_headings_gives_empty_items():
    md = toc_md()
    _, state = md.parse("just a paragraph\n")
    assert state.env["toc_items"] == []
