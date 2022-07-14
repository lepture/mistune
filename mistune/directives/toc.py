"""
    TOC directive
    ~~~~~~~~~~~~~

    The TOC directive syntax looks like::

        .. toc:: Title
           :level: 3

    "Title" and "level" option can be empty. "level" is an integer less
    than 6, which defines the max heading level writers want to include
    in TOC.
"""

from .base import Directive, parse_options
from ..toc import normalize_toc_item, render_toc_ul


class DirectiveToc(Directive):
    def __init__(self, level=3, heading_id=None):
        self.level = level

        if callable(heading_id):
            self.heading_id = heading_id
        else:
            def heading_id(token, index):
                return 'toc_' + str(index + 1)
            self.heading_id = heading_id

    def parse(self, block, m, state):
        title = m.group('value')
        level = None
        options = parse_options(m)
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

        if level is None:
            level = self.level
        elif level < 1 or level > 6:
            level = self.level

        attrs = {'title': title, 'level': level}
        return {'type': 'toc', 'raw': '', 'attrs': attrs}

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
                toc_items.append(normalize_toc_item(md, tok))

            for sec in sections:
                level = sec['attrs']['level']
                toc = [item for item in toc_items if item[0] <= level]
                sec['raw'] = render_toc_ul(toc)

    def __call__(self, md):
        if md.renderer and md.renderer.NAME == 'html':
            # only works with HTML renderer
            self.register_directive(md, 'toc')
            md.before_render_hooks.append(self.toc_hook)
            md.renderer.register('toc', render_html_toc)


def render_html_toc(renderer, text, title, level):
    if not title:
        title = 'Table of Contents'

    html = '<details class="toc">\n<summary>' + title + '</summary>\n'
    return html + text + '</details>\n'
