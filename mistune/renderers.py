from .util import escape, escape_html


class BaseRenderer(object):
    NAME = 'base'

    def __init__(self):
        self.__methods = {}

    def register(self, name, method):
        # bind self into renderer method
        self.__methods[name] = lambda *arg, **kwargs: method(self, *arg, **kwargs)

    def _get_method(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            method = self.__methods.get(name)
            if not method:
                raise AttributeError('No renderer "{!r}"'.format(name))
            return method

    def _iter_tokens(self, tokens):
        for tok in tokens:
            func = self._get_method(tok['type'])

            if 'raw' in tok:
                children = tok['raw']
            elif 'children' in tok:
                children = tok['children']
            else:
                yield func()
                continue

            attrs = tok.get('attrs')
            if attrs:
                yield func(children, **attrs)
            else:
                yield func(children)

    def __call__(self, tokens):
        return ''.join(self._iter_tokens(tokens))

    def finalize(self, result, state):
        return result.strip()



class HTMLRenderer(BaseRenderer):
    NAME = 'html'
    HARMFUL_PROTOCOLS = {
        'javascript:',
        'vbscript:',
        'data:',
    }

    def __init__(self, escape=True, allow_harmful_protocols=None):
        super(HTMLRenderer, self).__init__()
        self._escape = escape
        self._allow_harmful_protocols = allow_harmful_protocols

    def _safe_url(self, url):
        if self._allow_harmful_protocols is None:
            schemes = self.HARMFUL_PROTOCOLS
        elif self._allow_harmful_protocols is True:
            schemes = None
        else:
            allowed = set(self._allow_harmful_protocols)
            schemes = self.HARMFUL_PROTOCOLS - allowed

        if schemes:
            for s in schemes:
                if url.lower().startswith(s):
                    url = '#harmful-link'
                    break
        return url

    def text(self, text):
        if self._escape:
            return escape(text)
        return escape_html(text)

    def link(self, text, url, title=None):
        s = '<a href="' + self._safe_url(url) + '"'
        if title:
            s += ' title="' + escape_html(title) + '"'
        return s + '>' + text + '</a>'

    def image(self, text, url, title=None):
        src = self._safe_url(url)
        alt = escape_html(text)
        s = '<img src="' + src + '" alt="' + alt + '"'
        if title:
            s += ' title="' + escape_html(title) + '"'
        return s + ' />'

    def emphasis(self, text):
        return '<em>' + text + '</em>'

    def strong(self, text):
        return '<strong>' + text + '</strong>'

    def codespan(self, text):
        return '<code>' + escape(text) + '</code>'

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

    def heading(self, text, level):
        tag = 'h' + str(level)
        return '<' + tag + '>' + text + '</' + tag + '>\n'

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
            lang = escape_html(lang)
            html += ' class="language-' + lang + '"'
        return html + '>' + escape(code) + '</code></pre>\n'

    def block_quote(self, text):
        return '<blockquote>' + text + '</blockquote>\n'

    def block_html(self, html):
        if not self._escape:
            return html + '\n'
        return '<p>' + escape(html) + '</p>\n'

    def block_error(self, html):
        return '<div class="error">' + html + '</div>\n'

    def list(self, text, ordered, start=None, depth=None, tight=True):
        if ordered:
            html = '<ol'
            if start is not None:
                html += ' start="' + str(start) + '"'
            return html + '>' + text + '\n</ol>\n'
        return '<ul>\n' + text + '</ul>\n'

    def list_item(self, text):
        return '<li>' + text + '</li>\n'
