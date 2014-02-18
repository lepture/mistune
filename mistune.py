# coding: utf-8
"""
    mistune
    ~~~~~~~

    Yet another markdown parser, inspired by marked in JavaScript.
"""

import re
from collections import OrderedDict

__version__ = '0.1.0'
__author__ = 'Hsiaoming Yang <me@lepture.com>'


def _pure_pattern(regex):
    return re.sub('(^|[^\[])\^', '\1', regex.pattern)


class BlockGrammar(object):
    _tag = (
        '(?!(?:'
        'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|'
        'var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|'
        'span|br|wbr|ins|del|img)\\b)\\w+(?!:/|[^\\w\\s@]*@)\\b'
    )

    newline = re.compile(r'^\n+')
    code = re.compile(r'^( {4}[^\n]+\n*)+')
    fences = re.compile(
        r'^ *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        '([\s\S]+?)\s*'
        '\1*(?:\n+|$)'  # ```
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
        r'^( *)([*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\1(?:[*+-]|\d+\.) )[^\n]*)*'
    )
    list_pure_bullet = re.compile(r'(?:[*+-]|\d\.)')
    list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
    def_links = re.compile(
        r'^ *\[([^^\]]+)\]: *'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'
    )
    def_footnotes = re.compile(
        r'^\[\^([^\]]+)\]: *'  # [^key]:
        r'([^\n]*(?:\n [^\n]*)*)'
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
            '<!--[\s\S]*?-->',
            '<(' + _tag + ')[\s\S]+?<\/\1>',
            '<' + _tag + '''(?:"[^"]*}|'[^']*'|[^'">])*?>''',
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
    top_methods = [
        'newline',
        'code',
        'fences',
        'heading',
        'nptable',
        'lheading',
        'hr',
        'blockquote',
        'list_block',
        'html',
        'def_links',
        'def_footnotes',
        'table',
        'paragraph',
        'text',
    ]
    low_methods = [
        'newline',
        'code',
        'fences',
        'lheading',
        'hr',
        'blockquote',
        'list_block',
        'html',
        'text',
    ]

    def __init__(self, rules=None, **kwargs):
        self.options = kwargs

        self.tokens = []
        self.def_links = OrderedDict()
        self.def_footnotes = OrderedDict()

        if not rules:
            rules = BlockGrammar()

        self.rules = rules
        self._parse_methods = self.top_methods

    def parse(self, src, methods=None):
        src = src.rstrip('\n')

        if methods:
            self._parse_methods = methods
        while src:
            for key in self._parse_methods:
                alt = getattr(self, 'parse_%s' % key)(src)
                if alt != src:
                    src = alt
                    continue
            if src:
                raise RuntimeError('Infinite loop at: %s' % src)
        return self.tokens

    def parse_newline(self, src):
        m = self.rules.newline.match(src)
        if not m:
            return src
        length = len(m.group(0))
        if length > 1:
            self.tokens.append({'type': 'space'})
        return src[length:]

    def parse_code(self, src):
        m = self.rules.code.match(src)
        if not m:
            return src
        code = m.group(0)
        pattern = re.compile(r'^ {4}', re.M)
        code = pattern.sub(code, '')
        self.tokens.append({
            'type': 'code',
            'lang': None,
            'text': code,
        })
        return src[len(code):]

    def parse_fences(self, src):
        m = self.rules.fences.match(src)
        if not m:
            return src
        self.tokens.append({
            'type': 'code',
            'lang': m.group(2),
            'text': m.group(3),
        })
        return src[len(m.group(0)):]

    def parse_heading(self, src):
        m = self.rules.heading.match(src)
        if not m:
            return src
        self.tokens.append({
            'type': 'heading',
            'level': len(m.group(1)),
            'text': m.group(2),
        })
        return src[len(m.group(0)):]

    def parse_lheading(self, src):
        """Parse setext heading."""
        m = self.rules.lheading.match(src)
        if not m:
            return src
        self.tokens.append({
            'type': 'heading',
            'level': 1 if m.group(2) == '=' else 2,
            'text': m.group(1),
        })
        return src[len(m.group(0)):]

    def parse_hr(self, src):
        m = self.rules.hr.match(src)
        if not m:
            return src
        self.tokens.append({'type': 'hr'})
        return src[len(m.group(0)):]

    def parse_list_block(self, src):
        m = self.rules.list_block.match(src)
        if not m:
            return src
        bull = m.group(2)
        self.tokens.push({
            'type': 'list_start',
            'ordered': len(bull) > 1,
        })
        cap = m.group(0)
        src = self._process_list_item(cap, bull, src[len(cap):])
        self.tokens.append({'type': 'list_end'})
        return src

    def _process_list_item(self, cap, bull, src):
        m = self.rules.list_item.match(cap)
        _next = False
        length = len(m.groups())

        for i in range(length + 1):
            item = m.group(i)

            # remove the bullet
            space = len(item)
            item = self.rules.list_bullet.sub('', item)

            # outdent
            if '\n ' in item:
                space -= len(item)
                item = re.sub(r'^ {1,%d}' % space, '', item, re.M)

            # determine if the next list item belongs here
            if i != length:
                b = self.rules.list_pure_bullet.match(m.group(i + 1))
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
            if i != length:
                _next = item[len(item)-1] == '\n'
                if not loose:
                    loose = _next

            if loose:
                t = 'loose_item_start'
            else:
                t = 'list_item_start'

            self.tokens.append({'type': t})
            # recurse
            self.parse(item, self.low_methods)
            self.tokens.append({'type': 'list_item_end'})
        return src

    def parse_blockquote(self, src):
        m = self.rules.blockquote.match(src)
        if not m:
            return src
        self.token.append({'type': 'blockquote_start'})
        cap = m.group(0)
        src = src[len(cap):]
        cap = re.sub(r'^ *> ?', '', cap, flags=re.M)
        self.parse(cap)
        self.tokens.append({'type': 'blockquote_end'})
        return src

    def parse_def_links(self, src):
        m = self.rules.def_links.match(src)
        if not m:
            return src
        key = m.group(1).lower()
        self.def_links[key] = {
            'href': m.group(2),
            'title': m.group(3),
        }
        return src[len(m.group(0)):]

    def parse_def_footnotes(self, src):
        m = self.rules.def_footnotes.match(src)
        if not m:
            return src
        key = m.group(1).lower()
        self.def_footnotes[key] = m.group(2)
        return src[len(m.group(0)):]

    def parse_table(self, src):
        m = self.rules.table.match(src)
        if not m:
            return src
        item = self._process_table(m)

        cells = re.sub(r'(?: *\| *)?\n$', '', m.group(3))
        cells = cells.split('\n')
        for i, v in enumerate(cells):
            v = re.sub(r'^ *\| *| *\| *$', '', v)
            cells[i] = re.split(r' *\| *', v)

        item['cells'] = cells
        self.tokens.append(item)
        return src[len(m.group(0)):]

    def parse_nptable(self, src):
        m = self.rules.nptable.match(src)
        if not m:
            return src
        item = self._process_table(m)

        cells = re.sub(r'\n$', '', m.group(3))
        cells = cells.split('\n')
        for i, v in enumerate(cells):
            cells[i] = re.split(r' *\| *', v)

        item['cells'] = cells
        self.tokens.append(item)
        return src[len(m.group(0)):]

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

    def parse_html(self, src):
        m = self.rules.html.match(src)
        if not m:
            return src
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
        return src[len(text):]

    def parse_paragraph(self, src):
        m = self.rules.paragraph.match(src)
        if not m:
            return src
        text = m.group(1).rstrip('\n')
        self.tokens.append({'type': 'paragraph', 'text': text})
        return src[len(m.group(0)):]

    def parse_text(self, src):
        m = self.rules.text.match(src)
        if not m:
            return src
        text = m.group(0)
        self.tokens.append({'type': 'text', 'text': text})
        return src[len(text):]


def preprocessing(text, tab=4):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = text.replace('\t', ' ' * tab)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


def parse(text, tab=4):
    text = preprocessing(text, tab)
    lexer = BlockLexer()
    print lexer.parse(text)
