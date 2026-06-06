import argparse
import io
import os
import sys
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from mistune.__main__ import _output, cli


class TestCLI(TestCase):
    def test_output_file_is_utf8(self):
        # The rendered output must be written as UTF-8 regardless of the
        # platform default encoding (e.g. cp1251 on some Windows locales),
        # otherwise non-Latin characters such as "★" (U+2605) raise
        # UnicodeEncodeError. Regression test for issue #379.
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        try:
            _output("<p>star ★</p>", argparse.Namespace(output=path))
            with open(path, encoding="utf-8") as f:
                self.assertIn("★", f.read())
        finally:
            os.remove(path)

    def test_output_stdout_keeps_unicode(self):
        # The default (no -o) path prints to stdout; non-Latin characters
        # must survive. Regression test for issue #379.
        buffer = io.StringIO()
        with patch.object(sys, "stdout", buffer):
            _output("<p>star ★</p>", argparse.Namespace(output=None))
        self.assertIn("★", buffer.getvalue())

    def test_cli_reconfigures_streams_to_utf8(self):
        # cli() must switch the standard streams to UTF-8 so that reading or
        # printing non-Latin characters does not raise on platforms whose
        # default encoding is not UTF-8 (e.g. cp1251). Regression test for #379.
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        with patch.object(sys, "argv", ["mistune", "-m", "Hi ★"]), patch.object(
            sys, "stdin", mock_stdin
        ), patch.object(sys, "stdout", mock_stdout), patch.object(
            sys, "stderr", mock_stderr
        ):
            cli()
        for stream in (mock_stdin, mock_stdout, mock_stderr):
            stream.reconfigure.assert_called_once_with(encoding="utf-8")

    def test_cli_tolerates_reconfigure_failure(self):
        # A detached or already-closed stream may raise when reconfigured; cli()
        # must swallow that and keep working instead of crashing.
        mock_stdout = MagicMock()
        mock_stdout.reconfigure.side_effect = ValueError("stream is detached")
        with patch.object(sys, "argv", ["mistune", "-m", "Hi ★"]), patch.object(
            sys, "stdin", MagicMock()
        ), patch.object(sys, "stdout", mock_stdout), patch.object(
            sys, "stderr", MagicMock()
        ):
            cli()  # must not raise
        mock_stdout.write.assert_called()

    def test_cli_skips_streams_without_reconfigure(self):
        # io.StringIO has no reconfigure(); cli() must skip it and still render.
        buffer = io.StringIO()
        with patch.object(sys, "argv", ["mistune", "-m", "Hi ★"]), patch.object(
            sys, "stdin", io.StringIO()
        ), patch.object(sys, "stdout", buffer), patch.object(
            sys, "stderr", io.StringIO()
        ):
            cli()
        self.assertIn("★", buffer.getvalue())
