import time
from unittest import TestCase

from mistune import create_markdown


class TestFormattingSecurity(TestCase):
    def test_repeated_formatting_pairs_return_quickly(self):
        cases = [
            ("strikethrough", "~~x~~"),
            ("mark", "==x=="),
            ("insert", "^^x^^"),
        ]
        for plugin, unit in cases:
            md = create_markdown(plugins=[plugin])
            text = unit * 3000

            start = time.monotonic()
            md(text)
            elapsed = time.monotonic() - start

            self.assertLess(elapsed, 0.5, plugin)
