
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

    inline = MyInlineLexer(renderer=mistune.Renderer())
    markdown = mistune.Markdown(inline=inline)
    ret = markdown('[[Link Text|Wiki Link]]')
    assert '<a href' in ret
