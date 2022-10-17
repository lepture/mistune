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
        collapse = False
        options = parse_options(m)
        if options:
            d_options = dict(options)
            collapse = 'collapse' in d_options
            level = d_options.get('level')
            if level:
                try:
                    level = self._parse_level(level, 'level')
                except IntegerTokenError as ex:
                    return {
                        'type': 'block_error',
                        'raw': 'TOC {token} MUST be integer'.format(token=ex.token_name),
                    }

        if level is None:
            level = self.level
        elif level < 1 or level > 6:
            level = self.level

        attrs = {'title': title, 'level': level, 'collapse': collapse}
        return {'type': 'toc', 'raw': '', 'attrs': attrs}

    @staticmethod
    def _parse_level(token, token_name):
        try:
            return int(token)
        except (ValueError, TypeError):
            raise IntegerTokenError(token_name)

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


def render_html_toc(renderer, text, title, level, collapse=False):
    if not title:
        title = 'Table of Contents'

    html = '<details class="toc"'
    if not collapse:
        html += ' open'
    html += '>\n<summary>' + title + '</summary>\n'
    return html + text + '</details>\n'

class IntegerTokenError(ValueError):
    """
    Raised if a token cannot be converted to an int.
    """
    def __init__(self, token_name, *args, **kwargs):
        self.token_name = token_name
        super(IntegerTokenError, self).__init__(*args, **kwargs)
