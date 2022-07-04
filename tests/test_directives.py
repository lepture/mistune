from mistune3 import create_markdown
from mistune3.directives import Admonition, DirectiveToc
from tests import BaseTestCase


def load_directive_test(filename, directive):
    class TestDirective(BaseTestCase):
        @staticmethod
        def parse(text):
            md = create_markdown(
                escape=False,
                plugins=[directive]
            )
            html = md(text)
            return html

        def assert_case(self, name, text, html):
            result = self.parse(text)
            self.assertEqual(result, html)

    TestDirective.load_fixtures(filename + '.txt')
    globals()["TestDirective_" + filename] = TestDirective


load_directive_test('directive_toc', DirectiveToc())
load_directive_test('directive_admonition', Admonition())
