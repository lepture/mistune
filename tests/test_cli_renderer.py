"""Tests for CLI renderer-aware default plugins (issue #530)."""

import io
import sys
from contextlib import redirect_stdout
from unittest import TestCase
from unittest.mock import patch

from mistune.__main__ import cli


def _run(args: list[str]) -> str:
    with patch.object(sys, "argv", ["python -m mistune"] + args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli()
    return buf.getvalue()


class TestCliRendererPlugins(TestCase):
    """Default plugins must match what each renderer can handle (issue #530)."""

    def test_markdown_renderer_with_footnote_does_not_crash(self):
        text = "hello[^1] world\n\n[^1]: note\n"
        # Must not raise AttributeError for footnote_ref
        result = _run(["-r", "markdown", "-m", text])
        self.assertIn("hello", result)

    def test_rst_renderer_with_footnote_does_not_crash(self):
        text = "x [^1]\n\n[^1]: note\n"
        result = _run(["-r", "rst", "-m", text])
        self.assertIn("x", result)

    def test_rst_renderer_with_table_does_not_crash(self):
        text = "| A | B |\n| - | - |\n| 1 | 2 |\n"
        result = _run(["-r", "rst", "-m", text])
        self.assertIsInstance(result, str)

    def test_markdown_renderer_with_table_still_works(self):
        text = "| A | B |\n| - | - |\n| 1 | 2 |\n"
        result = _run(["-r", "markdown", "-m", text])
        self.assertIn("A", result)
        self.assertIn("B", result)

    def test_html_renderer_still_uses_all_plugins(self):
        # footnotes must still work for the default html renderer
        text = "hello[^1] world\n\n[^1]: a note\n"
        result = _run(["-m", text])
        self.assertIn("footnote", result.lower())

    def test_explicit_plugin_overrides_defaults(self):
        # passing --plugin explicitly still works for any renderer
        text = "| A | B |\n| - | - |\n| 1 | 2 |\n"
        result = _run(["-r", "markdown", "-p", "table", "-m", text])
        self.assertIn("A", result)
