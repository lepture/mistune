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
from mistune3.plugins.speed import speed
from tests import BaseTestCase, fixtures


def load_plugin(plugin_name, plugin_func):
    md1 = create_markdown(escape=False, plugins=[plugin_func])
    md2 = create_markdown(escape=False, plugins=[plugin_func, speed])

    class TestPlugin1(BaseTestCase):
        parse = md1

    class TestPlugin2(BaseTestCase):
        parse = md2

    TestPlugin1.load_fixtures(plugin_name + ".txt")
    TestPlugin2.load_fixtures(plugin_name + ".txt")
    globals()["TestPlugin1_" + plugin_name] = TestPlugin1
    globals()["TestPlugin2_" + plugin_name] = TestPlugin2


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
