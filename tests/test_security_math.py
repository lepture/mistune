from unittest import TestCase

from mistune import create_markdown
from tests.perf_utils import assert_near_linear


class TestMathSecurity(TestCase):
    def test_math_plugin_escapes_math_content(self):
        md = create_markdown(escape=True, plugins=["math"])

        inline_html = md("$<script>alert(1)</script>$\n")
        block_html = md("$$\n<script>alert(1)</script>\n$$\n")

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", inline_html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", block_html)
        self.assertNotIn("<script>", inline_html)
        self.assertNotIn("<script>", block_html)

    def test_math_plugin_escapes_content_when_raw_html_is_enabled(self):
        md = create_markdown(escape=False, plugins=["math"])

        self.assertIn("&lt;marker&gt;", md("$<marker>$\n"))

    def test_repeated_inline_math_openers_are_near_linear(self):
        md = create_markdown(plugins=["math"])

        def render(size):
            return md("$a " * size + "\n")

        _small, html = assert_near_linear(self, render, 1000, 2000)
        self.assertIn('<span class="math">', html)
