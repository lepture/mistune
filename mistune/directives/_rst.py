"""
    RST Directive Syntax
    ~~~~~~~~~~~~~~~~~~~~

    This syntax is inspired by reStructuredText. The syntax is very powerful,
    that you can define a lot of custom features by your own.

    The syntax looks like::

        .. directive-name:: directive value
           :option-key: option value
           :option-key: option value

           full featured markdown text here

    :copyright: (c) Hsiaoming Yang
"""

import re
from ._base import DirectiveParser, BaseDirective

__all__ = ['RstDirective']


_directive_re = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9_-]+)\:\: *(?P<title>[^\n]*)(?:\n|$)'
    r'(?P<options>(?:  \1 {0,3}\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)'
    r'\n*(?P<text>(?:  \1 {0,3}[^\n]*\n+)*)'
)


class RstParser(DirectiveParser):
    NAME = 'rst_directive'

    @staticmethod
    def parse_name(m: re.Match):
        return m.group('name')

    @staticmethod
    def parse_title(m: re.Match):
        return m.group('title')

    @staticmethod
    def parse_content(m: re.Match):
        full_content = m.group(0)
        text = m.group('text')
        pretext = full_content[:-len(text)]
        leading = len(m.group(1)) + 2
        return '\n'.join(line[leading:] for line in text.splitlines()) + '\n'


class RstDirective(BaseDirective):
    parser = RstParser
    DIRECTIVE_PATTERN = r'^\.\. +[a-zA-Z0-9_-]+\:\:'

    def parse_directive(self, block, m, state):
        m = _directive_re.match(state.src, state.cursor)
        if not m:
            return

        name = m.group('name')
        self.parse_method(name, block, m, state)
        return m.end()
