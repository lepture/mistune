import os
from mistune import create_markdown
from mistune.directives import DirectiveInclude
from tests.fixtures import ROOT
from unittest import TestCase


class TestPluginDirective(TestCase):
    def test_html_include(self):
        md = create_markdown(
            escape=False,
            plugins=[DirectiveInclude()]
        )
        html = md.read(os.path.join(ROOT, 'include/text.md'))
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)

    def test_include_missing_source(self):
        md = create_markdown(plugins=[DirectiveInclude()])
        s = '.. include:: foo.txt'
        html = md(s)
        self.assertIn('Missing source file', html)

    def test_ast_include(self):
        md = create_markdown(
            renderer='ast',
            plugins=[DirectiveInclude()]
        )
        filepath = os.path.join(ROOT, 'include/foo.txt')
        s = '.. include:: hello.txt'
        tokens = md.parse(s, {'__file__': filepath})
        token = tokens[0]
        self.assertEqual(token['type'], 'include')
        self.assertEqual(token['text'], 'hello\n')
        self.assertEqual(token['relpath'], 'hello.txt')
