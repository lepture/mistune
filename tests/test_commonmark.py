import re
import mistune
from mistune.util import html
from tests import BaseTestCase


DIFF_CASES = {
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


def normalize_html(html):
    html = re.sub(r'\s*\n+\s*', '\n', html)
    html = re.sub(r'>\n', '>', html)
    html = re.sub(r'\n<', '<', html)
    return html


TestCommonMark.load_fixtures('commonmark.json')
