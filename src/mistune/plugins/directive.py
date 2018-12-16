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

DIRECTIVE_PATTERN = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9\-]+)\:\: *(?P<value>[^\n]*)\n+'
    r'(?P<options>(?:  \1 {0,3}\:[a-zA-Z0-9\-]+\: *[^\n]*(?:\n[ \t]*)+)*)'
    r'(?P<text>(?:\n+(?:  \1 {0,3}[^\n]*\n)*)*)(?:\n+|$)'
)


def _parse_options(text):
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


def _parse_text_lines(text, leading):
    spaces = ' ' * leading
    for line in text.splitlines():
        line = line.replace(spaces, '', 1)
        if not line.startswith('    '):
            line = line.strip()
        else:
            line = line.rstrip()
        yield line


def parse_directive(self, m, state):
    token = {
        'type': 'directive',
        'params': (
            m.group('name'),
            m.group('value'),
            _parse_options(m.group('options')),
        )
    }
    text = m.group('text')
    if not text.strip():
        token['children'] = []
        return token
    leading = len(m.group(1)) + 2

    text = '\n'.join(_parse_text_lines(text, leading)).lstrip('\n') + '\n'
    rules = list(self.default_rules)
    rules.remove('directive')
    children = self.parse(text, state, rules)
    token['children'] = children
    return token


def render_ast_directive(children, name, value=None, options=None):
    return {
        'type': 'directive',
        'name': name,
        'value': value,
        'options': options,
        'children': children,
    }


def render_html_admonition(text, name, title=None):
    html = '<section class="admonition ' + name + '">\n'
    if title:
        html += '<h1>' + title + '</h1>\n'
    if text:
        html += '<div class="admonition-text">\n' + text + '</div>\n'
    return html + '</section>\n'


def render_html_directive(text, name, value=None, options=None):
    if not options:
        # admonition is a special directive that has no options
        return render_html_admonition(text, name, title=value)
    return '<!-- directive (' + name + ') not supported yet -->\n'


def register_directive(md, html_renderer):
    md.block.register_rule('directive', DIRECTIVE_PATTERN, parse_directive)
    md.block.default_rules.append('directive')

    if md.renderer.NAME == 'ast':
        md.renderer._methods['directive'] = render_ast_directive
    elif md.renderer.NAME == 'html':
        md.renderer._methods['directive'] = html_renderer


def directive(md):
    register_directive(md, render_html_directive)


class Directive(object):
    def __init__(self):
        self._html_renderers = {}

    def register_html_renderer(self, name, fn):
        self._html_renderers[name] = fn

    def render_html_directive(self, text, name, value=None, options=None):
        render = self._html_renderers.get(name)
        if render:
            return render(text, value=value, options=options)
        return render_html_directive(text, name, value=value, options=options)

    def __call__(self, md):
        register_directive(md, self.render_html_directive)
