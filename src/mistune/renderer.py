
class ASTRenderer(object):
    IS_AST = True


class HTMLRenderer(object):
    IS_AST = False

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
        return '<br/>'

    def inline_html(self, html):
        return html

    def footnote_ref(self, key, index):
        html = (
            '<sup class="footnote-ref" id="fnref-%d">'
            '<a href="#fn-%d">%d</a></sup>'
        ) % (index, index, index)
        return html
