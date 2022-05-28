from .base import Directive, parse_options, parse_children


class Admonition(Directive):
    SUPPORTED_NAMES = {
        "attention", "caution", "danger", "error", "hint",
        "important", "note", "tip", "warning",
    }

    def parse(self, block, m, state):
        options = parse_options(m)

        name = m.group('name')
        title = m.group('value')
        attrs = {'name': name, 'title': title, 'options': options}

        children = parse_children(block, m, state)
        return {
            'type': 'admonition',
            'children': children,
            'attrs': attrs,
        }

    def __call__(self, md):
        for name in self.SUPPORTED_NAMES:
            self.register_directive(md, name)

        if md.renderer.NAME == 'html':
            md.renderer.register('admonition', render_admonition)


def render_admonition(self, text, name, title="", options=None):
    html = '<section class="admonition ' + name + '">\n'
    if not title:
        title = name.capitalize()
    if title:
        html += '<p class="admonition-title">' + title + '</p>\n'
    if text:
        html += text
    return html + '</section>\n'
