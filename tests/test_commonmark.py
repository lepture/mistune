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
    'code_spans_341',  # no higher precedence
    'code_spans_342',

    'links_496',  # we don't support link title in (title)
    'links_504',

    'links_515',  # please see emphasis issues
    'links_529',
    'links_532',

    # ignore emphasis cases for now
    'emphasis_and_strong_emphasis_352',
    'emphasis_and_strong_emphasis_367',
    'emphasis_and_strong_emphasis_368',
    'emphasis_and_strong_emphasis_372',
    'emphasis_and_strong_emphasis_379',
    'emphasis_and_strong_emphasis_388',
    'emphasis_and_strong_emphasis_391',
    'emphasis_and_strong_emphasis_392',

    'emphasis_and_strong_emphasis_424',
    'emphasis_and_strong_emphasis_425',
    'emphasis_and_strong_emphasis_426',
    'emphasis_and_strong_emphasis_429',
    'emphasis_and_strong_emphasis_430',
    'emphasis_and_strong_emphasis_431',
    'emphasis_and_strong_emphasis_436',
    'emphasis_and_strong_emphasis_439',
    'emphasis_and_strong_emphasis_441',
    'emphasis_and_strong_emphasis_443',
    'emphasis_and_strong_emphasis_444',
    'emphasis_and_strong_emphasis_448',
    'emphasis_and_strong_emphasis_451',
    'emphasis_and_strong_emphasis_460',
    'emphasis_and_strong_emphasis_477',
    'emphasis_and_strong_emphasis_478',
}

for i in range(406, 419):
    IGNORE_CASES.add('emphasis_and_strong_emphasis_' + str(i))
for i in range(453, 459):
    IGNORE_CASES.add('emphasis_and_strong_emphasis_' + str(i))
for i in range(462, 468):
    IGNORE_CASES.add('emphasis_and_strong_emphasis_' + str(i))
for i in range(470, 474):
    IGNORE_CASES.add('emphasis_and_strong_emphasis_' + str(i))


class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return n in IGNORE_CASES or n in DIFF_CASES

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures('commonmark.json')
