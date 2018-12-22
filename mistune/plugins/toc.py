from mistune.renderers import HTMLRenderer


class TocRenderer(HTMLRenderer):
    def __init__(self, toc_level=3, escape=True):
        super(TocRenderer, self).__init__(escape=escape)
        self._toc_level = 3
        self._tocs = []

    def heading(self, text, level):
        if level > self._toc_level:
            return super(TocRenderer, self).heading(text, level)

        k = self.generate_heading_id(text, level)
        self._tocs.append((k, text, level))

        tag = 'h' + str(level)
        html = '<' + tag + ' id="' + k + '">'
        return html + text + '</' + tag + '>\n'

    def generate_heading_id(self, text, level):
        return 'toc-' + str(len(self._tocs) + 1)

    def render_toc(self):
        html = render_html_toc(self._tocs)
        self._tocs = []
        return '<section class="toc">' + html + '<section>\n'


def render_html_toc(toc):
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
                levels.append(level)
                s += '</li>\n</ul>\n</li>\n<li>' + item

    while len(levels) > 1:
        s += '</li>\n</ul>\n'
        levels.pop()

    return s + '</li>\n</ul>\n'
