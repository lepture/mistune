import re
import unittest

import mistune

class MathBlockGrammar(mistune.BlockGrammar):
    block_math = re.compile("^\$\$(.*?)\$\$", re.DOTALL)
    latex_environment = re.compile(r"^\\begin\{([a-z]*\*?)\}(.*?)\\end\{\1\}",
                                                re.DOTALL)


class MathBlockLexer(mistune.BlockLexer):
    default_rules = ['block_math', 'latex_environment'] + mistune.BlockLexer.default_rules

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
        return self.renderer.latex_environment(self.token['name'], self.token['text'])

class CustomRenderer(mistune.Renderer):
    def block_math(self, text):
        return '$$%s$$' % text

    def latex_environment(self, name, text):
        return r'\begin{%s}%s\end{%s}' % (name, text, name)

    def inline_math(self, text):
        return '$%s$' % text

class MarkdownMathTestCase(unittest.TestCase):
    def test_markdown2html_math(self):
        # Mathematical expressions should be passed through unaltered
        cases = [("\\begin{equation*}\n"
                  "\\left( \\sum_{k=1}^n a_k b_k \\right)^2 \\leq \\left( \\sum_{k=1}^n a_k^2 \\right) \\left( \\sum_{k=1}^n b_k^2 \\right)\n"
                  "\\end{equation*}"),
                 ("$$\n"
                  "a = 1 *3* 5\n"
                  "$$"),
                  "$ a = 1 *3* 5 $",
                ]
        for case in cases:
            self.assertIn(case, MarkdownWithMath(renderer=CustomRenderer()).render(case))

    def test_markdown2html_math_paragraph(self):
        # https://github.com/ipython/ipython/issues/6724
        a = """Water that is stored in $t$, $s_t$, must equal the storage content of the previous stage,
$s_{t-1}$, plus a stochastic inflow, $I_t$, minus what is being released in $t$, $r_t$.
With $s_0$ defined as the initial storage content in $t=1$, we have"""
        self.assertIn(a, MarkdownWithMath(renderer=CustomRenderer()).render(a))
