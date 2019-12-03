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

__all__ = ['Directive', 'PluginAdmonition', 'PluginDirective']


DIRECTIVE_PATTERN = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9_-]+)\:\: *(?P<value>[^\n]*)\n+'
    r'(?P<options>(?:  \1 {0,3}\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)'
    r'(?P<text>(?:  \1 {0,3}[^\n]*\n+)*)'
)


class Directive(object):
    @staticmethod
    def parse_text(m):
        text = m.group('text')
        if not text.strip():
            return ''

        leading = len(m.group(1)) + 2
        text = '\n'.join(_parse_text_lines(text, leading)).lstrip('\n') + '\n'
        return text

    @staticmethod
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

    def register_directive(self, md, name):
        plugin = getattr(md, '_directive', None)
        if not plugin:
            raise RuntimeError('You MUST add "directive" plugin at first')
        plugin.register_directive(name, self.parse)

    def parse(self, block, m, state):
        raise NotImplementedError()

    def __call__(self, md):
        raise NotImplementedError()


def render_html_admonition(text, name, title=None):
    html = '<section class="admonition ' + name + '">\n'
    if title:
        html += '<h1>' + title + '</h1>\n'
    if text:
        html += '<div class="admonition-text">\n' + text + '</div>\n'
    return html + '</section>\n'


def render_ast_admonition(children, name, title=None):
    return {
        'type': 'admonition',
        'children': children,
        'name': name,
        'title': title,
    }


class PluginAdmonition(Directive):
    SUPPORTED_NAMES = {
        "attention", "caution", "danger", "error", "hint",
        "important", "note", "tip", "warning",
    }

    def parse(self, block, m, state):
        options = self.parse_options(m)
        if options:
            return {
                'type': 'block_error',
                'raw': 'Admonition has no options'
            }
        name = m.group('name')
        title = m.group('value')
        text = self.parse_text(m)

        rules = list(block.rules)
        rules.remove('directive')
        children = block.parse(text, state, rules)
        return {
            'type': 'admonition',
            'children': children,
            'params': (name, title)
        }

    def __call__(self, md):
        for name in self.SUPPORTED_NAMES:
            self.register_directive(md, name)

        if md.renderer.NAME == 'html':
            md.renderer.register('admonition', render_html_admonition)
        elif md.renderer.NAME == 'ast':
            md.renderer.register('admonition', render_ast_admonition)


class PluginDirective(object):
    def __init__(self):
        self._directives = {}

    def register_directive(self, name, fn):
        self._directives[name] = fn

    def parse_block_directive(self, block, m, state):
        name = m.group('name')
        method = self._directives.get(name)
        if method:
            return method(block, m, state)

        token = {
            'type': 'block_error',
            'raw': 'Unsupported directive: ' + name,
        }
        return token

    def __call__(self, md):
        md._directive = self
        md.block.register_rule(
            'directive', DIRECTIVE_PATTERN,
            self.parse_block_directive
        )
        md.block.rules.append('directive')


def _parse_text_lines(text, leading):
    spaces = ' ' * leading
    for line in text.splitlines():
        line = line.replace(spaces, '', 1)
        if not line.startswith('    '):
            line = line.strip()
        else:
            line = line.rstrip()
        yield line
