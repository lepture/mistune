# coding: utf-8
"""
    mistune
    ~~~~~~~

    Yet another markdown parser, inspired by marked in JavaScript.

    :copyright: (c) 2014 by Hsiaoming Yang.
"""

import re
from cgi import escape
from collections import OrderedDict

__version__ = '0.1.0'
__author__ = 'Hsiaoming Yang <me@lepture.com>'
__all__ = [
    'BlockGrammar', 'BlockLexer',
    'InlineGrammar', 'InlineLexer',
    'Parser', 'markdown',
]


def _pure_pattern(regex):
    return re.sub('(^|[^\[])\^', '\1', regex.pattern)


def preprocessing(text, tab=4):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = text.replace('\t', ' ' * tab)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


class BlockGrammar(object):
    _tag = (
        r'(?!(?:'
        r'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|'
        r'var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|'
        r'span|br|wbr|ins|del|img)\b)\w+(?!:/|[^\w\s@]*@)\b'
    )

    newline = re.compile(r'^\n+')
    block_code = re.compile(r'^( {4}[^\n]+\n*)+')
    fences = re.compile(
        r'^ *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )
    hr = re.compile(r'^(?: *[-*_]){3,} *(?:\n+|$)')
    heading = re.compile(r'^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')
    lheading = re.compile(r'^([^\n]+)\n *(=|-){2,} *(?:\n+|$)')
    blockquote = re.compile(r'^( *>[^\n]+(\n[^\n]+)*\n*)+')
    list_block = re.compile(
        r'^( *)([*+-]|\d+\.) [\s\S]+?'
        r'(?:'
        r'\n+(?=(?: *[-*_]){3,} *(?:\n+|$))' # hr
        r'|'
        r'\n{2,}'
        r'(?! )'
        r'(?!\1(?:[*+-]|\d+\.) )\n*'
        r'|'
        r'\s*$)'
    )
    list_item = re.compile(
        r'^(( *)(?:[*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[*+-]|\d+\.) )[^\n]*)*)',
        flags=re.M
    )
    list_pure_bullet = re.compile(r'(?:[*+-]|\d\.)')
    list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
    def_links = re.compile(
        r'^ *\[([^^\]]+)\]: *'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'
    )
    def_footnotes = re.compile(
        r'^\[\^([^\]]+)\]: *('
        r'[^\n]*(?:\n+|$)'  # [^key]:
        r'(?: {1,}[^\n]*(?:\n+|$))*'
        r')'
    )
    paragraph = re.compile(
        r'^((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s|%s|%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(fences).replace('\\1', '\\2'),
            _pure_pattern(list_block).replace('\\1', '\\3'),
            _pure_pattern(hr),
            _pure_pattern(heading),
            _pure_pattern(lheading),
            _pure_pattern(blockquote),
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
            '<' + _tag,
        )
    )
    html = re.compile(
        r'^ *(?:%s|%s|%s) *(?:\n{2,}|\s*$)' % (
            r'<!--[\s\S]*?-->',
            r'<(%s)[\s\S]+?<\/\1>' % _tag,
            r'''<%s(?:"[^"]*}|'[^']*'|[^'">])*?>''' % _tag,
        )
    )
    table = re.compile(
        r'^ *\|(.+)\n *\|( *[-:]+[-| :]*)\n((?: *\|.*(?:\n|$))*)\n*'
    )
    nptable = re.compile(
        r'^ *(\S.*\|.*)\n *([-:]+ *\|[-| :]*)\n((?:.*\|.*(?:\n|$))*)\n*'
    )
    text = re.compile(r'^[^\n]+')


class BlockLexer(object):
    def __init__(self, rules=None, **kwargs):
        self.options = kwargs

        self.tokens = []
        self.def_links = OrderedDict()
        self.def_footnotes = OrderedDict()

        if not rules:
            rules = BlockGrammar()

        self.rules = rules

    def __call__(self, src, methods=None):
        return self.parse(src, methods)

    def parse(self, src, methods=None):
        src = src.rstrip('\n')

        if not methods:
            methods = [
                'newline', 'block_code', 'fences', 'heading',
                'nptable', 'lheading', 'hr', 'blockquote',
                'list_block', 'html', 'def_links', 'def_footnotes',
                'table', 'paragraph', 'text'
            ]

        def manipulate(src):
            for key in methods:
                rule = getattr(self.rules, key)
                m = rule.match(src)
                if not m:
                    continue
                getattr(self, 'parse_%s' % key)(m)
                return m
            return False

        while src:
            m = manipulate(src)
            if m is not False:
                src = src[len(m.group(0)):]
                continue
            if src:
                raise RuntimeError('Infinite loop at: %s' % src)
        return self.tokens

    def parse_newline(self, m):
        length = len(m.group(0))
        if length > 1:
            self.tokens.append({'type': 'space'})

    def parse_block_code(self, m):
        code = m.group(0)
        pattern = re.compile(r'^ {4}', re.M)
        code = pattern.sub(code, '')
        self.tokens.append({
            'type': 'code',
            'lang': None,
            'text': code,
        })

    def parse_fences(self, m):
        self.tokens.append({
            'type': 'code',
            'lang': m.group(2),
            'text': m.group(3),
        })

    def parse_heading(self, m):
        self.tokens.append({
            'type': 'heading',
            'level': len(m.group(1)),
            'text': m.group(2),
        })

    def parse_lheading(self, m):
        """Parse setext heading."""
        self.tokens.append({
            'type': 'heading',
            'level': 1 if m.group(2) == '=' else 2,
            'text': m.group(1),
        })

    def parse_hr(self, m):
        self.tokens.append({'type': 'hr'})

    def parse_list_block(self, m):
        bull = m.group(2)
        self.tokens.append({
            'type': 'list_start',
            'ordered': len(bull) > 1,
        })
        cap = m.group(0)
        self._process_list_item(cap, bull)
        self.tokens.append({'type': 'list_end'})

    def _process_list_item(self, cap, bull):
        methods = [
            'newline', 'block_code', 'fences', 'lheading', 'hr',
            'blockquote', 'list_block', 'html', 'text',
        ]

        cap = self.rules.list_item.findall(cap)

        _next = False
        l = len(cap)

        for i in range(l):
            item = cap[i][0]

            # remove the bullet
            space = len(item)
            item = self.rules.list_bullet.sub('', item)

            # outdent
            if '\n ' in item:
                space = space - len(item)
                item = re.sub(r'^ {1,%d}' % space, '', item, re.M)

            # determine if the next list item belongs here
            if self.options.get('smart_lists') and i + 1 < length:
                b = self.rules.list_pure_bullet.match(cap[i + 1][0])
                b = b.group(0)
                # bullet type changed
                if bull != b and not (len(bull) > 1 and len(b) > 1):
                    # TODO
                    #src = '\n'.join(m.group([i+1:]))
                    pass

            # determin whether item is loose or not
            loose = _next
            if not loose and re.search(r'\n\n(?!\s*$)', item):
                loose = True
            if i != l:
                _next = item[len(item)-1] == '\n'
                if not loose:
                    loose = _next

            if loose:
                t = 'loose_item_start'
            else:
                t = 'list_item_start'

            self.tokens.append({'type': t})
            # recurse
            self.parse(item, methods)
            self.tokens.append({'type': 'list_item_end'})

    def parse_blockquote(self, m):
        self.tokens.append({'type': 'blockquote_start'})
        cap = m.group(0)
        cap = re.sub(r'^ *> ?', '', cap, flags=re.M)
        self.parse(cap)
        self.tokens.append({'type': 'blockquote_end'})

    def parse_def_links(self, m):
        key = m.group(1).lower()
        self.def_links[key] = {
            'link': m.group(2),
            'title': m.group(3),
        }

    def parse_def_footnotes(self, m):
        key = m.group(1).lower()
        self.def_footnotes[key] = {
            'index': 0,
            'text': m.group(2),
        }

    def parse_table(self, m):
        item = self._process_table(m)

        cells = re.sub(r'(?: *\| *)?\n$', '', m.group(3))
        cells = cells.split('\n')
        for i, v in enumerate(cells):
            v = re.sub(r'^ *\| *| *\| *$', '', v)
            cells[i] = re.split(r' *\| *', v)

        item['cells'] = cells
        self.tokens.append(item)

    def parse_nptable(self, m):
        item = self._process_table(m)

        cells = re.sub(r'\n$', '', m.group(3))
        cells = cells.split('\n')
        for i, v in enumerate(cells):
            cells[i] = re.split(r' *\| *', v)

        item['cells'] = cells
        self.tokens.append(item)

    def _process_table(self, m):
        header = re.sub(r'^ *| *\| *$', '', m.group(1))
        header = re.split(r' *\| *', header)
        align = re.sub(r' *|\| *$', '', m.group(2))
        align = re.split(r' *\| *', align)

        for i, v in enumerate(align):
            if re.search(r'^ *-+: *$', v):
                align[i] = 'right'
            elif re.search(r'^ *:-+: *$', v):
                align[i] = 'center'
            elif re.search(r'^ *:-+ *$', v):
                align[i] = 'left'
            else:
                align[i] = None

        item = {
            'type': 'table',
            'header': header,
            'align': align,
        }
        return item

    def parse_html(self, m):
        pre = m.group(1) in ['pre', 'script', 'style']
        if 'sanitize' in self.options and self.options['sanitize']:
            t = 'paragraph'
        else:
            t = 'html'
        text = m.group(0)
        self.tokens.append({
            'type': t,
            'pre': pre,
            'text': text
        })

    def parse_paragraph(self, m):
        text = m.group(1).rstrip('\n')
        self.tokens.append({'type': 'paragraph', 'text': text})

    def parse_text(self, m):
        text = m.group(0)
        self.tokens.append({'type': 'text', 'text': text})


class InlineGrammar(object):
    escape = re.compile(r'^\\([\\`*{}\[\]()#+\-.!_>~|])')
    tag = re.compile(
        r'^<!--[\s\S]*?-->|'
        r'^<\/?\w+(?:"[^"]*"|'
        r'''[^']*'|[^'">])*?>'''
    )
    autolink = re.compile(r'^<([^ >]+(@|:\/)[^ >]+)>')
    link = re.compile(
        r'^!?\[('
        r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
        r')\]\('
        r'''\s*<?([\s\S]*?)>?(?:\s+['"]([\s\S]*?)['"])?\s*'''
        r'\)'
    )
    reflink = re.compile(
        r'^!?\[('
        r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
        r')\]\s*\[([^^\]]*)\]'
    )
    nolink = re.compile(r'^!?\[((?:\[[^\]]*\]|[^\[\]])*)\]')
    url = re.compile(r'''^(https?:\/\/[^\s<]+[^<.,:;"')\]\s])''')
    strong = re.compile(
        r'^__([\s\S]+?)__(?!_)'  # __word__
        r'|'
        r'^\*\*([\s\S]+?)\*\*(?!\*)/'  # **word**
    )
    em = re.compile(
        r'^\b_((?:__|[\s\S])+?)_\b'  # _word_
        r'|'
        r'^\*((?:\*\*|[\s\S])+?)\*(?!\*)'  # *word*
    )
    code = re.compile(r'^(`+)\s*([\s\S]*?[^`])\s*\1(?!`)')
    br = re.compile(r'^ {2,}\n(?!\s*$)')
    strike = re.compile(r'/^~~(?=\S)([\s\S]*?\S)~~/')
    footnote = re.compile(r'^\[\^([^\]]+)\]')
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~]|https?://| {2,}\n|$)')


class InlineLexer(object):
    def __init__(self, renderer, rules=None, **kwargs):
        self.options = kwargs

        self.renderer = renderer
        self.links = []
        self.footnotes = []
        self.footnote_index = 0

        if not rules:
            rules = InlineGrammar()

        self.rules = rules

    def __call__(self, src):
        return self.output(src)

    def setup(self, links, footnotes):
        self.footnote_index = 0
        self.links = links or []
        self.footnotes = footnotes or []

    def output(self, src):
        src = src.rstrip('\n')

        methods = [
            'escape', 'autolink', 'url', 'tag',
            'footnote', 'link', 'strong', 'em',
            'code', 'br', 'strike', 'text',
        ]

        output = ''

        def manipulate(src):
            for key in methods:
                pattern = getattr(self.rules, key)
                m = pattern.match(src)
                if not m:
                    continue
                out = getattr(self, 'output_%s' % key)(m)
                if out is not None:
                    return m, out
            return False

        while src:
            ret = manipulate(src)
            if ret is not False:
                m, out = ret
                output += out
                src = src[len(m.group(0)):]
                continue
            if src:
                raise RuntimeError('Infinite loop at: %s' % src)

        return output

    def output_escape(self, m):
        return m.group(1)

    def output_autolink(self, m):
        data = m.group(1)
        if m.group(2) == '@':
            is_email = True
            link = escape(data)
        else:
            is_email = False
            link = escape(data)
        return self.renderer.autolink(link, is_email)

    def output_url(self, m):
        link = escape(m.group(1))
        return self.renderer.autolink(link, False)

    def output_tag(self, m):
        return m.group(0)

    def output_footnote(self, m):
        key = m.group(1).lower()
        if key not in self.footnotes:
            return None
        index = self.footnotes[key]['index']
        if index:
            return None
        self.footnote_index += 1
        self.footnotes[key]['index'] = self.footnote_index
        return self.renderer.footnote_ref(key, self.footnote_index)

    def output_link(self, m):
        return self._process_link(m, m.group(2), m.group(3))

    def output_reflink(self, m):
        key = m.group(2).lower()
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def output_nolink(self, m):
        key = m.group(1).lower()
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def _process_link(self, m, link, title=None):
        line = m.group(0)

        if title:
            title = escape(title)

        text = m.group(1)

        if line[0] == '!':
            return self.renderer.image(link, title, escape(text))
        return self.renderer.link(link, title, self.output(text))

    def output_strong(self, m):
        text = m.group(2) or m.group(1)
        return self.renderer.strong(text)

    def output_em(self, m):
        text = m.group(2) or m.group(1)
        return self.renderer.em(text)

    def output_code(self, m):
        return self.renderer.codespan(m.group(2))

    def output_br(self):
        return self.renderer.br()

    def output_strike(self, m):
        return self.renderer.strike(self.output(m.group(1)))

    def output_text(self, m):
        return escape(m.group(0))


class Renderer(object):
    def __init__(self, **kwargs):
        self.options = kwargs

    def block_code(self, code, lang=None):
        if not lang:
            return '<pre><code>%s\n</code></pre>\n' % escape(code)
        return '<pre class="lang-%s"><code>%s\n</code>\n</pre>' % (
            lang, escape(code)
        )

    def blockquote(self, text):
        return '<blockquote>%s\n</blockquote>' % text

    def html(self, html):
        return html

    def heading(self, text, level, raw=None):
        return '<h%d>%s</h%d>\n' % (level, text, level)

    def hr(self):
        return '<hr>\n'

    def list(self, body, ordered=True):
        tag = 'ol'
        if ordered:
            tag = 'ul'
        return '<%s>\n%s</%s>\n' % (tag, body, tag)

    def list_item(self, text):
        return '<li>%s</li>\n' % text

    def paragraph(self, text):
        return '<p>%s</p>\n' % text

    def table(self, header, body):
        return (
            '<table>\n<thead>%s</thead>\n'
            '<tbody>\n%s</tbody>\n</table>\n'
        ) % (header, body)

    def table_row(self, text):
        return '<tr>\n%s</tr>\n' % text

    def table_cell(self, text, **flags):
        if flags['header']:
            tag = 'th'
        else:
            tag = 'td'
        align = flags['align']
        if not align:
            return '<%s>%s</%s>\n' % (tag, text, tag)
        return '<%s style="text-align:%s">%s</%s>\n' % (tag, align, text, tag)

    def strong(self, text):
        return '<strong>%s</strong>' % text

    def em(self, text):
        return '<em>%s</em>' % text

    def codespan(self, text):
        return '<code>%s</code>' % escape(text)

    def br(self):
        return '<br>'

    def strike(self, text):
        return '<del>%s</del>' % text

    def autolink(self, link, is_email=False):
        if is_email:
            href = 'mailto:%s' % link
            text = link
        else:
            href = link
            text = re.sub('^https?:\/\/', '', href)
        return '<a href="%s">%s</a>' % (link, text)

    def link(self, link, title, text):
        if 'javascript:' in link:
            # for safety
            return ''
        if not title:
            return '<a href="%s">%s</a>' % (link, text)
        return '<a href="%s" title="%s">%s</a>' % (link, title, text)

    def image(self, link, title, text):
        if not title:
            return '<img src="%s" alt="%s">' % (link, text)
        return '<img src="%s" alt="%s" title="%s">' % (link, text, title)

    def footnote_ref(self, key, index):
        html = (
            '<sup class="footnote-ref" id="fnref-%s">'
            '<a href="#fn-%s">%d</a></sup>'
        ) % (escape(key), escape(key), index)
        return html

    def footnote_item(self, key, text):
        back = (
            '<a href="#fnref-%s" class="footnote-back">&#8617;</a>'
        ) % escape(key)
        text = re.sub(r'<\/(\w+)>$', r'%s</\1>' % back, text)
        html = '<li id="fn-%s">%s''</li>\n' % (escape(key), text)
        return html

    def footnotes(self, text):
        return '<div class="footnotes">\n<ol>%s</ol>\n</div>\n' % text


class Parser(object):
    def __init__(self, inline=None, block=None, renderer=None, **kwargs):
        self.options = kwargs
        if not renderer:
            renderer = Renderer()

        self.renderer = renderer

        self.inline = inline or InlineLexer(renderer, **kwargs)
        self.block = block = BlockLexer(**kwargs)

        self.tokens = []

    def __call__(self, src):
        return self.parse(src)

    def parse(self, src):
        out = self.output(src)

        body = ''
        footnotes = self.block.def_footnotes.copy().items()
        footnotes = filter(lambda o: o[1]['index'], footnotes)
        footnotes = sorted(footnotes, key=lambda o: o[1]['index'])

        links = self.block.def_links.copy()

        methods = [
            'newline',  'hr', 'blockquote', 'list_block',
            'html', 'paragraph', 'text'
        ]

        def clean(text):
            lines = text.split('\n')
            whitespace = None
            for line in lines[1:]:
                space = len(line) - len(line.lstrip())
                if space and (space < whitespace or not whitespace):
                    whitespace = space

            newlines = [lines[0]]
            for line in lines[1:]:
                newlines.append(line[whitespace:])
            return '\n'.join(newlines)

        for key, value in footnotes:
            text = value['text']
            if '\n' in text:
                item = self.output(clean(text), links, methods=methods)
            else:
                item = '<p>%s</p>' % self.inline(text)
            body += self.renderer.footnote_item(key, item)

        out += self.renderer.footnotes(body)
        return out

    def output(self, src, links=None, footnotes=None, methods=None):
        src = preprocessing(src)

        self.tokens = self.block(src, methods)
        self.tokens.reverse()

        if not links:
            links = self.block.def_links
            footnotes = self.block.def_footnotes

        self.inline.setup(links, footnotes)

        out = ''
        while self.next():
            out += self.tok()

        return out

    def next(self):
        if not self.tokens:
            return None
        self.token = self.tokens.pop()
        return self.token

    def peek(self):
        if self.tokens:
            return self.tokens[-1]
        return None

    def tok(self):
        t = self.token['type']

        # sepcial cases
        if t.endswith('_start'):
            t = t[:-6]

        return getattr(self, 'parse_%s' % t)()

    def tok_text(self):
        text = self.token['text']
        while self.peek()['type'] == 'text':
            text += '\n' + self.next()['text']
        return self.inline(text)

    def parse_space(self):
        return ''

    def parse_hr(self):
        return self.renderer.hr()

    def parse_heading(self):
        return self.renderer.heading(
            self.inline(self.token['text']),
            self.token['level'],
            self.token['text'],
        )

    def parse_code(self):
        return self.renderer.block_code(
            self.token['text'], self.token['lang']
        )

    def parse_table(self):
        aligns = self.token['align']
        cell = ''

        # header part
        header = ''
        for i, value in enumerate(self.token['header']):
            flags = {'header': True, 'align': aligns[i]}
            cell += self.renderer.table_cell(self.inline(value), **flags)

        header += self.renderer.table_row(cell)

        # body part
        body = ''
        for i, row in enumerate(self.token['cells']):
            cell = ''
            for j, value in enumerate(row):
                flags = {'header': False, 'align': aligns[j]}
                cell += self.renderer.table_cell(self.inline(value), **flags)
            body += self.renderer.table_row(cell)

        return self.renderer.table(header, body)

    def parse_blockquote(self):
        body = ''
        while self.next()['type'] != 'blockquote_end':
            body += self.tok()
        return self.renderer.blockquote(body)

    def parse_list(self):
        ordered = self.token['ordered']
        body = ''
        while self.next()['type'] != 'list_end':
            body += self.tok()
        return self.renderer.list(body, ordered)

    def parse_list_item(self):
        body = ''
        while self.next()['type'] != 'list_item_end':
            if self.token['type'] == 'text':
                body += self.tok_text()
            else:
                body += self.tok()

        return self.renderer.list_item(body)

    def parse_loose_item(self):
        body = ''
        while self.next()['type'] != 'list_item_end':
            body += self.tok()
        return self.renderer.list_item(body)

    def parse_html(self):
        text = self.token['text']
        if 'pre' not in self.token or not self.token['pre']:
            text = self.inline(text)
        return self.renderer.html(text)

    def parse_paragraph(self):
        return self.renderer.paragraph(self.inline(self.token['text']))

    def parse_text(self):
        return self.renderer.paragraph(self.tok_text())


def markdown(text):
    parse = Parser()
    return parse(text)
