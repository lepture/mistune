from mistune import create_markdown
from mistune.plugins.table import table_in_list, table_in_quote
from mistune.plugins.math import math_in_list, math_in_quote
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
        text = """- Cell | Cell
  ---- | ----
   1  |  2
"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["table", table_in_list])
        self.assertNotIn("<table>", md1(text))
        self.assertIn("<table>", md2(text))

    def test_table_in_quote(self):
        text = """> Cell | Cell
> ---- | ----
>  1  |  2
"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["table", table_in_quote])
        self.assertNotIn("<table>", md1(text))
        self.assertIn("<table>", md2(text))

    def test_math_in_list(self):
        text = """- $$
  foo
  $$
"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["math", math_in_list])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))

    def test_math_in_quote(self):
        text = """> $$
> foo
> $$
"""
        md1 = create_markdown(escape=False)
        md2 = create_markdown(escape=False, plugins=["math", math_in_quote])
        self.assertNotIn('class="math"', md1(text))
        self.assertIn('class="math"', md2(text))


class TestImportPluginSecurity(BaseTestCase):
    """Tests that import_plugin rejects arbitrary module names (CVE fix)."""

    def test_known_plugin_accepted(self):
        from mistune.plugins import import_plugin
        plugin = import_plugin("table")
        self.assertTrue(callable(plugin))

    def test_unknown_plugin_raises(self):
        from mistune.plugins import import_plugin
        with self.assertRaises(ValueError) as ctx:
            import_plugin("os.getcwd")
        self.assertIn("Unknown plugin", str(ctx.exception))

    def test_unknown_plugin_not_cached(self):
        from mistune.plugins import import_plugin, _cached_modules
        evil_name = "subprocess.check_output"
        _cached_modules.pop(evil_name, None)
        with self.assertRaises(ValueError):
            import_plugin(evil_name)
        self.assertNotIn(evil_name, _cached_modules)

    def test_create_markdown_rejects_unknown_plugin(self):
        with self.assertRaises(ValueError):
            create_markdown(plugins=["os.getcwd"])
