import mistune
from tests import BaseTestCase


class TestSyntax(BaseTestCase):
    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(result, html)


TestSyntax.load_fixtures('syntax.md')
TestSyntax.load_fixtures('non-commonmark.txt')
