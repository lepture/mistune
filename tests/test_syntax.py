import mistune
from tests import BaseTestCase


class TestSyntax(BaseTestCase):
    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(result, html)


TestSyntax.load_fixtures('fix-commonmark.txt')
# TestSyntax.load_fixtures('diff-commonmark.txt')
