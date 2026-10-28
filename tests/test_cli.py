import io
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

from mistune.__main__ import cli
from tests import BaseTestCase


class TestCliMessage(BaseTestCase):
    def parse(self, text: str) -> str:
        with patch.object(sys, "argv", ["python -m mistune", "-m", text]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli()
        output = buf.getvalue()
        if output.endswith("\n"):
            output = output[:-1]
        return output


TestCliMessage.load_fixtures("cli.txt")


class TestCliNonHtmlRenderer(BaseTestCase):
    """The documented ``-r markdown`` / ``-r rst`` commands must not crash on
    documents containing footnotes (``markdown``) or footnotes and tables
    (``rst``), because neither renderer provides the render methods for the
    footnote (and, for rst, table) tokens of the CLI default plugins."""

    def render_with(self, *argv: str) -> str:
        with patch.object(sys, "argv", ["python -m mistune", *argv]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli()
        output = buf.getvalue()
        if output.endswith("\n"):
            output = output[:-1]
        return output

    def test_markdown_renderer_with_footnote(self):
        # would previously raise: AttributeError No renderer "'footnote_ref'"
        out = self.render_with(
            "-r", "markdown",
            "-m", "hello[^1] world\n\n[^1]: note\n",
        )
        self.assertIn("[^1]", out)

    def test_rst_renderer_with_table_and_footnote(self):
        # would previously raise: AttributeError No renderer "'table'"
        out = self.render_with(
            "-r", "rst",
            "-m", "| A | B |\n| - | - |\n| 1 | 2 |\n\nfoot[^2]\n\n[^2]: note\n",
        )
        self.assertIn("|", out)
        self.assertIn("^2", out)

    def test_default_html_plugins_unchanged(self):
        out = self.render_with(
            "-m", "a ~~b~~ c\n\nfoot[^1]\n\n[^1]: note\n",
        )
        self.assertIn("<del>b</del>", out)
        self.assertIn('class="footnote-ref"', out)
