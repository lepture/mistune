import pytest

from mistune import create_markdown


@pytest.fixture(params=[False, True], ids=["plain", "speedup"])
def md(request):
    plugins = ["def_list", "speedup"] if request.param else ["def_list"]
    return create_markdown(plugins=plugins)


@pytest.mark.parametrize("indent", range(4))
@pytest.mark.parametrize("separator", [" ", "\t"], ids=["space", "tab"])
@pytest.mark.parametrize("loose", [False, True], ids=["tight", "loose"])
def test_definition_marker_indentation(md, indent, separator, loose):
    source = "Term\n" + ("\n" if loose else "") + " " * indent + ":" + separator + "definition\n"
    definition = "<p>definition</p>\n" if loose else "definition"
    assert md(source) == "<dl>\n<dt>Term</dt>\n<dd>" + definition + "</dd>\n</dl>\n"


def test_successive_definition_markers_with_different_indentation(md):
    source = "Term\n: first\n : second\n  : third\n   : fourth\n"
    assert md(source) == (
        "<dl>\n<dt>Term</dt>\n<dd>first</dd>\n<dd>second</dd>\n<dd>third</dd>\n<dd>fourth</dd>\n</dl>\n"
    )


def test_indented_definition_preserves_continuation_blocks(md):
    source = "Term\n   : definition\n    continuation\n\n        code\n\nparagraph\n"
    assert md(source) == (
        "<dl>\n<dt>Term</dt>\n<dd><p>definition\ncontinuation</p>\n"
        "<pre><code>code</code></pre>\n</dd>\n</dl>\n<p>paragraph</p>\n"
    )


def test_four_space_indented_colon_is_not_a_definition_marker(md):
    assert md("Term\n    : definition\n") == "<p>Term\n: definition</p>\n"


def test_indented_marker_requires_a_term(md):
    assert md("   : orphan\n") == "<p>: orphan</p>\n"


@pytest.mark.parametrize("speedup", [False, True])
def test_indented_definition_ast(speedup):
    plugins = ["def_list", "speedup"] if speedup else ["def_list"]
    md = create_markdown(renderer=None, plugins=plugins)
    assert md("Term\n   : definition\n") == [
        {
            "type": "def_list",
            "children": [
                {"type": "def_list_head", "children": [{"type": "text", "raw": "Term"}]},
                {
                    "type": "def_list_item",
                    "children": [{"type": "block_text", "children": [{"type": "text", "raw": "definition"}]}],
                },
            ],
        }
    ]


@pytest.mark.parametrize("definition_at_end", [False, True])
def test_definition_list_preserves_reference_definitions(md, definition_at_end):
    source = "Term\n: [inside][ref]\n\n    [ref]: /target\n"
    definition = '<p><a href="/target">inside</a></p>\n'
    if not definition_at_end:
        source += "\n    Final paragraph.\n"
        definition += "<p>Final paragraph.</p>\n"
    source += "\n[outside][ref]\n"

    assert md(source) == (
        "<dl>\n<dt>Term</dt>\n<dd>" + definition + '</dd>\n</dl>\n<p><a href="/target">outside</a></p>\n'
    )
    assert md("[outside][ref]\n") == "<p>[outside][ref]</p>\n"


@pytest.mark.parametrize("outer_first", [False, True])
def test_definition_list_reference_precedence(md, outer_first):
    source = "Term\n: [inside][ref]\n\n    [ref]: /inner\n\n[outside][ref]\n"
    outer = "[ref]: /outer\n\n"
    source = outer + source if outer_first else source + "\n" + outer
    expected = "/outer" if outer_first else "/inner"

    assert md(source).count('href="' + expected + '"') == 2


def test_reference_definition_shared_between_definition_items(md):
    source = "First\n: [inside][ref]\n\nSecond\n: another definition\n\n    [ref]: /target\n\n[outside][ref]\n"
    result = md(source)
    assert '<a href="/target">inside</a>' in result
    assert '<a href="/target">outside</a>' in result


@pytest.mark.parametrize("speedup", [False, True])
def test_definition_list_reference_ast(speedup):
    plugins = ["def_list", "speedup"] if speedup else ["def_list"]
    md = create_markdown(renderer=None, plugins=plugins)
    tokens = md("Term\n: [inside][ref]\n\n    [ref]: /target\n\n[outside][ref]\n")
    inside = tokens[0]["children"][1]["children"][0]["children"][0]
    outside = tokens[-1]["children"][0]
    for token in (inside, outside):
        assert token["type"] == "link"
        assert token["attrs"]["url"] == "/target"
