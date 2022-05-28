import re
import mistune3 as mistune
from tests import BaseTestCase, normalize_html


DIFF_CASES = {
    'setext_headings_093',
    'html_blocks_191',  # mistune keeps \n

    'images_573', # image can not be in image

    'links_517',  # aggressive link group
    'links_518',
    'links_519',
    'links_520',
    'links_531',
    'links_533',
    'links_563',
}

IGNORE_CASES = {
    'lists_313',  # TODO: need to fix this case

    'code_spans_341',  # no higher precedence
    'code_spans_342',

    'links_496',  # we don't support link title in (title)
    'links_504',

    'links_515',  # please see emphasis issues
    'links_529',
    'links_532',
}


class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return n in IGNORE_CASES or n in DIFF_CASES

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures('commonmark.json')
