from mistune import Markdown, AstRenderer, HTMLRenderer
from mistune.plugins.footnote import footnote
from tests import fixtures
from unittest import TestCase


md = Markdown(renderer=HTMLRenderer(escape=False), plugins=[footnote])


class TestPluginFootnote(TestCase):
    def test_ast_renderer(self):
        md = Markdown(renderer=AstRenderer(), plugins=[footnote])
        data = fixtures.load_json('footnote.json')
        self.assertEqual(md(data['text']), data['tokens'])


def assert_method(self, name, text, html):
    result = md(text)
    self.assertEqual(result, html)


fixtures.load_cases(TestPluginFootnote, assert_method, 'footnote.txt')
