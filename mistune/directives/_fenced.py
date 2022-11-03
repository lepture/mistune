"""
    Fenced Directive Syntax
    ~~~~~~~~~~~~~~~~~~~~~~~

    This syntax is inspired by markdown-it-docutils, the syntax looks
    like a fenced code block, except the language code is wrapped with
    ``{`` and ``}``::

        ```{name} title
        :option: value

        content
        ```

    :copyright: (c) Hsiaoming Yang
"""

import re
from ._base import DirectiveParser, BaseDirective

__all__ = ['FencedDirective']


_directive_re = re.compile(
    r'\{(?P<name>[a-zA-Z0-9_-]+)\} +(?P<title>[^\n]*)(?:\n|$)'
    r'(?P<options>(?:\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)'
    r'\n*(?P<text>(?:[^\n]*\n+)*)'
)


class FencedParser(DirectiveParser):
    NAME = 'fenced_directive'

    @staticmethod
    def parse_name(m: re.Match):
        return m.group('name')

    @staticmethod
    def parse_title(m: re.Match):
        return m.group('title')

    @staticmethod
    def parse_content(m: re.Match):
        text = m.group('text')
        return text.strip() + '\n'


class FencedDirective(BaseDirective):
    parser = FencedParser
    directive_pattern = r'^(?P<fenced_directive_mark>`{3,}|~{3,})\{[a-zA-Z0-9_-]+\}'
    register_before = 'fenced_code'

    def parse_directive(self, block, m, state):
        marker = m.group('fenced_directive_mark')
        mlen = len(marker)
        _end_pattern = (
            r'^ {0,3}' + marker[0] + '{' + str(mlen) + r',}'
            r'[ \t]*(?:\n|$)'
        )
        _end_re = re.compile(_end_pattern, re.M)
        cursor_start = m.start() + mlen

        _end_m = _end_re.search(state.src, cursor_start)
        if _end_m:
            text = state.src[cursor_start:_end_m.start()]
            end_pos = _end_m.end()
        else:
            text = state.src[cursor_start:]
            end_pos = state.cursor_max

        _new_m = _directive_re.match(text)
        if not _new_m:
            return

        name = _new_m.group('name')
        self.parse_method(name, block, _new_m, state)
        return end_pos
