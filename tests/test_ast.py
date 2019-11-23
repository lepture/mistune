import mistune
from tests import fixtures
from unittest import TestCase


class TestAstRenderer(TestCase):
    @classmethod
    def load_fixtures(cls, case_file):
        cases = fixtures.load_json(case_file)

        def attach_case(n, data):

            def method(self):
                tokens = mistune.markdown(data['text'], renderer='ast')
                self.assertEqual(tokens, data['tokens'])

            name = 'test_{}'.format(n)
            method.__name__ = name
            method.__doc__ = 'Run fixture {} - {}'.format(case_file, n)
            setattr(cls, name, method)

        for n, data in enumerate(cases):
            attach_case(n, data)


TestAstRenderer.load_fixtures('ast.json')
