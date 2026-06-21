from unittest import TestCase

from mistune import create_markdown


class TestMathSecurity(TestCase):
    def test_math_plugin_escapes_math_content(self):
        md = create_markdown(escape=True, plugins=["math"])

        inline_html = md("$<script>alert(1)</script>$\n")
        block_html = md("$$\n<script>alert(1)</script>\n$$\n")

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", inline_html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", block_html)
        self.assertNotIn("<script>", inline_html)
        self.assertNotIn("<script>", block_html)
