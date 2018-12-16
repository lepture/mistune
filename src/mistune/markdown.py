from .blocks import BlockParser
from .inlines import InlineParser


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
        self.after_parse_hooks = []

    def use(self, plugin):
        plugin(self)

    def before_parse(self, s, state):
        # prepare state for blocks
        state.update({
            'def_links': {},
            'def_footnotes': {},
        })
        for hook in self.before_parse_hooks:
            s, state = hook(s, state)
        return s, state

    def after_parse(self, tokens, state):
        footnotes = state.get('footnotes')
        if footnotes:
            def_footnotes = state['def_footnotes']
            children = [
                self.block.parse_footnote_item(def_footnotes[k])
                for k in footnotes
            ]
            tokens.append({'type': 'footnote', 'children': children})

        for hook in self.after_parse_hooks:
            tokens, state = hook(tokens, state)
        return tokens, state

    def parse(self, s, state=None):
        if state is None:
            state = {}

        s, state = self.before_parse(s, state)
        tokens = self.block.parse(s, state)
        tokens, state = self.after_parse(tokens, state)
        return self.block.render(tokens, self.inline, state)

    def __call__(self, s):
        return self.parse(s)
