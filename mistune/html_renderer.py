from .core import BaseRenderer
from .util import escape, striptags, safe_entity


class HTMLRenderer(BaseRenderer):
    NAME = 'html'
    HARMFUL_PROTOCOLS = (
        'javascript:',
        'vbscript:',
        'file:',
        'data:',
    )
    GOOD_DATA_PROTOCOLS = (
        'data:image/gif;',
        'data:image/png;',
        'data:image/jpeg;',
        'data:image/webp;',
    )

    def __init__(self, escape=True, allow_harmful_protocols=None):
        super(HTMLRenderer, self).__init__()
        self._allow_harmful_protocols = allow_harmful_protocols
        self._escape = escape

    def _safe_url(self, url):
        if self._allow_harmful_protocols is True:
            return url

        _url = url.lower()
        if self._allow_harmful_protocols and \
            _url.startswith(tuple(self._allow_harmful_protocols)):
            return url

        if _url.startswith(self.HARMFUL_PROTOCOLS) and \
            not _url.startswith(self.GOOD_DATA_PROTOCOLS):
            return '#harmful-link'
        return url

    def text(self, text):
        if self._escape:
            return escape(text)
        return safe_entity(text)

    def link(self, text, url, title=None):
        s = '<a href="' + self._safe_url(url) + '"'
        if title:
            s += ' title="' + title + '"'
        return s + '>' + text + '</a>'

    def image(self, text, url, title=None):
        src = self._safe_url(url)
        alt = escape(striptags(text))
        s = '<img src="' + src + '" alt="' + alt + '"'
        if title:
            s += ' title="' + title + '"'
        return s + ' />'

    def emphasis(self, text):
        return '<em>' + text + '</em>'

    def strong(self, text):
        return '<strong>' + text + '</strong>'

    def codespan(self, text):
        return '<code>' + text + '</code>'

    def linebreak(self):
        return '<br />\n'

    def softbreak(self):
        return '\n'

    def inline_html(self, html):
        if self._escape:
            return escape(html)
        return html

    def paragraph(self, text):
        return '<p>' + text + '</p>\n'

    def heading(self, text, level, **attrs):
        tag = 'h' + str(level)
        html = '<' + tag
        _id = attrs.get('id')
        if _id:
            html += ' id="' + _id + '"'
        return html + '>' + text + '</' + tag + '>\n'

    def blank_line(self):
        return ''

    def thematic_break(self):
        return '<hr />\n'

    def block_text(self, text):
        return text

    def block_code(self, code, info=None):
        html = '<pre><code'
        if info is not None:
            info = info.strip()
        if info:
            lang = info.split(None, 1)[0]
            html += ' class="language-' + lang + '"'
        return html + '>' + escape(code) + '</code></pre>\n'

    def block_quote(self, text):
        return '<blockquote>\n' + text + '</blockquote>\n'

    def block_html(self, html):
        if self._escape:
            return '<p>' + escape(html) + '</p>\n'
        return html + '\n'

    def block_error(self, html):
        return '<div class="error">' + html + '</div>\n'

    def list(self, text, ordered, **attrs):
        if ordered:
            html = '<ol'
            start = attrs.get('start')
            if start is not None:
                html += ' start="' + str(start) + '"'
            return html + '>\n' + text + '</ol>\n'
        return '<ul>\n' + text + '</ul>\n'

    def list_item(self, text, **attrs):
        return '<li>' + text + '</li>\n'
