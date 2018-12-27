import os
import mistune
from tests import fixtures
from unittest import TestCase


def assert_spec(self, n, text, html):
    result = mistune.html(text)
    self.assertEqual(result, html)


class TestSyntax(TestCase):
    pass


ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, '../syntax.md'), 'rb') as f:
    s = f.read().decode('utf-8')
    fixtures.parse_cases(TestSyntax, assert_spec, s)
