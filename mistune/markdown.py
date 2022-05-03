from .block_parser import State, BlockParser, expand_leading_tab
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

    def before_render(self, tokens, state):
        for hook in self.before_render_hooks:
            tokens = hook(self, tokens, state)
        return tokens

    def after_render(self, result, state):
        for hook in self.after_render_hooks:
            result = hook(self, result, state)
        return result

    def parse(self, s, state=None):
        if state is None:
            state = State()

        if s is None:
            s = '\n'
        else:
            s = expand_leading_tab(s)

        lines = s.splitlines()
        state.lines = lines
        state.cursor_end = len(lines) - 1

        for hook in self.before_parse_hooks:
            hook(self, s, state)

        self.block.parse(state)

        print(state.tokens)
        # tokens = self.before_render(tokens, state)
        # result = self.block.render(tokens, self.inline, state)
        # result = self.after_render(result, state)
        return state

    def read(self, filepath, state=None):
        if state is None:
            state = {}

        state['__file__'] = filepath
        with open(filepath, 'rb') as f:
            s = f.read()

        return self.parse(s.decode('utf-8'), state)

    def __call__(self, s):
        return self.parse(s)
