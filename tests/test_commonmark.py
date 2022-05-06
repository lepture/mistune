import re
import mistune
from tests import BaseTestCase, normalize_html


DIFF_CASES = {
    'setext_headings_093',
    'list_items_300',
}

IGNORE_CASES = {
}

INSANE_CASES = {
}



class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return n in IGNORE_CASES or n in DIFF_CASES or n in INSANE_CASES

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures('commonmark.json')
