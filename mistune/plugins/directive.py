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
import os
from mistune.markdown import preprocess

__all__ = ['plugin_directive', 'PluginDirective']


DIRECTIVE_PATTERN = re.compile(
    r'\.\.( +)(?P<name>[a-zA-Z0-9_-]+)\:\: *(?P<value>[^\n]*)\n+'
    r'(?P<options>(?:  \1 {0,3}\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)'
    r'(?P<text>(?:  \1 {0,3}[^\n]*\n+)*)'
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


def _parse_include(self, filepath, options, state):
    source_file = state.get('__file__')
    if not source_file:
        return {
            'type': 'block_error',
            'raw': 'Missing source file configuration',
        }

    dest = os.path.join(os.path.dirname(source_file), filepath)
    dest = os.path.normpath(dest)
    if dest == source_file:
        return {
            'type': 'block_error',
            'raw': 'Could not include self: ' + filepath,
        }

    if not os.path.isfile(dest):
        return {
            'type': 'block_error',
            'raw': 'Could not find file: ' + filepath,
        }

    with open(dest, 'rb') as f:
        content = f.read()
        text = content.decode('utf-8')

    if not options:
        ext = os.path.splitext(filepath)[1]
        if ext in {'.md', '.markdown', '.mkd'}:
            text, state = preprocess(text, {'__file__': dest})
            return self.parse(text, state)
        if ext in {'.html', '.xhtml', '.htm'}:
            return {'type': 'block_html', 'text': text}

    return {
        'type': 'include',
        'text': text,
        'params': (filepath, dest, options)
    }


def parse_directive(self, m, state):
    name = m.group('name')
    value = m.group('value')
    options = _parse_options(m.group('options'))
    if name == 'include':
        return _parse_include(self, value, options, state)

    token = {
        'type': 'directive',
        'params': (name, value, options)
    }
    text = m.group('text')
    if not text.strip():
        token['children'] = []
        return token

    leading = len(m.group(1)) + 2
    text = '\n'.join(_parse_text_lines(text, leading)).lstrip('\n') + '\n'
    rules = list(self.rules)
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


def render_ast_include(text, relpath, abspath=None, options=None):
    return {
        'type': text,
        'relpath': relpath,
        'abspath': abspath,
        'options': options,
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


def render_html_include(text, relpath, abspath=None, options=None):
    html = '<section class="directive-include" data-relpath="'
    return html + relpath + '">\n' + text + '</section>\n'


def register_directive(md, html_renderer):
    md.block.register_rule('directive', DIRECTIVE_PATTERN, parse_directive)
    md.block.rules.append('directive')

    if md.renderer.NAME == 'ast':
        md.renderer.register('directive', render_ast_directive)
        md.renderer.register('include', render_ast_include)
    elif md.renderer.NAME == 'html':
        md.renderer.register('directive', render_html_directive)
        md.renderer.register('include', render_html_include)


def plugin_directive(md):
    register_directive(md, render_html_directive)


class PluginDirective(object):
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
