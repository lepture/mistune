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

    TestDirective.load_fixtures(filename + ".txt")
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test("rst_admonition", Admonition(), RSTDirective)
load_directive_test("rst_toc", TableOfContents(), RSTDirective)
load_directive_test("fenced_admonition", Admonition(), FencedDirective)
load_directive_test("fenced_toc", TableOfContents(), FencedDirective)
load_directive_test("fenced_image", Image(), FencedDirective)
load_directive_test("fenced_figure", Figure(), FencedDirective)


class CustomizeTableOfContents(TableOfContents):
    def generate_heading_id(self, token, i):
        return "t-" + str(i + 1)


class TestCustomizeToc(BaseTestCase):
    def test_rst_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                RSTDirective([CustomizeTableOfContents()]),
            ],
        )
        html = md("# h1\n\n.. toc::\n")
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)

    def test_fenced_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                FencedDirective([CustomizeTableOfContents()]),
            ],
        )
        html = md("# h1\n\n```{toc}\n```\n")
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)

    def test_colon_fenced_toc(self):
        md = create_markdown(
            escape=False,
            plugins=[
                FencedDirective([CustomizeTableOfContents()], ":"),
            ],
        )
        html = md("# h1\n\n:::{toc}\n:::\n")
        self.assertIn('<h1 id="t-1">h1</h1>', html)
        self.assertIn('<a href="#t-1">h1</a>', html)


class TestFencedDirectiveInList(BaseTestCase):
    md = create_markdown(  # type: ignore[list-item]
        escape=False,
        plugins=[FencedDirective([Admonition()], markers=":")],
    )

    def test_marker_run_below_fence_length_is_not_a_directive(self):
        # A directive needs three or more markers, inside a list item as well
        # as outside one. The list break rules are recompiled per item, and a
        # marker run shorter than the fence must stay literal text.
        for text in (":{note}\nlazy\n", "100. item\n:{note}\nlazy\n"):
            self.assertNotIn("admonition", self.md(text))

        html = self.md("- item\n:{note}\nlazy\n")
        self.assertNotIn("admonition", html)
        self.assertIn(":{note}", html)

    def test_directive_still_breaks_a_list(self):
        html = self.md("- item\n:::{note}\nbody\n:::\n")
        self.assertIn('<section class="admonition note">', html)
        self.assertIn("<p>body</p>", html)


class TestDirectiveInclude(BaseTestCase):
    md = create_markdown(escape=False, plugins=[RSTDirective([Include()])])  # type: ignore[list-item]

    def test_html_include(self):
        html = self.md.read(os.path.join(ROOT, "include/text.md"))[0]
        self.assertIn("Could not include self", html)
        self.assertIn("Could not find file", html)
        self.assertIn("<div>include html</div>", html)
        self.assertIn("<blockquote>", html)
        self.assertIn("Could not include outside source dir", html)

    def test_include_missing_source(self):
        s = ".. include:: foo.txt"
        html = self.md(s)
        self.assertIn("Missing source file", html)


class TestImageDirectiveSrc(BaseTestCase):
    md = create_markdown(escape=False, plugins=[RSTDirective([Image()])])  # type: ignore[list-item]

    def test_harmful_src_blocked(self):
        html = self.md(".. image:: javascript:alert")
        self.assertIn('src="#harmful-link"', html)
        self.assertNotIn("javascript:alert", html)

    def test_safe_src_preserved(self):
        html = self.md(".. image:: cat.png")
        self.assertIn('src="cat.png"', html)

    def test_target_still_filtered(self):
        html = self.md(".. image:: cat.png\n   :target: javascript:alert")
        self.assertNotIn("javascript:alert", html)
