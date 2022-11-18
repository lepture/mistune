from mistune import create_markdown
from mistune.renderers.rst import RSTRenderer
from tests import BaseTestCase


class TestRSTRenderer(BaseTestCase):
    @staticmethod
    def parse(text):
        md = create_markdown(renderer=RSTRenderer())
        return md(text)

TestRSTRenderer.load_fixtures('renderer_rst.txt')
