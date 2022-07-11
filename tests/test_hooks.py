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
        result = html + render_toc_ul(state.env['toc_items'])
        return result


TestTocHook.load_fixtures('hook_toc.txt')
