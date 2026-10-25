"""Coverage for the abbr and task_lists plugins.

All expected HTML was produced by running the real parser first; the
tests pin that behaviour, including the quirks noted below.
"""

import mistune
from mistune.plugins.abbr import render_abbr
from mistune.plugins.task_lists import render_task_list_item


def abbr_md():
    return mistune.create_markdown(plugins=["abbr"])


def task_md():
    return mistune.create_markdown(plugins=["task_lists"])


# --- abbr --------------------------------------------------------------------

def test_abbr_basic_definition_applies():
    assert abbr_md()("The HTML spec\n\n*[HTML]: Hyper Text Markup Language\n") == (
        "<p>The <abbr title=\"Hyper Text Markup Language\">HTML</abbr> spec</p>\n"
    )


def test_abbr_definition_itself_produces_no_output():
    out = abbr_md()("The HTML spec\n\n*[HTML]: Hyper Text Markup Language\n")
    assert out.count("<abbr") == 1
    assert "Hyper Text Markup Language" in out  # only as the title attribute


def test_abbr_without_definition_left_alone():
    assert abbr_md()("No defs HTML here\n") == "<p>No defs HTML here</p>\n"


def test_abbr_matches_inside_longer_word():
    # Quirk (current behaviour): matching is a plain substring search,
    # so HTML inside HTML5 is also wrapped and the "5" is left behind.
    assert abbr_md()("HTML and HTML5 here\n\n*[HTML]: Hyper Text Markup Language\n") == (
        "<p><abbr title=\"Hyper Text Markup Language\">HTML</abbr> and "
        "<abbr title=\"Hyper Text Markup Language\">HTML</abbr>5 here</p>\n"
    )


def test_abbr_multiple_definitions():
    assert abbr_md()(
        "W3C and HTML\n\n*[HTML]: Hyper Text Markup Language\n"
        "*[W3C]: World Wide Web Consortium\n"
    ) == (
        "<p><abbr title=\"World Wide Web Consortium\">W3C</abbr> and "
        "<abbr title=\"Hyper Text Markup Language\">HTML</abbr></p>\n"
    )


def test_abbr_definition_before_use():
    assert abbr_md()(
        "*[HTML]: Hyper Text Markup Language\n\nHTML at start\n"
    ) == (
        "<p><abbr title=\"Hyper Text Markup Language\">HTML</abbr> at start</p>\n"
    )


def test_abbr_longest_key_wins_over_prefix_key():
    assert abbr_md()("HTML HT\n\n*[HT]: short\n*[HTML]: long\n") == (
        "<p><abbr title=\"long\">HTML</abbr> <abbr title=\"short\">HT</abbr></p>\n"
    )


def test_abbr_definition_on_next_indented_line():
    assert abbr_md()("HTML here\n\n*[HTML]:\n    Hyper Text Markup\n") == (
        "<p><abbr title=\"Hyper Text Markup\">HTML</abbr> here</p>\n"
    )


def test_abbr_same_line_text_does_not_continue():
    # Quirk (current behaviour): when the definition already has text on
    # its own line, a following indented line is NOT part of the
    # definition -- it becomes a code block instead.
    assert abbr_md()("HTML here\n\n*[HTML]: Hyper\n    Markup\n") == (
        "<p><abbr title=\"Hyper\">HTML</abbr> here</p>\n"
        "<pre><code>Markup</code></pre>\n"
    )


def test_abbr_empty_definition_renders_bare_abbr():
    assert abbr_md()("HTML\n\n*[HTML]: \n") == "<p><abbr>HTML</abbr></p>\n"


def test_render_abbr_no_title():
    assert render_abbr(None, "HTML", "") == "<abbr>HTML</abbr>"


def test_render_abbr_title_is_escaped():
    assert render_abbr(None, "HTML", 'a"b & <c>') == (
        '<abbr title="a&quot;b &amp; &lt;c&gt;">HTML</abbr>'
    )


# --- task_lists ---------------------------------------------------------------

def test_task_list_unchecked_checked_uppercase():
    assert task_md()("- [ ] unchecked\n- [x] checked\n- [X] upper\n- plain\n") == (
        "<ul>\n"
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "unchecked</li>\n"
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled checked/>'
        "checked</li>\n"
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled checked/>'
        "upper</li>\n"
        "<li>plain</li>\n</ul>\n"
    )


def test_task_list_marker_requires_trailing_space():
    assert task_md()("- [ ]a no space\n") == "<ul>\n<li>[ ]a no space</li>\n</ul>\n"


def test_task_list_other_bracket_contents_not_tasks():
    assert task_md()("- [] empty\n") == "<ul>\n<li>[] empty</li>\n</ul>\n"
    assert task_md()("- [y] other\n") == "<ul>\n<li>[y] other</li>\n</ul>\n"


def test_task_list_ordered_list():
    assert task_md()("1. [ ] ordered\n") == (
        "<ol>\n<li class=\"task-list-item\">"
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "ordered</li>\n</ol>\n"
    )


def test_task_list_inline_markup_inside_task():
    assert task_md()("- [ ] task with `code` and *em*\n") == (
        "<ul>\n<li class=\"task-list-item\">"
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "task with <code>code</code> and <em>em</em></li>\n</ul>\n"
    )


def test_task_list_nested_item():
    assert task_md()("- nested\n  - [ ] sub\n") == (
        "<ul>\n<li>nested<ul>\n<li class=\"task-list-item\">"
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "sub</li>\n</ul>\n</li>\n</ul>\n"
    )


def test_task_list_inside_blockquote():
    assert task_md()("> - [ ] quoted task\n") == (
        "<blockquote>\n<ul>\n<li class=\"task-list-item\">"
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "quoted task</li>\n</ul>\n</blockquote>\n"
    )


def test_render_task_list_item_unchecked():
    assert render_task_list_item(None, "do it", False) == (
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "do it</li>\n"
    )


def test_render_task_list_item_checked():
    assert render_task_list_item(None, "do it", True) == (
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled checked/>'
        "do it</li>\n"
    )


def test_render_task_list_item_default_is_unchecked():
    assert render_task_list_item(None, "do it") == (
        '<li class="task-list-item">'
        '<input class="task-list-item-checkbox" type="checkbox" disabled/>'
        "do it</li>\n"
    )


def test_render_task_list_item_checkbox_goes_inside_p():
    assert render_task_list_item(None, "<p>do it</p>", True) == (
        '<li class="task-list-item"><p>'
        '<input class="task-list-item-checkbox" type="checkbox" disabled checked/>'
        "do it</p></li>\n"
    )
