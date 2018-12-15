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

    def use(self, plugin):
        plugin(self)

    def parse(self, s, state=None):
        if state is None:
            state = {}

        # prepare state for blocks
        state.update({
            'def_links': {},
            'def_footnotes': {},
        })

        tokens = self.block.parse(s, state)
        footnotes = state.get('footnotes')
        if footnotes:
            def_footnotes = state['def_footnotes']
            children = [
                self.block.parse_footnote_item(def_footnotes[k])
                for k in footnotes
            ]
            tokens.append({'type': 'footnote', 'children': children})
        return self.block.render(tokens, self.inline, state)

    def __call__(self, s):
        return self.parse(s)
