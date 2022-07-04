from mistune3 import create_markdown
from mistune3.directives import DirectiveToc
from tests import BaseTestCase


class TestPluginToc(BaseTestCase):
    @staticmethod
    def parse(text):
        md = create_markdown(
            escape=False,
            plugins=[DirectiveToc()]
        )
        html = md(text)
        return html

    def assert_case(self, name, text, html):
        result = self.parse(text)
        self.assertEqual(result, html)

TestPluginToc.load_fixtures('toc.txt')
