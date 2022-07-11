from .block_parser import BlockParser
from .inline_parser import InlineParser


class Markdown:
    def __init__(self, renderer, block=None, inline=None, plugins=None):
        if block is None:
            block = BlockParser()

        if inline is None:
            inline = InlineParser(renderer)

        self.block = block
        self.inline = inline
        self.renderer = inline.renderer
        self.before_parse_hooks = []
        self.before_render_hooks = []
        self.after_render_hooks = []

        if plugins:
            for plugin in plugins:
                plugin(self)

    def use(self, plugin):
        plugin(self)

    def parse(self, s, state=None):
        if state is None:
            state = self.block.state_cls()

        # normalize line separator
        s = s.replace('\r\n', '\n')
        s = s.replace('\r', '\n')

        state.process(s)

        for hook in self.before_parse_hooks:
            hook(self, state)

        self.block.parse(state)

        for hook in self.before_render_hooks:
            hook(self, state)

        result = self.block.render(state, self.inline)

        for hook in self.after_render_hooks:
            result = hook(self, result, state)
        return result, state

    def read(self, filepath, encoding='utf-8', state=None):
        if state is None:
            state = self.block.state_cls()

        state.env['__file__'] = filepath
        with open(filepath, 'rb') as f:
            s = f.read()

        s = s.decode(encoding)
        return self.parse(s, state)

    def __call__(self, s):
        if s is None:
            s = '\n'
        return self.parse(s)[0]
