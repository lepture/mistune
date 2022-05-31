"""
    Directive Syntax
    ~~~~~~~~~~~~~~~~~

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

__all__ = ['Directive']


DIRECTIVE_PATTERN = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9_-]+)\:\: *(?P<value>[^\n]*)\n+'
    r'(?P<options>(?:  \1 {0,3}\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)'
    r'(?P<text>(?:  \1 {0,3}[^\n]*\n+)*)'
)


class Directive(object):

    def register_directive(self, md, name):
        plugin = getattr(md, '_rst_directive', None)
        if not plugin:
            plugin = PluginDirective()
            plugin(md)

        plugin.register_directive(name, self.parse)

    def parse(self, block, m, state):
        raise NotImplementedError()

    def __call__(self, md):
        raise NotImplementedError()


class PluginDirective(object):
    def __init__(self):
        self._directives = {}

    def register_directive(self, name, fn):
        self._directives[name] = fn

    def parse_block_directive(self, block, m, state):
        m = state.match(DIRECTIVE_PATTERN)
        if not m:
            return

        name = m.group('name')
        method = self._directives.get(name)
        if method:
            token = method(block, m, state)
        else:
            token = {
                'type': 'block_error',
                'raw': 'Unsupported directive: ' + name,
            }

        end_pos = m.end()
        text = state.get_text(end_pos)
        state.append_token(token)
        return end_pos

    def __call__(self, md):
        md._rst_directive = self
        pattern = r'^\.\. +[a-zA-Z0-9_-]+\:\:'
        md.block.register_rule('directive', pattern, self.parse_block_directive)


def parse_options(m):
    text = m.group('options')
    if not text.strip():
        return []

    options = []
    for line in re.split(r'\n+', text):
        line = line.strip()[1:]
        if not line:
            continue
        i = line.find(':')
        k = line[:i]
        v = line[i + 1:].strip()
        options.append((k, v))
    return options


def parse_children(block, m, state):
    full_content = m.group(0)
    text = m.group('text')

    pretext = full_content[:-len(text)]

    rules = list(block.rules)
    rules.remove('directive')

    # scan children state
    leading = len(m.group(1)) + 2
    text = '\n'.join(line[leading:] for line in text.splitlines()) + '\n'

    child = block.state_cls(state)
    child.process(text)

    block.parse(child, rules)
    return child.tokens
