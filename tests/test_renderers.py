from mistune import create_markdown
from mistune.renderers.rst import RSTRenderer
from mistune.renderers.markdown import MarkdownRenderer
from tests import BaseTestCase


def load_renderer(renderer):
    class TestRenderer(BaseTestCase):
        parse = create_markdown(renderer=renderer)

    name = renderer.NAME
    TestRenderer.load_fixtures('renderer_' + name + '.txt')
    globals()["TestRenderer" + name.title()] = TestRenderer


load_renderer(RSTRenderer())
load_renderer(MarkdownRenderer())
