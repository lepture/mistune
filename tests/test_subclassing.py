# coding: utf-8

import os
import re
import copy
import mistune

root = os.path.dirname(__file__)


class MathBlockGrammar(mistune.BlockGrammar):
    block_math = re.compile(r'^\$\$(.*?)\$\$', re.DOTALL)
    latex_environment = re.compile(
        r"^\\begin\{([a-z]*\*?)\}(.*?)\\end\{\1\}",
        re.DOTALL
    )


class MathBlockLexer(mistune.BlockLexer):
    default_rules = ['block_math', 'latex_environment'] + \
        mistune.BlockLexer.default_rules

    def __init__(self, rules=None, **kwargs):
        if rules is None:
            rules = MathBlockGrammar()
        super(MathBlockLexer, self).__init__(rules, **kwargs)

    def parse_block_math(self, m):
        """Parse a $$math$$ block"""
        self.tokens.append({
            'type': 'block_math',
            'text': m.group(1)
        })

    def parse_latex_environment(self, m):
        self.tokens.append({
            'type': 'latex_environment',
            'name': m.group(1),
            'text': m.group(2)
        })


class MathInlineGrammar(mistune.InlineGrammar):
    math = re.compile(r'^\$(.+?)\$')
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~$]|https?://| {2,}\n|$)')


class MathInlineLexer(mistune.InlineLexer):
    default_rules = ['math'] + mistune.InlineLexer.default_rules

    def __init__(self, renderer, rules=None, **kwargs):
        if rules is None:
            rules = MathInlineGrammar()
        super(MathInlineLexer, self).__init__(renderer, rules, **kwargs)

    def output_math(self, m):
        return self.renderer.inline_math(m.group(1))


class MarkdownWithMath(mistune.Markdown):
    def __init__(self, renderer, **kwargs):
        if 'inline' not in kwargs:
            kwargs['inline'] = MathInlineLexer
        if 'block' not in kwargs:
            kwargs['block'] = MathBlockLexer
        super(MarkdownWithMath, self).__init__(renderer, **kwargs)

    def output_block_math(self):
        return self.renderer.block_math(self.token['text'])

    def output_latex_environment(self):
        return self.renderer.latex_environment(
            self.token['name'], self.token['text']
        )


class MathRenderer(mistune.Renderer):
    def block_math(self, text):
        return '$$%s$$' % text

    def latex_environment(self, name, text):
        return r'\begin{%s}%s\end{%s}' % (name, text, name)

    def inline_math(self, text):
        return '$%s$' % text


def assert_data(filename):
    if filename.endswith('.md'):
        filename = os.path.join(root, 'fixtures', 'data', filename)
        with open(filename) as f:
            text = f.read().strip()
    else:
        text = filename

    rv = MarkdownWithMath(renderer=MathRenderer()).render(text)
    assert text in rv


def test_simple_math():
    assert_data("$$\na = 1 *3* 5\n$$")
    assert_data("$ a = 1 *3* 5 $")


def test_markdown2html_math():
    # Mathematical expressions should be passed through unaltered
    assert_data('math.md')


def test_math_paragraph():
    # https://github.com/ipython/ipython/issues/6724
    assert_data('math-paragraph.md')


class WikiInlineGrammar(mistune.InlineGrammar):
    # it would take a while for creating the right regex
    wiki_link = re.compile(
        r'\[\['                   # [[
        r'([\s\S]+?\|[\s\S]+?)'   # Page 2|Page 2
        r'\]\](?!\])'             # ]]
    )


class WikiInlineLexer(mistune.InlineLexer):
    default_rules = copy.copy(mistune.InlineLexer.default_rules)
    default_rules.insert(3, 'wiki_link')

    def __init__(self, renderer, rules=None, **kwargs):
        if rules is None:
            rules = WikiInlineGrammar()

        super(WikiInlineLexer, self).__init__(renderer, rules, **kwargs)

    def output_wiki_link(self, m):
        text = m.group(1)
        alt, link = text.split('|')
        return '<a href="%s">%s</a>' % (link, alt)


def test_custom_lexer():
    markdown = mistune.Markdown(inline=WikiInlineLexer)
    ret = markdown('[[Link Text|Wiki Link]]')
    assert '<a href' in ret


class TokenTreeRenderer(mistune.Renderer):
    # options is required
    options = {}

    def placeholder(self):
        return []

    def __getattribute__(self, name):
        """Saves the arguments to each Markdown handling method."""
        found = TokenTreeRenderer.__dict__.get(name)
        if found is not None:
            return object.__getattribute__(self, name)

        def fake_method(*args, **kwargs):
            return [(name, args, kwargs)]
        return fake_method


def test_token_tree():
    """Tests a Renderer that returns a list from the placeholder method."""
    with open(os.path.join(root, 'fixtures', 'data', 'tree.md')) as f:
        content = f.read()

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

    processor = mistune.Markdown(renderer=TokenTreeRenderer())
    found = processor.render(content)
    assert expected == found, "Expected:\n%r\n\nFound:\n%r" % (expected, found)
