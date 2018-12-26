import os
from mistune import Markdown, AstRenderer, HTMLRenderer
from mistune.plugins.directive import Directive
from tests.fixtures import ROOT
from unittest import TestCase


md = Markdown(renderer=HTMLRenderer(escape=False))
md.use(Directive())


class TestPluginDirective(TestCase):
    def test_include(self):
        html = md.read(os.path.join(ROOT, 'include/text.md'))
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)

    def test_warn_admonition(self):
        s = '.. warn:: Warnning\n\n   message'
        html = md(s)
        self.assertIn('class="admonition warn"', html)
        self.assertIn('<h1>Warnning</h1>', html)

    def test_ast_directive(self):
        s = '.. name::\n   :k1: v1\n   :k2:v2'
        md = Markdown(renderer=AstRenderer())
        md.use(Directive())
        token = md(s)
        tok = token[0]
        self.assertEqual(tok['type'], 'directive')
        self.assertEqual(tok['name'], 'name')

        options = tok['options']
        self.assertEqual(dict(options), {'k1': 'v1', 'k2': 'v2'})

    def test_not_supported_directive(self):
        s = '.. name::\n   :k1: v1\n   :k2:v2\n\n   message'
        html = md(s)
        self.assertIn('not supported yet -->', html)
