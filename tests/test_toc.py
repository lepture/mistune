from mistune import Markdown
from mistune.toc import TocRenderer
from tests import BaseTestCase, fixtures


class TestPluginToc(BaseTestCase):
    @staticmethod
    def parse(text, escape=False):
        renderer = TocRenderer(escape=escape)
        md = Markdown(renderer)
        html = md(text)
        toc = renderer.render_toc()
        return html, toc

    def assert_case(self, name, text, html):
        result = '.\n'.join(self.parse(text))
        self.assertEqual(result, html)


TestPluginToc.load_fixtures('toc.txt')
