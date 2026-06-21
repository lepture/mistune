import platform
import time
from unittest import TestCase

from mistune import create_markdown

IS_PYPY = platform.python_implementation() == "PyPy"


class TestRefLinkSecurity(TestCase):
    def test_many_reference_links_return_quickly(self):
        repetitions = 500 if IS_PYPY else 3000
        deadline = 1.0 if IS_PYPY else 0.5

        text = "".join("[a{}]: u\n".format(i) for i in range(repetitions))

        start = time.monotonic()
        create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, deadline)
