from ._base import DirectivePlugin


class Admonition(DirectivePlugin):
    SUPPORTED_NAMES = {
        "attention", "caution", "danger", "error", "hint",
        "important", "note", "tip", "warning",
    }

    def parse(self, block, m, state):
        options = self.parse_options(m)
        name = self.parse_name(m)
        title = self.parse_title(m)
        attrs = {'name': name, 'options': options}

        content = self.parse_content(m)
        children = self.parse_tokens(block, content, state)
        return {
            'type': 'admonition',
            'title': title or '',
            'children': children,
            'attrs': attrs,
        }

    def __call__(self, directive, md):
        for name in self.SUPPORTED_NAMES:
            directive.register(name, self.parse)

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
