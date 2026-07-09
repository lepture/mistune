import platform
import time
from unittest import TestCase

from mistune import create_markdown


IS_PYPY = platform.python_implementation() == "PyPy"


class TestFormattingSecurity(TestCase):
    def test_repeated_formatting_pairs_render_as_adjacent_spans(self):
        md = create_markdown(plugins=["strikethrough"])
        result = md("~~x~~" * 3)
        self.assertEqual(result.strip(), "<p><del>x</del><del>x</del><del>x</del></p>")

    def test_repeated_formatting_pairs_return_quickly(self):
        cases = [
            ("strikethrough", "~~x~~"),
            ("mark", "==x=="),
            ("insert", "^^x^^"),
        ]
        for plugin, unit in cases:
            with self.subTest(plugin=plugin):
                md = create_markdown(plugins=[plugin])
                md(unit)

                repetitions = 500 if IS_PYPY else 3000
                deadline = 1.0 if IS_PYPY else 0.5
                text = unit * repetitions

                start = time.monotonic()
                md(text)
                elapsed = time.monotonic() - start

                self.assertLess(elapsed, deadline)

    def test_repeated_unclosed_formatting_markers_are_near_linear(self):
        cases = [
            ("strikethrough", "~~a "),
            ("mark", "==a "),
            ("insert", "^^a "),
        ]
        for plugin, unit in cases:
            with self.subTest(plugin=plugin):
                md = create_markdown(plugins=[plugin])

                def render(size):
                    start = time.process_time()
                    md(unit * size + "\n")
                    return time.process_time() - start

                render(200)
                small = render(1000)
                large = render(2000)

                self.assertLess(large, 1.0 if IS_PYPY else 0.5)
                self.assertLess(large, small * 3)
