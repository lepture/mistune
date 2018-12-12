from tests import fixtures
from unittest import TestCase
from mistune.inlines import InlineParser
from mistune.renderers import HTMLRenderer


inline = InlineParser(HTMLRenderer())


class TestInlineParser(TestCase):
    pass


def attach_case(n, text, html):
    def test_fixture(self):
        self.assertEqual(inline(text), html)
    name = 'test_{}'.format(n)
    setattr(TestInlineParser, name, test_fixture)


for n, text, html in fixtures.load('inlines.txt'):
    attach_case(n, text, html)
