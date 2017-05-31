import re
import inspect
from .grammar import BlockGrammar
from .lexer import BlockLexer, InlineLexer
from .renderer import Renderer

_newline_pattern = re.compile(r'\r\n|\r')
_pre_tags = ['pre', 'script', 'style']


def preprocessing(text, tab=4):
    text = _newline_pattern.sub('\n', text)
    text = text.expandtabs(tab)
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


class Markdown(object):
    """The Markdown parser.

    :param renderer: An instance of ``Renderer``.
    :param inline: An inline lexer class or instance.
    :param block: A block lexer class or instance.
    """
    def __init__(self, renderer=None, inline=None, block=None, **kwargs):
        if not renderer:
            renderer = Renderer(**kwargs)
        else:
            kwargs.update(renderer.options)

        self.renderer = renderer

        if inline and inspect.isclass(inline):
            inline = inline(renderer, **kwargs)
        if block and inspect.isclass(block):
            block = block(**kwargs)

        if inline:
            self.inline = inline
        else:
            self.inline = InlineLexer(renderer, **kwargs)

        self.block = block or BlockLexer(BlockGrammar())
        self.footnotes = []
        self.tokens = []

        # detect if it should parse text in block html
        self._parse_block_html = kwargs.get('parse_block_html')

    def __call__(self, text):
        return self.parse(text)

    def render(self, text):
        """Render the Markdown text.

        :param text: markdown formatted text content.
        """
        return self.parse(text)

    def parse(self, text):
        out = self.output(preprocessing(text))

        keys = self.block.def_footnotes

        # reset block
        self.block.def_links = {}
        self.block.def_footnotes = {}

        # reset inline
        self.inline.links = {}
        self.inline.footnotes = {}

        if not self.footnotes:
            return out

        footnotes = filter(lambda o: keys.get(o['key']), self.footnotes)
        self.footnotes = sorted(
            footnotes, key=lambda o: keys.get(o['key']), reverse=True
        )

        body = self.renderer.placeholder()
        while self.footnotes:
            note = self.footnotes.pop()
            body += self.renderer.footnote_item(
                note['key'], note['text']
            )

        out += self.renderer.footnotes(body)
        return out

    def pop(self):
        if not self.tokens:
            return None
        self.token = self.tokens.pop()
        return self.token

    def peek(self):
        if self.tokens:
            return self.tokens[-1]
        return None  # pragma: no cover

    def output(self, text, rules=None):
        self.tokens = self.block(text, rules)
        self.tokens.reverse()

        self.inline.setup(self.block.def_links, self.block.def_footnotes)

        out = self.renderer.placeholder()
        while self.pop():
            out += self.tok()
        return out

    def tok(self):
        t = self.token['type']

        # sepcial cases
        if t.endswith('_start'):
            t = t[:-6]

        return getattr(self, 'output_%s' % t)()

    def tok_text(self):
        text = self.token['text']
        while self.peek()['type'] == 'text':
            text += '\n' + self.pop()['text']
        return self.inline(text)

    def output_newline(self):
        return self.renderer.newline()

    def output_hrule(self):
        return self.renderer.hrule()

    def output_heading(self):
        return self.renderer.header(
            self.inline(self.token['text']),
            self.token['level'],
            self.token['text'],
        )

    def output_code(self):
        return self.renderer.block_code(
            self.token['text'], self.token['lang']
        )

    def output_table(self):
        aligns = self.token['align']
        aligns_length = len(aligns)
        cell = self.renderer.placeholder()

        # header part
        header = self.renderer.placeholder()
        for i, value in enumerate(self.token['header']):
            align = aligns[i] if i < aligns_length else None
            flags = {'header': True, 'align': align}
            cell += self.renderer.table_cell(self.inline(value), **flags)

        header += self.renderer.table_row(cell)

        # body part
        body = self.renderer.placeholder()
        for i, row in enumerate(self.token['cells']):
            cell = self.renderer.placeholder()
            for j, value in enumerate(row):
                align = aligns[j] if j < aligns_length else None
                flags = {'header': False, 'align': align}
                cell += self.renderer.table_cell(self.inline(value), **flags)
            body += self.renderer.table_row(cell)

        return self.renderer.table(header, body)

    def output_block_quote(self):
        body = self.renderer.placeholder()
        while self.pop()['type'] != 'block_quote_end':
            body += self.tok()
        return self.renderer.block_quote(body)

    def output_list(self):
        ordered = self.token['ordered']
        body = self.renderer.placeholder()
        while self.pop()['type'] != 'list_end':
            body += self.tok()
        return self.renderer.list(body, ordered)

    def output_list_item(self):
        body = self.renderer.placeholder()
        while self.pop()['type'] != 'list_item_end':
            if self.token['type'] == 'text':
                body += self.tok_text()
            else:
                body += self.tok()

        return self.renderer.list_item(body)

    def output_loose_item(self):
        body = self.renderer.placeholder()
        while self.pop()['type'] != 'list_item_end':
            body += self.tok()
        return self.renderer.list_item(body)

    def output_footnote(self):
        self.inline._in_footnote = True
        body = self.renderer.placeholder()
        key = self.token['key']
        while self.pop()['type'] != 'footnote_end':
            body += self.tok()
        self.footnotes.append({'key': key, 'text': body})
        self.inline._in_footnote = False
        return self.renderer.placeholder()

    def output_close_html(self):
        text = self.token['text']
        return self.renderer.block_html(text)

    def output_open_html(self):
        text = self.token['text']
        tag = self.token['tag']
        if self._parse_block_html and tag not in _pre_tags:
            text = self.inline(text, rules=self.inline.inline_html_rules)
        extra = self.token.get('extra') or ''
        html = '<%s%s>%s</%s>' % (tag, extra, text, tag)
        return self.renderer.block_html(html)

    def output_paragraph(self):
        return self.renderer.paragraph(self.inline(self.token['text']))

    def output_text(self):
        return self.renderer.paragraph(self.tok_text())


def markdown(text, escape=True, **kwargs):
    """Render markdown formatted text to html.

    :param text: markdown formatted text content.
    :param escape: if set to False, all html tags will not be escaped.
    :param use_xhtml: output with xhtml tags.
    :param hard_wrap: if set to True, it will use the GFM line breaks feature.
    :param parse_block_html: parse text only in block level html.
    :param parse_inline_html: parse text only in inline level html.
    """
    return Markdown(escape=escape, **kwargs)(text)
