import os
from mistune import create_markdown
from mistune.toc import add_toc_hook, render_toc_ul
from tests import BaseTestCase


class TestTocHook(BaseTestCase):
    @staticmethod
    def parse(text):
        md = create_markdown(escape=False)
        add_toc_hook(md)
        html, state = md.parse(text)
        result = html + render_toc_ul(state.env["toc_items"])
        return result

    def test_customize_heading_id_func(self):
        def heading_id(token, i):
            return "t-" + str(i + 1)

        md = create_markdown(escape=False)
        add_toc_hook(md, heading_id=heading_id)
        html = md("# h1")
        self.assertEqual(html, '<h1 id="t-1">h1</h1>\n')

    def test_render_empty_toc(self):
        self.assertEqual(render_toc_ul([]), "")
        self.assertEqual(render_toc_ul(filter(lambda _: False, [])), "")


TestTocHook.load_fixtures("hook_toc.txt")
