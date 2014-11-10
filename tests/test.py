
import os
import re
import mistune
root = os.path.dirname(__file__)

known = []

features = [
    'table', 'fenced_code', 'footnotes',
    'autolink', 'strikethrough',
]
m = mistune.Markdown(features=features)


def render(folder, name):
    filepath = os.path.join(folder, name + '.text')
    with open(filepath) as f:
        content = f.read()

    html = m.parse(content)

    filepath = os.path.join(folder, name + '.html')
    with open(filepath) as f:
        result = f.read()

    html = re.sub(r'\s', '', html)
    result = re.sub(r'\s', '', result)
    for i, s in enumerate(html):
        if s != result[i]:
            begin = max(i - 30, 0)
            msg = '\n\n%s\n------Not Equal(%d)------\n%s' % (
                html[begin:i+30], i, result[begin:i+30]
            )
            raise ValueError(msg)
    assert html == result


def listdir(folder):
    folder = os.path.join(root, folder)
    files = os.listdir(folder)
    files = filter(lambda o: o.endswith('.text'), files)
    names = map(lambda o: o[:-5], files)
    return folder, names


def test_extra():
    folder, names = listdir('extra')
    for key in names:
        yield render, folder, key


def test_normal():
    folder, names = listdir('cases')
    for key in names:
        yield render, folder, key


def test_escape():
    ret = mistune.markdown('<div>**foo**</div>', escape=True)
    assert '&gt;' in ret

    ret = mistune.markdown('this **foo** is <b>bold</b>', escape=True)
    assert '&gt;' in ret


def test_linebreak():
    ret = mistune.markdown('this **foo** \nis me')
    assert '<br>' not in ret

    ret = mistune.markdown('this **foo** \nis me', hard_wrap=True)
    assert '<br>' in ret


def test_safe_links():
    ret = mistune.markdown('javascript ![foo](<javascript:alert>) alert')
    assert 'src=""' in ret
    ret = mistune.markdown('javascript [foo](<javascript:alert>) alert')
    assert 'href=""' in ret


def test_skip_style():
    ret = mistune.markdown(
        'foo\n<style>body{color:red}</style>', skip_style=True
    )
    assert ret == '<p>foo</p>\n'


def test_use_xhtml():
    ret = mistune.markdown('foo\n\n----\n\nbar')
    assert '<hr>' in ret
    ret = mistune.markdown('foo\n\n----\n\nbar', use_xhtml=True)
    assert '<hr />' in ret

    ret = mistune.markdown('foo  \nbar', use_xhtml=True)
    assert '<br />' in ret

    ret = mistune.markdown('![foo](bar "title")', use_xhtml=True)
    assert '<img src="bar" alt="foo" title="title" />' in ret


def test_skip_html():
    ret = mistune.markdown('foo <b>bar</b>', skip_html=True)
    assert ret == '<p>foo bar</p>\n'


def test_block_html():
    ret = mistune.markdown('<div>**foo**</div>')
    assert '<strong>' not in ret
    ret = mistune.markdown('<div>**foo**</div>', parse_html=True)
    assert '<strong>' in ret


def test_trigger_more_cases():
    markdown = mistune.Markdown(
        inline=mistune.InlineLexer,
        block=mistune.BlockLexer,
        skip_html=True
    )
    ret = markdown.render('foo[^foo]\n\n[^foo]: foo\n\n[^foo]: bar\n')
    assert 'bar' not in ret


def test_custom_lexer():
    import copy

    class MyInlineGrammar(mistune.InlineGrammar):
        # it would take a while for creating the right regex
        wiki_link = re.compile(
            r'\[\['                   # [[
            r'([\s\S]+?\|[\s\S]+?)'   # Page 2|Page 2
            r'\]\](?!\])'             # ]]
        )

    class MyInlineLexer(mistune.InlineLexer):
        default_features = copy.copy(mistune.InlineLexer.default_features)
        default_features.insert(3, 'wiki_link')

        def __init__(self, renderer, rules=None, **kwargs):
            if rules is None:
                rules = MyInlineGrammar()

            super(MyInlineLexer, self).__init__(renderer, rules, **kwargs)

        def output_wiki_link(self, m):
            text = m.group(1)
            alt, link = text.split('|')
            return '<a href="%s">%s</a>' % (link, alt)

    markdown = mistune.Markdown(inline=MyInlineLexer)
    ret = markdown('[[Link Text|Wiki Link]]')
    assert '<a href' in ret


def test_custom_default_output():
    """Tests a Renderer that returns a list from the default_output method."""

    class CustomRenderer(mistune.Renderer):
        def default_output(self):
            return []

        def __getattribute__(self, name):
            """Saves the arguments to each Markdown handling method."""
            found = CustomRenderer.__dict__.get(name)
            if found:
                return object.__getattribute__(self, name)
            def fake_method(*args, **kwargs):
                return [(name, args, kwargs)]
            return fake_method

    markdown_data = """
## Title here

Some text.

In two paragraphs. And then a list.

- foo
- bar
    1. meep
    1. stuff
"""
    expected = [
        ('header', ([('text', ('Title here',), {})], 2, 'Title here'), {}),
        ('paragraph', ([('text', ('Some text.',), {})],), {}),
        ('paragraph',
         ([('text', ('In two paragraphs. And then a list.',), {})],),
         {}),
        ('list',
         ([('list_item', ([('text', ('foo',), {})],), {}),
             ('list_item',
              ([('text', ('bar',), {}),
                  ('list',
                   ([('list_item', ([('text', ('meep',), {})],), {}),
                       ('list_item', ([('text', ('stuff',), {})],), {})],
                    True),
                   {})],),
              {})],
          False),
         {})
    ]

    processor = mistune.Markdown(renderer=CustomRenderer())
    found = processor.render(markdown_data)
    assert expected == found, "Expected:\n%r\n\nFound:\n%r" % (expected, found)
