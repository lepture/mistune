from mistune import create_markdown
from mistune.plugins.url import url
from mistune.plugins.formatting import strikethrough, mark, insert, subscript
from mistune.plugins.task_lists import task_lists
from mistune.plugins.table import table
from mistune.plugins.footnotes import footnotes
from mistune.plugins.def_list import def_list
from mistune.plugins.abbr import abbr
from mistune.plugins.math import math
from mistune.plugins.ruby import ruby
from tests import BaseTestCase, fixtures


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
load_plugin("subscript")
load_plugin("task_lists")
load_plugin("table")
load_plugin("def_list")
load_plugin("footnotes")
load_plugin("abbr")
load_plugin("math")
load_plugin("ruby")
