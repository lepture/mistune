import re
from .blocks import BlockParser, expand_leading_tab
from .inlines import InlineParser

_newline_pattern = re.compile(r'\r\n|\r')
_blank_lines = re.compile(r'^ +$', re.M)


class Markdown(object):
    def __init__(self, renderer, block=None, inline=None):
        if block is None:
            block = BlockParser()

        if inline is None:
            inline = InlineParser(renderer)

        self.block = block
        self.inline = inline
        self.renderer = inline.renderer
        self.before_parse_hooks = []
        self.after_render_hooks = []

    def use(self, plugin):
        plugin(self)

    def before_parse(self, s, state):
        s, state = preprocess(s, state)
        for hook in self.before_parse_hooks:
            s, state = hook(s, state)
        return s, state

    def after_render(self, result, state):
        footnotes = self.render_footnotes(state)
        if footnotes is not None:
            if self.renderer.IS_TREE:
                result.extend(footnotes)
            else:
                result += footnotes

        for hook in self.after_render_hooks:
            result = hook(result, state)
        return result

    def render_footnotes(self, state):
        footnotes = state.get('footnotes')
        if not footnotes:
            return None

        children = [
            self.block.parse_footnote_item(k, i, state)
            for i, k in enumerate(footnotes)
        ]
        tokens = [{'type': 'footnote', 'children': children}]
        return self.block.render(tokens, self.inline, state)

    def parse(self, s, state=None):
        if state is None:
            state = {}

        s, state = self.before_parse(s, state)
        tokens = self.block.parse(s, state)
        result = self.block.render(tokens, self.inline, state)
        result = self.after_render(result, state)
        return result

    def read(self, filepath, state=None):
        if state is None:
            state = {}

        state['__file__'] = filepath
        with open(filepath, 'rb') as f:
            s = f.read()

        return self.parse(s.decode('utf-8'), state)

    def __call__(self, s):
        return self.parse(s)


def preprocess(s, state):
    state.update({
        'def_links': {},
        'def_footnotes': {},
        'footnotes': [],
    })

    if s is None:
        s = '\n'
    else:
        s = s.replace('\u2424', '\n')
        s = _newline_pattern.sub('\n', s)
        s = _blank_lines.sub('', s)
        s = expand_leading_tab(s)
        if not s.endswith('\n'):
            s += '\n'

    return s, state
