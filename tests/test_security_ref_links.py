from unittest import TestCase

from mistune import create_markdown
from tests.perf_utils import assert_near_linear


class TestRefLinkSecurity(TestCase):
    def test_many_reference_links_return_quickly(self):
        md = create_markdown()

        def render(size):
            return md("".join("[a{}]: u\n".format(i) for i in range(size)))

        _small, html = assert_near_linear(self, render, 1500, 3000)
        self.assertEqual(html, "")
