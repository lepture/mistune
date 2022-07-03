from mistune3 import create_markdown
from mistune3.plugins.url import url
from mistune3.plugins.formatting import strikethrough, mark, insert, subscript
from mistune3.plugins.task_lists import task_lists
from mistune3.plugins.table import table
from mistune3.plugins.footnotes import footnotes
from mistune3.plugins.def_list import def_list
from mistune3.plugins.abbr import abbr
from mistune3.plugins.math import math
from mistune3.plugins.ruby import ruby
from mistune3.directives import Admonition
from tests import BaseTestCase, fixtures


def load_plugin(plugin_name, plugin_func, test_ast=False):

    class TestPlugin(BaseTestCase):
        md = create_markdown(escape=False, plugins=[plugin_func])

    def test_ast_renderer(self):
        md = create_markdown(escape=False, plugins=[plugin_func], renderer=None)
        data = fixtures.load_ast(plugin_name + ".json")
        self.assertEqual(md(data["text"]), data["tokens"])

    if test_ast:
        test_ast_renderer.__doc__ = "Run {} ast renderer".format(plugin_name)
        setattr(TestPlugin, "test_ast_renderer", test_ast_renderer)

    TestPlugin.load_fixtures(plugin_name + ".txt")
    globals()["TestPlugin_" + plugin_name] = TestPlugin


load_plugin("url", url)
load_plugin("strikethrough", strikethrough)
load_plugin("mark", mark)
load_plugin("insert", insert)
load_plugin("subscript", subscript)
load_plugin("task_lists", task_lists)
load_plugin("table", table)
load_plugin("def_list", def_list)
load_plugin("footnotes", footnotes)
load_plugin("abbr", abbr)
load_plugin("math", math)
load_plugin("ruby", ruby)
load_plugin("admonition", Admonition())
