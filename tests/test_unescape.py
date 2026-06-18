import mistune
from unittest import TestCase


class TestMiscCases(TestCase):
    def test_unescape_url(self):
        md = mistune.create_markdown()
        result = md('[&quotidian](search?c=x&section=1)')
        expected = '<p><a href="search?c=x&section=1">&quotidian</a></p>'
        self.assertEqual(result.strip().replace('&amp;', '&'), expected)

    def test_unescape_alt(self):
        md = mistune.create_markdown()
        result = md('![&quotidian](quot.png)')
        expected = '<p><img src="quot.png" alt="&quotidian" /></p>'
        self.assertEqual(result.strip().replace('&amp;', '&'), expected)
