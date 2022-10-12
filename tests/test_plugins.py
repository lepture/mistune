from mistune import create_markdown
from mistune.plugins.table import table_in_list, table_in_quote
from mistune.plugins.math import math_in_list, math_in_quote
from tests import BaseTestCase


def load_plugin(plugin_name):
    md1 = create_markdown(escape=False, plugins=[plugin_name])
    md2 = create_markdown(escape=False, plugins=[plugin_name, 'speedup'])

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
        text = '''- Cell | Cell\n  ---- | ----\n   1  |  2\n'''
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=['table', table_in_list])
        self.assertNotIn('<table>', md1(text))
        self.assertIn('<table>', md2(text))

    def test_table_in_quote(self):
        text = '''> Cell | Cell\n> ---- | ----\n>  1  |  2\n'''
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=['table', table_in_quote])
        self.assertNotIn('<table>', md1(text))
        self.assertIn('<table>', md2(text))

    def test_math_in_list(self):
        text = '''- $$\n  foo\n  $$\n'''
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=['math', math_in_list])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))

    def test_math_in_quote(self):
        text = '''> $$\n> foo\n> $$\n'''
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=['math', math_in_quote])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))
