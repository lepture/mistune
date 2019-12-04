from mistune import create_markdown
from mistune.directives import DirectiveToc
from mistune.directives.toc import render_toc_ul, extract_toc_items
from tests import BaseTestCase, fixtures


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


class TestPluginTocAst(BaseTestCase):
    def test_render_toc_ul(self):
        result = render_toc_ul(None)
        self.assertEqual(result, '')

    def test_extract_toc_items(self):
        md = create_markdown(
            renderer='ast',
            plugins=[DirectiveToc()]
        )
        self.assertEqual(extract_toc_items(md, ''), [])
        s = '# H1\n## H2\n# H1'
        result = extract_toc_items(md, s)
        expected = [
            ('toc_1', 'H1', 1),
            ('toc_2', 'H2', 2),
            ('toc_3', 'H1', 1),
        ]
        self.assertEqual(result, expected)

    def test_ast_renderer(self):
        md = create_markdown(
            renderer='ast',
            plugins=[DirectiveToc()]
        )
        data = fixtures.load_json('toc.json')
        self.assertEqual(md(data['text']), data['tokens'])


TestPluginToc.load_fixtures('toc.txt')
