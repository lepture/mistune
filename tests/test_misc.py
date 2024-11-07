import mistune
from unittest import TestCase


class TestMiscCases(TestCase):
    def test_none(self):
        self.assertEqual(mistune.html(None), '')

    def test_before_parse_hooks(self):
        def _add_name(md, state):
            state.env['name'] = 'test'

        md = mistune.create_markdown()
        md.before_parse_hooks.append(_add_name)
        state = md.block.state_cls()
        md.parse('', state)
        self.assertEqual(state.env['name'], 'test')

    def test_hard_wrap(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md('foo\nbar')
        expected = '<p>foo<br />\nbar</p>'
        self.assertEqual(result.strip(), expected)

        md = mistune.create_markdown(
            escape=False, hard_wrap=True, plugins=['speedup'])
        result = md('foo\nbar')
        self.assertEqual(result.strip(), expected)

    def test_escape_html(self):
        md = mistune.create_markdown(escape=True)
        result = md('<div>1</div>')
        expected = '<p>&lt;div&gt;1&lt;/div&gt;</p>'
        self.assertEqual(result.strip(), expected)

        result = md('<em>1</em>')
        expected = '<p>&lt;em&gt;1&lt;/em&gt;</p>'
        self.assertEqual(result.strip(), expected)

    def test_harmful_links(self):
        result = mistune.html('[h](javAscript:alert)')
        expected = '<p><a href="#harmful-link">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_ref_link(self):
        result = mistune.html('[link][h]\n\n[h]: /foo')
        expected = '<p><a href="/foo">link</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_allow_harmful_protocols(self):
        renderer = mistune.HTMLRenderer(allow_harmful_protocols=True)
        md = mistune.Markdown(renderer)
        result = md('[h](javascript:alert)')
        expected = '<p><a href="javascript:alert">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_allow_data_protocols(self):
        renderer = mistune.HTMLRenderer(allow_harmful_protocols=['data:'])
        md = mistune.Markdown(renderer)
        result = md('[h](data:alert)')
        expected = '<p><a href="data:alert">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_use_plugin(self):
        from mistune.plugins.url import url
        md = mistune.Markdown(mistune.HTMLRenderer())
        md.use(url)

    def test_markdown_func(self):
        result = mistune.markdown('**b**')
        expected = '<p><strong>b</strong></p>\n'
        self.assertEqual(result, expected)

        # trigger to use cached parser
        result = mistune.markdown('**b**')
        self.assertEqual(result, expected)

    def test_ast_output(self):
        md = mistune.create_markdown(escape=False, renderer=None)
        text = '# h1\n\nfoo **bar**\n\n`&<>"`'
        result = md(text)
        expected = [
            {
                'type': 'heading',
                'children': [{'type': 'text', 'raw': 'h1'}],
                'attrs': {'level': 1},
                'style': 'atx',
            },
            {'type': 'blank_line'},
            {
                'type': 'paragraph',
                'children': [
                    {'type': 'text', 'raw': 'foo '},
                    {'type': 'strong', 'children': [{'type': 'text', 'raw': 'bar'}]}
                ]
            },
            {'type': 'blank_line'},
            {
                'type': 'paragraph',
                'children': [
                    {'type': 'codespan', 'raw': '&<>"'},
                ]
            },
        ]
        self.assertEqual(result, expected)

    def test_ast_url(self):
        md = mistune.create_markdown(escape=False, renderer=None)
        label = 'hi &<>"'
        url = 'https://example.com/foo?a=1&b=2'
        text = '[{}]({})'.format(label, url)
        result = md(text)
        expected = [
            {
                'type': 'paragraph',
                'children': [
                    {
                        'type': 'link',
                        'children': [{'type': 'text', 'raw': label}],
                        'attrs': {'url': url},
                    },
                ],
            },
        ]
        self.assertEqual(result, expected)

    def test_emsp(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md('\u2003\u2003foo\nbar\n\n\u2003\u2003foobar')
        expected = '<p>\u2003\u2003foo<br />\nbar</p>\n<p>\u2003\u2003foobar</p>'
        self.assertEqual(result.strip(), expected)

    def test_html_tag_text_following_list(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md('foo\n- bar\n\ntable')
        expected = '<p>foo</p>\n<ul>\n<li>bar</li>\n</ul>\n<p>table</p>'
        self.assertEqual(result.strip(), expected)
