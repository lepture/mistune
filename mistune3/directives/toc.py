"""
    TOC directive
    ~~~~~~~~~~~~~

    The TOC directive syntax looks like::

        .. toc:: Title
           :depth: 3

    "Title" and "depth" option can be empty. "depth" is an integer less
    than 6, which defines the max heading level writers want to include
    in TOC.
"""

from .base import Directive, parse_options
from ..util import striptags


class DirectiveToc(Directive):
    def __init__(self, depth=3):
        self.depth = depth

    def parse(self, block, m, state):
        title = m.group('value')
        depth = None
        options = parse_options(m)
        if options:
            depth = dict(options).get('depth')
            if depth:
                try:
                    depth = int(depth)
                except (ValueError, TypeError):
                    return {
                        'type': 'block_error',
                        'raw': 'TOC depth MUST be integer',
                    }

        if depth is None:
            depth = self.depth
        elif depth < 1 or depth > 6:
            depth = self.depth

        attrs = {'title': title, 'depth': depth}
        return {'type': 'toc', 'raw': [], 'attrs': attrs}

    def heading_id(self, token, index):
        return 'hid-' + str(index + 1)

    def toc_hook(self, md, state):
        sections = []
        headings = []

        for tok in state.tokens:
            if tok['type'] == 'toc':
                sections.append(tok)
            elif tok['type'] == 'heading':
                headings.append(tok)

        if sections:
            toc_items = []
            # adding ID for each heading
            for i, tok in enumerate(headings):
                tok['attrs']['id'] = self.heading_id(tok, i)
                toc_items.append(cleanup_toc_item(md, tok))

            for sec in sections:
                depth = sec['attrs']['depth']
                sec['raw'] = [item for item in toc_items if item[0] <= depth]

    def __call__(self, md):
        if md.renderer.NAME == 'html':
            # only works with HTML renderer
            self.register_directive(md, 'toc')
            md.before_render_hooks.append(self.toc_hook)
            md.renderer.register('toc', render_html_toc)


def render_html_toc(self, items, title, depth):
    html = '<details class="toc">\n'
    if title:
        html += '<summary>' + title + '</summary>\n'

    return html + render_toc_ul(items) + '</details>\n'


def cleanup_toc_item(md, tok):
    text = tok['text']
    html = md.inline(text, {})
    text = striptags(html)
    attrs = tok['attrs']
    return attrs['level'], attrs['id'], text


def render_toc_ul(toc):
    """Render a <ul> table of content HTML. The param "toc" should
    be formatted into this structure::

        [
          (level, id, text),
        ]

    For example::

        [
          (1, 'toc-intro', 'Introduction'),
          (2, 'toc-install', 'Install'),
          (2, 'toc-upgrade', 'Upgrade'),
          (1, 'toc-license', 'License'),
        ]
    """
    if not toc:
        return ''

    s = '<ul>\n'
    levels = []
    for level, k, text in toc:
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
