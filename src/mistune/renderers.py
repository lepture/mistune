from .scanner import escape


class BaseRenderer(object):
    NAME = 'base'
    IS_TREE = False

    def __init__(self):
        self._methods = {}

    def _get_method(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            method = self._methods.get(name)
            if not method:
                raise AttributeError('No renderer "{!r}"'.format(name))
            return method


class AstRenderer(BaseRenderer):
    NAME = 'ast'
    IS_TREE = True

    def text(self, text):
        return {'type': 'text', 'text': text}

    def link(self, link, text=None, title=None):
        return {'type': 'link', 'link': link, 'text': text, 'title': title}

    def image(self, src, alt="", title=None):
        return {'type': 'image', 'src': src, 'alt': alt, 'title': title}

    def codespan(self, text):
        return {'type': 'codespan', 'text': text}

    def linebreak(self):
        return {'type': 'linebreak'}

    def inline_html(self, html):
        return {'type': 'inline_html', 'text': html}

    def footnote_ref(self, key, index):
        return {'type': 'footnote_ref', 'key': key, 'index': index}

    def heading(self, children, level):
        return {'type': 'heading', 'children': children, 'level': level}

    def thematic_break(self):
        return {'type': 'thematic_break'}

    def block_code(self, children, language=None):
        return {
            'type': 'block_code',
            'text': children,
            'language': language
        }

    def block_html(self, children):
        return {'type': 'block_html', 'text': children}

    def list(self, children, ordered=False, start=None):
        token = {'type': 'list', 'children': children, 'ordered': ordered}
        if start is not None:
            token['start'] = start
        return token

    def footnote_item(self, children, key, index):
        return {
            'type': 'footnote_item',
            'children': children,
            'key': key,
            'index': index,
        }

    def _create_default_method(self, name):
        def __ast(children):
            return {'type': name, 'children': children}
        return __ast

    def _get_method(self, name):
        try:
            return super(AstRenderer, self)._get_method(name)
        except AttributeError:
            return self._create_default_method(name)


class HTMLRenderer(BaseRenderer):
    NAME = 'html'
    IS_TREE = False
    HARMFUL_PROTOCOLS = {
        'javascript:',
        'vbscript:',
        'data:',
    }

    def __init__(self, escape=True, allow_harmful_protocols=None):
        super(HTMLRenderer, self).__init__()
        self._escape = escape
        self._allow_harmful_protocols = allow_harmful_protocols

    def text(self, text):
        return text

    def link(self, link, text=None, title=None):
        if text is None:
            text = link

        if self._allow_harmful_protocols is None:
            schemes = self.HARMFUL_PROTOCOLS
        elif self._allow_harmful_protocols is True:
            schemes = None
        else:
            allowed = set(self._allow_harmful_protocols)
            schemes = self.HARMFUL_PROTOCOLS - allowed

        if schemes:
            for s in schemes:
                if link.startswith(s):
                    link = '#harmful-link'
                    break

        s = '<a href="' + link + '"'
        if title:
            s += ' title="' + title + '"'
        return s + '>' + (text or link) + '</a>'

    def image(self, src, alt="", title=None):
        s = '<img src="' + src + '" alt="' + alt + '"'
        if title:
            s += ' title="' + title + '"'
        return s + '/>'

    def emphasis(self, text):
        return '<em>' + text + '</em>'

    def strong(self, text):
        return '<strong>' + text + '</strong>'

    def codespan(self, text):
        return '<code>' + text + '</code>'

    def strikethrough(self, text):
        return '<del>' + text + '</del>'

    def linebreak(self):
        return '<br />\n'

    def inline_html(self, html):
        if self._escape:
            return escape(html)
        return html

    def footnote_ref(self, key, index):
        i = str(index)
        html = '<sup class="footnote-ref" id="fnref-' + i + '">'
        return html + '<a href="#fn-' + i + '">' + i + '</a></sup>'

    def paragraph(self, text):
        return '<p>' + text + '</p>\n'

    def heading(self, text, level):
        tag = 'h' + str(level)
        return '<' + tag + '>' + text + '</' + tag + '>\n'

    def thematic_break(self):
        return '<hr />\n'

    def block_code(self, code, language=None):
        html = '<pre><code'
        if language:
            html += ' class="language-' + language + '"'
        return html + '>' + code + '</code></pre>\n'

    def block_quote(self, text):
        return '<blockquote>\n' + text + '</blockquote>\n'

    def block_html(self, html):
        if not self._escape:
            return html + '\n'
        return '<p>' + escape(html) + '</p>\n'

    def list(self, text, ordered=False, start=None):
        if ordered:
            html = '<ol'
            if start:
                html += ' start="' + str(start) + '"'
            return html + '>\n' + text + '</ol>\n'
        return '<ul>\n' + text + '</ul>\n'

    def list_item(self, text):
        return '<li>' + text + '</li>\n'

    def footnote(self, text):
        return (
            '<section class="footnote">\n<ol>\n'
            + text +
            '</ol>\n</section>\n'
        )

    def footnote_item(self, text, key, index):
        i = str(index)
        back = '<a href="#fnref-' + i + '" class="footnote">&#8617;</a>'

        text = text.rstrip()
        if text.endswith('</p>'):
            text = text[:-4] + back + '</p>'
        else:
            text = text + back
        return '<li id="fn-' + i + '">' + text + '</li>\n'
