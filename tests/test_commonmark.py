import re
import mistune
import fixtures
from unittest import TestCase


IGNORE_CASES = {
    'setext_headings_02',  # we only allow one line title
    'setext_headings_15',

    'setext_headings_03',  # must start with 2 = or -
    'setext_headings_07',  # ignore
    'setext_headings_13',  # ignore

    'html_blocks_39',  # ignore
    'link_reference_definitions_19',  # weird rule

    'block_quotes_08',  # we treat it different

    'list_items_05',  # I don't agree
    'list_items_24',
    'list_items_28',
    'list_items_39',  # no lazy
    'list_items_40',
    'list_items_41',

    'lists_05',  # ordered list must start with newlines
    'lists_07',  # we use simple way to detect tight list
    'lists_16',
    'lists_17',
    'lists_18',
    'lists_19',

    'block_quotes_05',  # we don't allow lazy continuation
    'block_quotes_06',
    'block_quotes_11',
    'block_quotes_20',
    'block_quotes_23',
    'block_quotes_24',  # this test case shows why lazy is not good
}
INSANE_CASES = {
    'fenced_code_blocks_13',
    'fenced_code_blocks_15',
    'list_items_33',
    'list_items_38',

    'link_reference_definitions_02',  # only allow one line definition
    'link_reference_definitions_03',
    'link_reference_definitions_04',
    'link_reference_definitions_05',
    'link_reference_definitions_07',
    'link_reference_definitions_21',
}

DIFFERENCES = {
    'tabs_05': lambda s: s.replace('<code>  ', '<code>'),
    'tabs_06': lambda s: s.replace('<code>  ', '<code>'),
    'tabs_07': lambda s: s.replace('<code>  ', '<code>'),
}


class TestCommonMark(TestCase):
    pass


def attach_case(n, text, html):
    def test_spec(self):
        print(text)
        result = mistune.html(text)
        # normalize to match commonmark
        result = re.sub(r'\n+\s*', '\n', result)
        result = re.sub(r'>\n', '>', result)
        result = re.sub(r'\n<', '<', result)
        expect = re.sub(r'\n+\s*', '\n', html)
        expect = re.sub(r'>\n', '>', expect)
        expect = re.sub(r'\n<', '<', expect)
        if n in DIFFERENCES:
            expect = DIFFERENCES[n](expect)
        self.assertEqual(result, expect)

    name = 'test_{}'.format(n)
    setattr(TestCommonMark, name, test_spec)


for n, text, html in fixtures.load('commonmark.txt'):
    if n not in IGNORE_CASES and n not in INSANE_CASES:
        attach_case(n, text, html)
