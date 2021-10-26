from tests import fixtures
from unittest import TestCase


class BaseTestCase(TestCase):
    @classmethod
    def load_fixtures(cls, case_file):
        def attach_case(n, text, html):
            def method(self):
                self.assert_case(n, text, html)

            name = 'test_{}'.format(n)
            method.__name__ = name
            method.__doc__ = 'Run fixture {} - {}'.format(case_file, n)
            setattr(cls, name, method)

        for n, text, html in fixtures.load_examples(case_file):
            if cls.ignore_case(n):
                continue
            attach_case(n, text, html)

    @classmethod
    def ignore_case(cls, name):
        return False

    def assert_case(self, name, text, html):
        result = self.md(text)
        try:
            self.assertEqual(result.strip(), html.strip())
        except AssertionError as ae:
            #import pdb ; pdb.set_trace()
            print(f"\n\nFailed to match case {name}\n\n--------------\nResult:\n{result}\n\nExpected:\n{html.strip()}\n--------------")
            raise
