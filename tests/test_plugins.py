from mistune import Markdown, AstRenderer, HTMLRenderer, plugins
from tests import BaseTestCase, fixtures


def load_plugin(plugin_name, ast=False):
    _plugin = getattr(plugins, 'plugin_{}'.format(plugin_name))

    class TestPlugin(BaseTestCase):
        md = Markdown(
            renderer=HTMLRenderer(escape=False),
            plugins=[_plugin]
        )

    def test_ast_renderer(self):
        md = Markdown(renderer=AstRenderer(), plugins=[_plugin])
        data = fixtures.load_json(plugin_name + '.json')
        self.assertEqual(md(data['text']), data['tokens'])

    if ast:
        test_ast_renderer.__doc__ = 'Run {} ast renderer'.format(plugin_name)
        setattr(TestPlugin, 'test_ast_renderer', test_ast_renderer)

    TestPlugin.load_fixtures(plugin_name + '.txt')
    globals()['TestPlugin_' + plugin_name] = TestPlugin


load_plugin('url')
load_plugin('strikethrough')
load_plugin('footnotes', True)
load_plugin('table', True)
load_plugin('task_lists', True)
