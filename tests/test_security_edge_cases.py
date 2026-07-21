import time
from unittest import TestCase

from mistune import create_markdown


class TestEdgeCaseSecurity(TestCase):
    def test_blank_list_continuations_are_near_linear(self):
        md = create_markdown()

        def render(size):
            text = "- first\n" + "\n" * size + "  last\n"
            started = time.perf_counter()
            md(text)
            return time.perf_counter() - started

        render(500)
        small = render(2000)
        large = render(8000)

        self.assertLess(large, small * 8 + 0.02)

    def test_dense_emphasis_is_near_linear(self):
        md = create_markdown()

        def render(size):
            started = time.perf_counter()
            md("*a" * size + "\n")
            return time.perf_counter() - started

        render(1000)
        small = render(4000)
        large = render(8000)

        self.assertLess(large, small * 3.5 + 0.02)

    def test_dense_emphasis_preserves_adjacent_tokens(self):
        md = create_markdown()
        self.assertEqual(
            md("*a" * 6 + "\n"),
            "<p><em>a</em>a<em>a</em>a<em>a</em>a</p>\n",
        )
