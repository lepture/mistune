import json
from mistune import create_markdown
from mistune.directives import Admonition
from tests import fixtures
from unittest import TestCase


class TestPluginAdmonition(TestCase):
    def test_unsupported_directive(self):
        md = create_markdown(plugins=[Admonition()])
        s = '.. hello:: Warnning\n\n   message'
        html = md(s)
        self.assertIn('Unsupported directive: hello', html)

    def test_note_admonition(self):
        md = create_markdown(plugins=[Admonition()])
        s = '.. note:: Warnning\n\n   message'
        html = md(s)
        self.assertIn('class="admonition note"', html)
        self.assertIn('<h1>Warnning</h1>', html)
        self.assertIn('<p>message</p>', html)

    def test_code_admonition(self):
        md = create_markdown(plugins=[Admonition()])
        s = '.. note:: Warnning\n\n       print() '
        html = md(s)
        self.assertIn('class="admonition note"', html)
        self.assertIn('<h1>Warnning</h1>', html)
        self.assertIn('<pre><code>print() \n</code></pre>', html)

    def test_note_admonition_no_text(self):
        md = create_markdown(
            plugins=[Admonition()]
        )
        s = '.. note:: Warnning'
        html = md(s)
        self.assertIn('class="admonition note"', html)
        self.assertIn('<h1>Warnning</h1>', html)

    def test_admonition_options(self):
        md = create_markdown(plugins=[Admonition()])
        s = '.. note:: Warnning\n\n   :option: 3'
        html = md(s)
        self.assertIn('Admonition has no options', html)

    def test_ast_admonition(self):
        data = fixtures.load_json('admonition.json')
        md = create_markdown(
            renderer='ast',
            plugins=[Admonition()]
        )
        # Use JSON to fix the differences between tuple and list
        tokens = json.loads(json.dumps(md(data['text'])))
        self.assertEqual(tokens, data['tokens'])
