import argparse
import io
import os
import sys
import tempfile
from unittest import TestCase
from unittest.mock import patch

from mistune.__main__ import _output


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
