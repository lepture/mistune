import platform
import time
from unittest import TestCase

from mistune import create_markdown

IS_PYPY = platform.python_implementation() == "PyPy"
DEADLINE = 1.0 if IS_PYPY else 0.5


class TestInlineParserSecurity(TestCase):
    def test_link_title_redos_payload_returns_quickly(self):
        md = create_markdown()
        payload = '[x](y "' + "\\!" * 24 + ")"

        start = time.monotonic()
        html = md(payload)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[x](y", html)

    def test_nested_bracket_link_input_does_not_recurse_forever(self):
        text = "[" * 8000 + "x" + "]" * 8000

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[", html)

    def test_failed_outer_bracket_preserves_nested_link(self):
        html = create_markdown()("[[x](https://example.com)]")

        self.assertEqual('<p>[<a href="https://example.com">x</a>]</p>\n', html)

    def test_failed_reference_after_nested_brackets_returns_quickly(self):
        text = "[" * 8000 + "x" + "]" * 8000 + "[missing]"

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[missing]", html)

    def test_failed_reference_does_not_hide_following_inline_link(self):
        html = create_markdown()("[foo][bar](https://example.com)")

        self.assertEqual('<p>[foo]<a href="https://example.com">bar</a></p>\n', html)

    def test_unmatched_bracket_input_returns_quickly(self):
        text = "[" * 4000

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[", html)
