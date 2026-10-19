from unittest import TestCase

from mistune import create_markdown
from tests.perf_utils import assert_near_linear


class TestEdgeCaseSecurity(TestCase):
    def test_blank_list_continuations_are_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("- first\n" + "\n" * size + "  last\n")

        _small, html = assert_near_linear(self, render, 2000, 4000)
        self.assertIn("last", html)

    def test_dense_emphasis_is_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("*a" * size + "\n")

        _small, html = assert_near_linear(self, render, 4000, 8000, warmup_size=1000)
        self.assertIn("<em>", html)

    def test_dense_emphasis_preserves_adjacent_tokens(self):
        md = create_markdown()
        self.assertEqual(
            md("*a" * 6 + "\n"),
            "<p><em>a</em>a<em>a</em>a<em>a</em>a</p>\n",
        )

    def test_mixed_emphasis_delimiters_are_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("*a_b" * size)

        _small, html = assert_near_linear(self, render, 2000, 4000, warmup_size=500)
        self.assertIn("a_b", html)

    def test_malformed_images_are_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("![" * size + "x" + "]" * size)

        _small, html = assert_near_linear(self, render, 2000, 4000, warmup_size=500)
        self.assertIn("![", html)

    def test_unclosed_link_destinations_are_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("[](" * size)

        _small, html = assert_near_linear(self, render, 2000, 4000, warmup_size=500)
        self.assertIn("[](", html)

    def test_failed_parent_destination_does_not_hide_nested_images(self):
        md = create_markdown()
        self.assertEqual(
            md("[](foo( [outer ![inner](url)](/outer)"),
            '<p>[](foo( <a href="/outer">outer <img src="url" alt="inner" /></a></p>\n',
        )

    def test_failed_angle_destination_does_not_hide_later_links(self):
        md = create_markdown()
        self.assertEqual(
            md("[]( <foo [bar](/url)"),
            '<p>[]( &lt;foo <a href="/url">bar</a></p>\n',
        )
