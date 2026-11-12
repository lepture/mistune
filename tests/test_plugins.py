import pytest

from mistune import create_markdown
from mistune.plugins.math import math_in_list, math_in_quote
from mistune.plugins.table import table_in_list, table_in_quote
from tests import BaseTestCase


def load_plugin(plugin_name):
    md1 = create_markdown(escape=False, plugins=[plugin_name])
    md2 = create_markdown(escape=False, plugins=[plugin_name, "speedup"])

    class TestPlugin1(BaseTestCase):
        parse = md1

    class TestPlugin2(BaseTestCase):
        parse = md2

    TestPlugin1.load_fixtures(plugin_name + ".txt")
    TestPlugin2.load_fixtures(plugin_name + ".txt")
    globals()["TestPlugin1_" + plugin_name] = TestPlugin1
    globals()["TestPlugin2_" + plugin_name] = TestPlugin2


load_plugin("url")
load_plugin("strikethrough")
load_plugin("mark")
load_plugin("insert")
load_plugin("superscript")
load_plugin("subscript")
load_plugin("task_lists")
load_plugin("table")
load_plugin("def_list")
load_plugin("footnotes")
load_plugin("abbr")
load_plugin("math")
load_plugin("ruby")
load_plugin("spoiler")


class TestExtraPlugins(BaseTestCase):
    def test_table_in_list(self):
        text = """- Cell | Cell\n  ---- | ----\n   1  |  2\n"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["table", table_in_list])
        self.assertNotIn("<table>", md1(text))
        self.assertIn("<table>", md2(text))

    def test_table_in_quote(self):
        text = """> Cell | Cell\n> ---- | ----\n>  1  |  2\n"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["table", table_in_quote])
        self.assertNotIn("<table>", md1(text))
        self.assertIn("<table>", md2(text))

    def test_math_in_list(self):
        text = """- $$\n  foo\n  $$\n"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["math", math_in_list])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))

    def test_math_in_quote(self):
        text = """> $$\n> foo\n> $$\n"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["math", math_in_quote])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))


class TestFootnoteReferenceDefinitions(BaseTestCase):
    def test_definition_before_another_paragraph(self):
        text = "Text[^one].\n\n[^one]: See [link][ref].\n\n    [ref]: /url\n\n    Final paragraph.\n"
        result = create_markdown(plugins=["footnotes"])(text)
        self.assertIn('<a href="/url">link</a>', result)
        self.assertIn("Final paragraph.", result)
        self.assertNotIn("[ref]", result)

    def test_definition_at_end_of_footnote(self):
        text = "Text[^one].\n\n[^one]: See [link][ref].\n\n    [ref]: /url\n"
        result = create_markdown(plugins=["footnotes"])(text)
        self.assertIn('<a href="/url">link</a>', result)
        self.assertNotIn("[ref]", result)

    def test_existing_document_definition_takes_precedence(self):
        text = "Text[^one].\n\n[ref]: /original\n\n[^one]: See [link][ref].\n\n    [ref]: /replacement\n"
        result = create_markdown(plugins=["footnotes"])(text)
        self.assertIn('<a href="/original">link</a>', result)
        self.assertNotIn("replacement", result)

    def test_missing_reference_stays_literal(self):
        text = "Text[^one].\n\n[^one]: See [link][missing].\n\n    Another paragraph.\n"
        result = create_markdown(plugins=["footnotes"])(text)
        self.assertIn("[link][missing]", result)


@pytest.mark.parametrize("renderer", [None, "html"])
@pytest.mark.parametrize(
    ("definitions", "keys"),
    [
        ("[^one]: First[^two].\n\n[^two]: Second.\n", ["ONE", "TWO"]),
        ("[^one]: First[^two].\n\n[^two]: Second[^three].\n\n[^three]: Third.\n", ["ONE", "TWO", "THREE"]),
        ("[^one]: First[^two][^two].\n\n[^two]: Second[^one].\n", ["ONE", "TWO"]),
    ],
)
def test_nested_footnote_references(renderer, definitions, keys):
    md = create_markdown(renderer=renderer, plugins=["footnotes"])
    result, state = md.parse("Body[^one].\n\n" + definitions + "\n[^unused]: Unused.\n")

    assert state.env["footnotes"] == keys
    if renderer is None:
        items = result[-1]["children"]
        assert isinstance(items, list)
        assert [item["attrs"]["key"] for item in items] == keys
        assert [item["attrs"]["index"] for item in items] == list(range(1, len(keys) + 1))
    else:
        assert result.count('<li id="fn-') == len(keys)
        for index in range(1, len(keys) + 1):
            assert f'<li id="fn-{index}">' in result
        assert "Second" in result
        assert "Unused" not in result


def test_nested_footnotes_preserve_initial_reference_definitions():
    text = (
        "Body[^one][^two].\n\n"
        "[^one]: [link][ref] and [^three].\n\n"
        "[^two]: Second.\n\n    [ref]: /target\n\n"
        "[^three]: Third.\n"
    )
    result = create_markdown(plugins=["footnotes"])(text)
    assert '<a href="/target">link</a>' in result
    assert '<li id="fn-3"><p>Third.' in result
