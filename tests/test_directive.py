import os
import json
from mistune import Markdown, AstRenderer, HTMLRenderer
from mistune.plugins import PluginDirective
from tests import fixtures
from tests.fixtures import ROOT
from unittest import TestCase


md = Markdown(renderer=HTMLRenderer(escape=False))
md.use(PluginDirective())


class TestPluginDirective(TestCase):
    def test_html_include(self):
        html = md.read(os.path.join(ROOT, 'include/text.md'))
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)

    def test_include_missing_source(self):
        s = '.. include:: foo.txt'
        html = md(s)
        self.assertIn('Missing source file', html)

    def test_ast_include(self):
        filepath = os.path.join(ROOT, 'include/foo.txt')
        md = Markdown(renderer=AstRenderer())
        md.use(PluginDirective())
        s = '.. include:: hello.txt'
        tokens = md.parse(s, {'__file__': filepath})
        token = tokens[0]
        self.assertEqual(token['type'], 'include')
        self.assertEqual(token['text'], 'hello\n')
        self.assertEqual(token['relpath'], 'hello.txt')

    def test_warn_admonition(self):
        s = '.. warn:: Warnning\n\n   message'
        html = md(s)
        self.assertIn('class="admonition warn"', html)
        self.assertIn('<h1>Warnning</h1>', html)

    def test_ast_directive(self):
        data = fixtures.load_json('directive.json')
        md = Markdown(renderer=AstRenderer())
        md.use(PluginDirective())
        # Use JSON to fix the differences between tuple and list
        tokens = json.loads(json.dumps(md(data['text'])))
        self.assertEqual(tokens, data['tokens'])

    def test_not_supported_directive(self):
        s = '.. name::\n   :k1: v1\n   :k2:v2\n\n   message'
        html = md(s)
        self.assertIn('not supported yet -->', html)

    def test_register_renderer(self):
        def _render_pre(text, value, options):
            return '<pre></pre>'

        pd = PluginDirective()
        pd.register_html_renderer('pre', _render_pre)
        md = Markdown(renderer=HTMLRenderer(escape=False))
        md.use(pd)
        html = md('.. pre::\n   :k1: v1\n')
        self.assertEqual(html, '<pre></pre>')
