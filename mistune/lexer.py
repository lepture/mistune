import re
from .grammar import BlockGrammar, InlineGrammar, inline_tags
from .util import keyify

_block_quote_leading_pattern = re.compile(r'^ *> ?', flags=re.M)
_block_code_leading_pattern = re.compile(r'^ {4}', re.M)


class BlockLexer(object):
    """Block level lexer for block grammars."""
    grammar_class = BlockGrammar

    default_rules = [
        'newline', 'hrule', 'block_code', 'fences', 'heading',
        'nptable', 'lheading', 'block_quote',
        'list_block', 'block_html', 'def_links',
        'def_footnotes', 'table', 'paragraph', 'text'
    ]

    list_rules = (
        'newline', 'block_code', 'fences', 'lheading', 'hrule',
        'block_quote', 'list_block', 'block_html', 'text',
    )

    footnote_rules = (
        'newline', 'block_code', 'fences', 'heading',
        'nptable', 'lheading', 'hrule', 'block_quote',
        'list_block', 'block_html', 'table', 'paragraph', 'text'
    )

    def __init__(self, rules=None, **kwargs):
        self.tokens = []
        self.def_links = {}
        self.def_footnotes = {}

        if not rules:
            rules = self.grammar_class()

        self.rules = rules

    def __call__(self, text, rules=None):
        return self.parse(text, rules)

    def parse(self, text, rules=None):
        text = text.rstrip('\n')

        if not rules:
            rules = self.default_rules

        def manipulate(text):
            for key in rules:
                rule = getattr(self.rules, key)
                m = rule.match(text)
                if not m:
                    continue
                getattr(self, 'parse_%s' % key)(m)
                return m
            return False  # pragma: no cover

        while text:
            m = manipulate(text)
            if m is not False:
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)
        return self.tokens

    def parse_newline(self, m):
        length = len(m.group(0))
        if length > 1:
            self.tokens.append({'type': 'newline'})

    def parse_block_code(self, m):
        # clean leading whitespace
        code = _block_code_leading_pattern.sub('', m.group(0))
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

    def parse_hrule(self, m):
        self.tokens.append({'type': 'hrule'})

    def parse_list_block(self, m):
        bull = m.group(2)
        self.tokens.append({
            'type': 'list_start',
            'ordered': '.' in bull,
        })
        cap = m.group(0)
        self._process_list_item(cap, bull)
        self.tokens.append({'type': 'list_end'})

    def _process_list_item(self, cap, bull):
        cap = self.rules.list_item.findall(cap)

        _next = False
        length = len(cap)

        for i in range(length):
            item = cap[i][0]

            # remove the bullet
            space = len(item)
            item = self.rules.list_bullet.sub('', item)

            # outdent
            if '\n ' in item:
                space = space - len(item)
                pattern = re.compile(r'^ {1,%d}' % space, flags=re.M)
                item = pattern.sub('', item)

            # determine whether item is loose or not
            loose = _next
            if not loose and re.search(r'\n\n(?!\s*$)', item):
                loose = True

            rest = len(item)
            if i != length - 1 and rest:
                _next = item[rest-1] == '\n'
                if not loose:
                    loose = _next

            if loose:
                t = 'loose_item_start'
            else:
                t = 'list_item_start'

            self.tokens.append({'type': t})
            # recurse
            self.parse(item, self.list_rules)
            self.tokens.append({'type': 'list_item_end'})

    def parse_block_quote(self, m):
        self.tokens.append({'type': 'block_quote_start'})
        # clean leading >
        cap = _block_quote_leading_pattern.sub('', m.group(0))
        self.parse(cap)
        self.tokens.append({'type': 'block_quote_end'})

    def parse_def_links(self, m):
        key = keyify(m.group(1))
        self.def_links[key] = {
            'link': m.group(2),
            'title': m.group(3),
        }

    def parse_def_footnotes(self, m):
        key = keyify(m.group(1))
        if key in self.def_footnotes:
            # footnote is already defined
            return

        self.def_footnotes[key] = 0

        self.tokens.append({
            'type': 'footnote_start',
            'key': key,
        })

        text = m.group(2)

        if '\n' in text:
            lines = text.split('\n')
            whitespace = None
            for line in lines[1:]:
                space = len(line) - len(line.lstrip())
                if space and (not whitespace or space < whitespace):
                    whitespace = space
            newlines = [lines[0]]
            for line in lines[1:]:
                newlines.append(line[whitespace:])
            text = '\n'.join(newlines)

        self.parse(text, self.footnote_rules)

        self.tokens.append({
            'type': 'footnote_end',
            'key': key,
        })

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

    def parse_block_html(self, m):
        tag = m.group(1)
        if not tag:
            text = m.group(0)
            self.tokens.append({
                'type': 'close_html',
                'text': text
            })
        else:
            attr = m.group(2)
            text = m.group(3)
            self.tokens.append({
                'type': 'open_html',
                'tag': tag,
                'extra': attr,
                'text': text
            })

    def parse_paragraph(self, m):
        text = m.group(1).rstrip('\n')
        self.tokens.append({'type': 'paragraph', 'text': text})

    def parse_text(self, m):
        text = m.group(0)
        self.tokens.append({'type': 'text', 'text': text})


class InlineLexer(object):
    """Inline level lexer for inline grammars."""
    grammar_class = InlineGrammar

    default_rules = [
        'escape', 'inline_html', 'autolink', 'url',
        'footnote', 'link', 'reflink', 'nolink',
        'double_emphasis', 'emphasis', 'code',
        'linebreak', 'strikethrough', 'text',
    ]
    inline_html_rules = [
        'escape', 'autolink', 'url', 'link', 'reflink',
        'nolink', 'double_emphasis', 'emphasis', 'code',
        'linebreak', 'strikethrough', 'text',
    ]

    def __init__(self, renderer, rules=None, **kwargs):
        self.renderer = renderer
        self.links = {}
        self.footnotes = {}
        self.footnote_index = 0

        if not rules:
            rules = self.grammar_class()

        kwargs.update(self.renderer.options)
        if kwargs.get('hard_wrap'):
            rules.hard_wrap()

        self.rules = rules

        self._in_link = False
        self._in_footnote = False
        self._parse_inline_html = kwargs.get('parse_inline_html')

    def __call__(self, text, rules=None):
        return self.output(text, rules)

    def setup(self, links, footnotes):
        self.footnote_index = 0
        self.links = links or {}
        self.footnotes = footnotes or {}

    def output(self, text, rules=None):
        text = text.rstrip('\n')
        if not rules:
            rules = list(self.default_rules)

        if self._in_footnote and 'footnote' in rules:
            rules.remove('footnote')

        output = self.renderer.placeholder()

        def manipulate(text):
            for key in rules:
                pattern = getattr(self.rules, key)
                m = pattern.match(text)
                if not m:
                    continue
                self.line_match = m
                out = getattr(self, 'output_%s' % key)(m)
                if out is not None:
                    return m, out
            return False  # pragma: no cover

        while text:
            ret = manipulate(text)
            if ret is not False:
                m, out = ret
                output += out
                text = text[len(m.group(0)):]
                continue
            if text:  # pragma: no cover
                raise RuntimeError('Infinite loop at: %s' % text)

        return output

    def output_escape(self, m):
        text = m.group(1)
        return self.renderer.escape(text)

    def output_autolink(self, m):
        link = m.group(1)
        if m.group(2) == '@':
            is_email = True
        else:
            is_email = False
        return self.renderer.autolink(link, is_email)

    def output_url(self, m):
        link = m.group(1)
        if self._in_link:
            return self.renderer.text(link)
        return self.renderer.autolink(link, False)

    def output_inline_html(self, m):
        tag = m.group(1)
        if self._parse_inline_html and tag in inline_tags:
            text = m.group(3)
            if tag == 'a':
                self._in_link = True
                text = self.output(text, rules=self.inline_html_rules)
                self._in_link = False
            else:
                text = self.output(text, rules=self.inline_html_rules)
            extra = m.group(2) or ''
            html = '<%s%s>%s</%s>' % (tag, extra, text, tag)
        else:
            html = m.group(0)
        return self.renderer.inline_html(html)

    def output_footnote(self, m):
        key = keyify(m.group(1))
        if key not in self.footnotes:
            return None
        if self.footnotes[key]:
            return None
        self.footnote_index += 1
        self.footnotes[key] = self.footnote_index
        return self.renderer.footnote_ref(key, self.footnote_index)

    def output_link(self, m):
        return self._process_link(m, m.group(3), m.group(4))

    def output_reflink(self, m):
        key = keyify(m.group(2) or m.group(1))
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def output_nolink(self, m):
        key = keyify(m.group(1))
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def _process_link(self, m, link, title=None):
        line = m.group(0)
        text = m.group(1)
        if line[0] == '!':
            return self.renderer.image(link, title, text)

        self._in_link = True
        text = self.output(text)
        self._in_link = False
        return self.renderer.link(link, title, text)

    def output_double_emphasis(self, m):
        text = m.group(2) or m.group(1)
        text = self.output(text)
        return self.renderer.double_emphasis(text)

    def output_emphasis(self, m):
        text = m.group(2) or m.group(1)
        text = self.output(text)
        return self.renderer.emphasis(text)

    def output_code(self, m):
        text = m.group(2)
        return self.renderer.codespan(text)

    def output_linebreak(self, m):
        return self.renderer.linebreak()

    def output_strikethrough(self, m):
        text = self.output(m.group(1))
        return self.renderer.strikethrough(text)

    def output_text(self, m):
        text = m.group(0)
        return self.renderer.text(text)
