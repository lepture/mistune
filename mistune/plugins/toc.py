"""
    TOC plugin
    ~~~~~~~~~~

    This TOC plugin is based on directive plugin. Developers MUST enable
    directive plugin to use this feature. The syntax looks like::

        .. toc:: Title
           :level: 3

    "Title" and "level" option can be empty. "level" is an integer less
    than 6, which defines the max heading level writers want to include
    in TOC.
"""
from .directive import parse_directive_options


def parse_directive_toc(block, m, state):
    title = m.group('value')
    level = None
    options = parse_directive_options(m.group('options'))
    if options:
        level = dict(options).get('level')
        if level:
            try:
                level = int(level)
            except (ValueError, TypeError):
                return {
                    'type': 'block_error',
                    'raw': 'TOC level MUST be integer',
                }

    return {'type': 'toc', 'raw': None, 'params': (title, level)}


def record_toc_heading(text, level, state):
    # we will use this method to replace tokenize_heading
    tid = 'toc_' + str(len(state['toc_headings']) + 1)
    state['toc_headings'].append((tid, text, level))
    return {'type': 'theading', 'text': text, 'params': (level, tid)}


def md_toc_hook(md, tokens, state):
    headings = state.get('toc_headings')
    if not headings:
        return tokens

    # add TOC items into the given location
    default_level = state.get('toc_level', 3)
    headings = list(_cleanup_headings_text(md.inline, headings, state))
    for tok in tokens:
        if tok['type'] == 'toc':
            params = tok['params']
            level = params[1] or default_level
            items = [d for d in headings if d[2] <= level]
            tok['raw'] = items
    return tokens


def render_ast_toc(items, title, level):
    return {
        'type': 'toc',
        'items': [list(d) for d in items],
        'title': title,
        'level': level,
    }


def render_ast_theading(children, level, tid):
    return {
        'type': 'heading', 'children': children,
        'level': level, 'id': tid,
    }


def render_html_toc(items, title, level):
    html = '<section class="toc">\n'
    if title:
        html += '<h1>' + title + '</h1>\n'

    return html + render_toc_ul(items) + '</section>\n'


def render_html_theading(text, level, tid):
    tag = 'h' + str(level)
    return '<' + tag + ' id="' + tid + '">' + text + '</' + tag + '>\n'


def register_toc_plugin(md, level=3):
    def reset_toc_state(md, s, state):
        state['toc_level'] = level
        state['toc_headings'] = []
        return s, state

    md.block.tokenize_heading = record_toc_heading
    # we don't pass any TOC pattern
    md.block.register_rule('directive_toc', None, parse_directive_toc)
    md.before_parse_hooks.append(reset_toc_state)
    md.before_render_hooks.append(md_toc_hook)

    if md.renderer.NAME == 'html':
        md.renderer.register('theading', render_html_theading)
        md.renderer.register('toc', render_html_toc)

    elif md.renderer.NAME == 'ast':
        md.renderer.register('theading', render_ast_theading)
        md.renderer.register('toc', render_ast_toc)


def plugin_toc(md):
    register_toc_plugin(md)


class PluginToc(object):
    def __init__(self, level=3):
        self.level = level

    def __call__(self, md):
        register_toc_plugin(md, self.level)


def extract_toc_items(md, s):
    """Extract TOC headings into list structure of::

        [
          ('toc_1', 'Introduction', 1),
          ('toc_2', 'Install', 2),
          ('toc_3', 'Upgrade', 2),
          ('toc_4', 'License', 1),
        ]

    :param md: Markdown Instance with TOC plugin.
    :param s: text string.
    """
    s, state = md.before_parse(s, {})
    rules = ('newline', 'axt_heading', 'setex_heading')
    md.block.parse(s, state, rules)
    headings = state.get('toc_headings')
    if not headings:
        return []
    return list(_cleanup_headings_text(md.inline, headings, state))


def render_toc_ul(toc):
    """Render a <ul> table of content HTML. The param "toc" should
    be formatted into this structure::

        [
          (toc_id, text, level),
        ]

    For example::

        [
          ('toc-intro', 'Introduction', 1),
          ('toc-install', 'Install', 2),
          ('toc-upgrade', 'Upgrade', 2),
          ('toc-license', 'License', 1),
        ]
    """
    if not toc:
        return ''

    s = '<ul>\n'
    levels = []
    for k, text, level in toc:
        item = '<a href="#{}">{}</a>'.format(k, text)
        if not levels:
            s += '<li>' + item
            levels.append(level)
        elif level == levels[-1]:
            s += '</li>\n<li>' + item
        elif level > levels[-1]:
            s += '\n<ul>\n<li>' + item
            levels.append(level)
        else:
            last_level = levels.pop()
            while levels:
                last_level = levels.pop()
                if level == last_level:
                    s += '</li>\n</ul>\n</li>\n<li>' + item
                    levels.append(level)
                    break
                elif level > last_level:
                    s += '</li>\n<li>' + item
                    levels.append(last_level)
                    levels.append(level)
                    break
                else:
                    s += '</li>\n</ul>\n'
            else:
                levels.append(level)
                s += '</li>\n<li>' + item

    while len(levels) > 1:
        s += '</li>\n</ul>\n'
        levels.pop()

    return s + '</li>\n</ul>\n'


def _cleanup_headings_text(inline, items, state):
    for item in items:
        text = item[1]
        tokens = inline._scan(text, state, inline.rules)
        text = ''.join(_inline_token_text(tok) for tok in tokens)
        yield item[0], text, item[2]


def _inline_token_text(token):
    tok_type = token[0]
    if tok_type == 'inline_html':
        return ''

    if tok_type in {'image', 'link'}:
        return token[2]

    if len(token) == 2:
        return token[1]

    return ''
