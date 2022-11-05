import re
from ._base import DirectiveParser, BaseDirective

__all__ = ['FencedDirective']


_directive_re = re.compile(
    r'\{(?P<name>[a-zA-Z0-9_-]+)\} *(?P<title>[^\n]*)(?:\n|$)'
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
        return m.group('text')


class FencedDirective(BaseDirective):
    """A **fenced** style of directive looks like a fenced code block, it is
    inspired by markdown-it-docutils. The syntax looks like:

    .. code-block:: text

        ```{directive-name} title
        :option-key: option value
        :option-key: option value

        content text here
        ```

    To use ``FencedDirective``, developers can add it into plugin list in
    the :class:`Markdown` instance:

    .. code-block:: python

        import mistune
        from mistune.directives import FencedDirective, Admonition

        md = mistune.create_markdown(plugins=[
            # ...
            FencedDirective([Admonition()]),
        ])

    FencedDirective is using >= 3 backticks or curly-brackets for the fenced
    syntax. Developers can change it to other characters, e.g. colon:

    .. code-block:: python

            directive = FencedDirective([Admonition()], ':')

    And then the directive syntax would look like:

    .. code-block:: text

        ::::{note} Nesting directives
        You can nest directives by ensuring the start and end fence matching
        the length. For instance, in this example, the admonition is started
        with 4 colons, then it should end with 4 colons.

        You can nest another admonition with other length of colons except 4.

        :::{tip} Longer outermost fence
        It would be better that you put longer markers for the outer fence,
        and shorter markers for the inner fence. In this example, we put 4
        colons outsie, and 3 colons inside.
        :::
        ::::

    :param plugins: list of directive plugins
    :param markers: characters to determine the fence, default is backtick
                    and curly-bracket
    """
    parser = FencedParser
    register_before = 'fenced_code'

    def __init__(self, plugins, markers='`~'):
        super(FencedDirective, self).__init__(plugins)
        _marker_pattern = '|'.join(re.escape(c) for c in markers)
        self.directive_pattern = (
            r'^(?P<fenced_directive_mark>(?:' + _marker_pattern + r'){3,})'
            r'\{[a-zA-Z0-9_-]+\}'
        )

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
