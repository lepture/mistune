import os
from mistune import create_markdown
from mistune.directives import (
    RstDirective,
    Admonition,
    TableOfContents,
    Include,
)
from tests import BaseTestCase
from tests.fixtures import ROOT


def load_directive_test(filename, directive):
    class TestDirective(BaseTestCase):
        @staticmethod
        def parse(text):
            md = create_markdown(
                escape=False,
                plugins=[RstDirective([directive])],
            )
            html = md(text)
            return html

    TestDirective.load_fixtures(filename + '.txt')
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test('rst_admonition', Admonition())
load_directive_test('rst_toc', TableOfContents())


class TestCustomizeHeadingToc(BaseTestCase):
    def test_customize_heading_id_func(self):
        def heading_id(token, i):
            return 't-' + str(i + 1)

        toc = TableOfContents(heading_id=heading_id)
        md = create_markdown(
            escape=False,
            plugins=[
                RstDirective([toc]),
            ],
        )
        html = md('# h1\n\n.. toc::\n')
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)



class TestDirectiveInclude(BaseTestCase):
    md = create_markdown(escape=False, plugins=[RstDirective([Include()])])

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
