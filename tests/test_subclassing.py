# coding: utf-8

import os
import re
import mistune

root = os.path.dirname(__file__)


class MathBlockGrammar(mistune.BlockGrammar):
    block_math = re.compile("^\$\$(.*?)\$\$", re.DOTALL)
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
    math = re.compile("^\$(.+?)\$")
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


class CustomRenderer(mistune.Renderer):
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

    rv = MarkdownWithMath(renderer=CustomRenderer()).render(text)
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
