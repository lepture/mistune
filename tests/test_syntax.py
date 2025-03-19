import mistune
from tests import BaseTestCase, normalize_html


class TestSyntax(BaseTestCase):
    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestSyntax.load_fixtures("fix-commonmark.txt")
TestSyntax.load_fixtures("diff-commonmark.txt")
