import re
import mistune
from tests import BaseTestCase, normalize_html


DIFF_CASES = {
    'setext_headings_093',
    'list_items_300',

    'links_495',  # return early
    'links_496',
}

IGNORE_CASES = {
    'links_504',  # we don't support link title in (title)
}

INSANE_CASES = {
    'links_511',  # please use escape
    'links_515',  # please see emphasis issues
}



class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return n in IGNORE_CASES or n in DIFF_CASES or n in INSANE_CASES

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures('commonmark.json')
