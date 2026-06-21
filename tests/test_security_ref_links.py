import time
from unittest import TestCase

from mistune import create_markdown


class TestRefLinkSecurity(TestCase):
    def test_many_reference_links_return_quickly(self):
        text = "".join("[a{}]: u\n".format(i) for i in range(3000))

        start = time.monotonic()
        create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, 0.5)
