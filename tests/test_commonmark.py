import mistune
from tests import BaseTestCase, normalize_html


class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return False

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures("commonmark.json")
