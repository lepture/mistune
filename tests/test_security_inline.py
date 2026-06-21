import time
from unittest import TestCase

from mistune import create_markdown


class TestInlineParserSecurity(TestCase):
    def test_link_title_redos_payload_returns_quickly(self):
        md = create_markdown()
        payload = '[x](y "' + "\\!" * 24 + ")"

        start = time.monotonic()
        html = md(payload)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 0.5)
        self.assertIn("[x](y", html)

    def test_nested_bracket_link_input_does_not_recurse_forever(self):
        text = "[" * 200 + "x" + "]" * 200

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 0.5)
        self.assertIn("[", html)

    def test_unmatched_bracket_input_returns_quickly(self):
        text = "[" * 4000

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 0.5)
        self.assertIn("[", html)
