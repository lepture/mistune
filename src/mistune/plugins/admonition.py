"""
    Admonition Syntax
    ~~~~~~~~~~~~~~~~~

    This syntax is inspired by reStructuredText. The syntax is very powerful,
    that you can define a lot of custom features by your own.

    The syntax looks like::

        .. admonition-name:: admonition title
           :option-key: option value
           :option-key: option value

           full featured markdown text here

    :copyright: (c) Hsiaoming Yang
"""

import re

ADMONITION_PATTERN = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9\-]+)\:\: *(?P<title>[^\n]*)\n+'
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


def parse_admonition(self, m, state):
    token = {
        'type': 'admonition',
        'params': (
            m.group('name'),
            m.group('title'),
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
    rules.remove('admonition')
    children = self.parse(text, state, rules)
    token['children'] = children
    return token


def render_ast_admonition(children, name, title=None, options=None):
    return {
        'type': 'admonition',
        'name': name,
        'title': title,
        'options': options,
        'children': children,
    }


def render_html_admonition(text, name, title=None, options=None):
    html = '<section class="admonition ' + name + '">\n'
    if title:
        html += '<h1>' + title + '</h1>\n'
    if text:
        html += '<div class="admonition-text">\n' + text + '</div>\n'
    return html + '</section>\n'


def register_admonition(md, html_renderer):
    md.block.register_rule('admonition', ADMONITION_PATTERN, parse_admonition)
    md.block.default_rules.append('admonition')

    if md.renderer.NAME == 'ast':
        md.renderer._methods['admonition'] = render_ast_admonition
    elif md.renderer.NAME == 'html':
        md.renderer._methods['admonition'] = html_renderer


def admonition(md):
    register_admonition(md, render_html_admonition)


class Admonition(object):
    def __init__(self):
        self._html_renderers = {}

    def register_html_renderer(self, name, fn):
        self._html_renderers[name] = fn

    def render_html_admonition(self, text, name, title=None, options=None):
        render = self._html_renderers.get(name)
        if render:
            return render(text, title=title, options=options)
        return render_html_admonition(
            text, name, title=title, options=options)

    def __call__(self, md):
        register_admonition(md, self.render_html_admonition)
