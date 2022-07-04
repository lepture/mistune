import os
from mistune3 import create_markdown
from mistune3.directives import Admonition, DirectiveToc, DirectiveInclude
from tests import BaseTestCase
from tests.fixtures import ROOT


def load_directive_test(filename, directive):
    class TestDirective(BaseTestCase):
        @staticmethod
        def parse(text):
            md = create_markdown(
                escape=False,
                plugins=[directive]
            )
            html = md(text)
            return html

        def assert_case(self, name, text, html):
            result = self.parse(text)
            self.assertEqual(result, html)

    TestDirective.load_fixtures(filename + '.txt')
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test('directive_toc', DirectiveToc())
load_directive_test('directive_admonition', Admonition())


class TestDirectiveInclude(BaseTestCase):
    md = create_markdown(escape=False, plugins=[DirectiveInclude()])

    def test_html_include(self):
        html = self.md.read(os.path.join(ROOT, 'include/text.md'))
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)

    def test_include_missing_source(self):
        s = '.. include:: foo.txt'
        html = self.md(s)
        self.assertIn('Missing source file', html)
