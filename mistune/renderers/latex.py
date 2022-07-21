from ..core import BaseRenderer


__all__ = ['LaTeXRenderer']


class LaTeXRenderer(BaseRenderer):
    def text(self, text):
        return text

    def emphasis(self, text):
        return r'\textit{' + text + '}'

    def strong(self, text):
        return r'\textbf{' + text + '}'

    def link(self, text, url, title=None):
        if text == url:
            return '\url{' + url + '}'
        return r'\href{' + url + '}{' + text + '}'

    def image(self, text, url, title=None):
        return (
            '\\begin{figure}\n'
            '  \\caption{' + text + '}\n'
            '  \\centering\n'
            '    \\includegraphics{' + url + '}\n'
            '\\end{figure}\n'
        )

    def codespan(self, text):
        return r'\verb|' + text + '|'

    def linebreak(self):
        return '\\newline\n'

    def softbreak(self):
        return '\n'

    def inline_html(self, html):
        if self._escape:
            return escape(html)
        return html

    def paragraph(self, text):
        return '\n' + text + '\n'

    def heading(self, text, level, **attrs):
        tag = 'h' + str(level)
        html = '<' + tag
        _id = attrs.get('id')
        if _id:
            html += ' id="' + _id + '"'
        return html + '>' + text + '</' + tag + '>\n'

    def blank_line(self):
        return '\n'

    def thematic_break(self):
        return '\\hrulefill\n'

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
        return '\\begin{displayquote}\n' + text + '\\end{displayquote}\n'

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
