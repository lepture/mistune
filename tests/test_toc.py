from mistune import Markdown
from mistune.toc import TocRenderer
from tests import fixtures
from unittest import TestCase


def parse(text, escape=False):
    renderer = TocRenderer(escape=escape)
    md = Markdown(renderer)
    html = md(text)
    toc = renderer.render_toc()
    return html, toc


def assert_method(self, name, text, html):
    result = '.\n'.join(parse(text))
    self.assertEqual(result, html)


class TestPluginToc(TestCase):
    pass


fixtures.load_cases(TestPluginToc, assert_method, 'toc.txt')
