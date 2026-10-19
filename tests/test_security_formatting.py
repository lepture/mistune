from unittest import TestCase

from mistune import create_markdown
from tests.perf_utils import assert_near_linear


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
                def render(size):
                    return md(unit * size)

                _small, html = assert_near_linear(self, render, 1500, 3000)
                self.assertEqual(html.count("</"), 3001)

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
                    return md(unit * size + "\n")

                _small, html = assert_near_linear(self, render, 1000, 2000)
                self.assertIn(unit.strip(), html)
