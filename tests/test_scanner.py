import re
from unittest import TestCase
from mistune.scanner import Scanner

class TestScanner(TestCase):
    lexicon = [
        (r'TAG:(\w+)', ("TAG", lambda m, _state: "TAG(%s)" % m.group(1))),
    ]

    @staticmethod
    def parse_text(s, _state):
        return s

    def test_with_capturing_groups(self):
        scanner = Scanner(self.lexicon)
        state = {}
        parsed = list(scanner.iter("tag:foo TAG:bar baz", state, self.parse_text))
        self.assertEqual(parsed, ["tag:foo ", "TAG(bar)", " baz"])

    def test_with_capturing_groups_ci(self):
        # Test with re flags for code coverage
        scanner = Scanner(self.lexicon, re.I)
        state = {}
        parsed = list(scanner.iter("tag:foo TAG:bar baz", state, self.parse_text))
        self.assertEqual(parsed, ["TAG(foo)", " ", "TAG(bar)", " baz"])
