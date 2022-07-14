import os
from mistune import create_markdown
from mistune.directives import Admonition, DirectiveToc, DirectiveInclude
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

    TestDirective.load_fixtures(filename + '.txt')
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test('directive_admonition', Admonition())


class TestDirectiveToc(BaseTestCase):
    @staticmethod
    def parse(text):
        md = create_markdown(
            escape=False,
            plugins=[DirectiveToc()]
        )
        html = md(text)
        return html

    def test_customize_heading_id_func(self):
        def heading_id(token, i):
            return 't-' + str(i + 1)

        md = create_markdown(
            escape=False,
            plugins=[DirectiveToc(heading_id=heading_id)]
        )
        html = md('# h1\n\n.. toc::\n')
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)


TestDirectiveToc.load_fixtures('directive_toc.txt')


class TestDirectiveInclude(BaseTestCase):
    md = create_markdown(escape=False, plugins=[DirectiveInclude()])

    def test_html_include(self):
        html = self.md.read(os.path.join(ROOT, 'include/text.md'))[0]
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)

    def test_include_missing_source(self):
        s = '.. include:: foo.txt'
        html = self.md(s)
        self.assertIn('Missing source file', html)
