
class BaseRenderer(object):
    NAME = 'base'
    IS_TREE = False

    def __init__(self):
        self._methods = {}

    def _get_method(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self._methods.get(name)


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
            'children': children,
            'language': language
        }

    def _create_default_method(self, name):
        def __ast(children):
            return {'type': name, 'children': children}
        return __ast

    def _get_method(self, name):
        method = super(AstRenderer, self)._get_method(name)
        if not method:
            method = self._create_default_method(name)
        return method


class HTMLRenderer(BaseRenderer):
    NAME = 'html'
    IS_TREE = False

    def text(self, text):
        return text

    def link(self, link, text=None, title=None):
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
        return html

    def footnote_ref(self, key, index):
        html = (
            '<sup class="footnote-ref" id="fnref-%d">'
            '<a href="#fn-%d">%d</a></sup>'
        ) % (index, index, index)
        return html

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
