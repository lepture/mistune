import os
from mistune import create_markdown
from mistune.directives import (
    RSTDirective,
    FencedDirective,
    Admonition,
    TableOfContents,
    Include,
    Image,
    Figure,
)
from tests import BaseTestCase
from tests.fixtures import ROOT


def load_directive_test(filename, directive, cls):
    class TestDirective(BaseTestCase):
        @staticmethod
        def parse(text):
            md = create_markdown(
                escape=False,
                plugins=[cls([directive])],
            )
            html = md(text)
            return html

    TestDirective.load_fixtures(filename + '.txt')
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test('rst_admonition', Admonition(), RSTDirective)
load_directive_test('rst_toc', TableOfContents(), RSTDirective)
load_directive_test('fenced_admonition', Admonition(), FencedDirective)
load_directive_test('fenced_toc', TableOfContents(), FencedDirective)
load_directive_test('fenced_image', Image(), FencedDirective)
load_directive_test('fenced_figure', Figure(), FencedDirective)


class CustomizeTableOfContents(TableOfContents):
    def generate_heading_id(self, token, i):
        return 't-' + str(i + 1)


class TestCustomizeToc(BaseTestCase):
    def test_rst_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                RSTDirective([CustomizeTableOfContents()]),
            ],
        )
        html = md('# h1\n\n.. toc::\n')
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)

    def test_fenced_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                FencedDirective([CustomizeTableOfContents()]),
            ],
        )
        html = md('# h1\n\n```{toc}\n```\n')
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)

    def test_colon_fenced_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                FencedDirective([CustomizeTableOfContents()], ':'),
            ],
        )
        html = md('# h1\n\n:::{toc}\n:::\n')
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)


class TestDirectiveInclude(BaseTestCase):
    md = create_markdown(escape=False, plugins=[RSTDirective([Include()])])  # type: ignore[list-item]

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
