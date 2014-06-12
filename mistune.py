# coding: utf-8
"""
    mistune
    ~~~~~~~

    The fastest markdown parser in pure Python, inspired by marked.

    :copyright: (c) 2014 by Hsiaoming Yang.
"""

import re

__version__ = '0.2.0'
__author__ = 'Hsiaoming Yang <me@lepture.com>'
__all__ = [
    'BlockGrammar', 'BlockLexer',
    'InlineGrammar', 'InlineLexer',
    'Renderer', 'Markdown',
    'markdown', 'escape',
]


def _pure_pattern(regex):
    pattern = regex.pattern
    if pattern.startswith('^'):
        pattern = pattern[1:]
    return pattern


_key_pattern = re.compile(r'\s+')


def _keyify(key):
    return _key_pattern.sub(' ', key.lower())


_escape_pattern = re.compile(r'&(?!#?\w+;)')


def escape(text, quote=False, smart_amp=True):
    """Replace special characters "&", "<" and ">" to HTML-safe sequences.

    The original cgi.escape will always escape "&", but you can control
    this one for a smart escape amp.

    :param quote: if set to True, " and ' will be escaped.
    :param smart_amp: if set to False, & will always be escaped.
    """
    if smart_amp:
        text = _escape_pattern.sub('&amp;', text)
    else:
        text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    if quote:
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
    return text


def preprocessing(text, tab=4):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = text.replace('\t', ' ' * tab)
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2424', '\n')
    pattern = re.compile(r'^ +$', re.M)
    return pattern.sub('', text)


class BlockGrammar(object):
    """Grammars for block level tokens."""

    _tag = (
        r'(?!(?:'
        r'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|'
        r'var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|'
        r'span|br|wbr|ins|del|img)\b)\w+(?!:/|[^\w\s@]*@)\b'
    )
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

    newline = re.compile(r'^\n+')
    block_code = re.compile(r'^( {4}[^\n]+\n*)+')
    fences = re.compile(
        r'^ *(`{3,}|~{3,}) *(\S+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )
    hrule = re.compile(r'^(?: *[-*_]){3,} *(?:\n+|$)')
    heading = re.compile(r'^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')
    lheading = re.compile(r'^([^\n]+)\n *(=|-){2,} *(?:\n+|$)')
    block_quote = re.compile(r'^( *>[^\n]+(\n[^\n]+)*\n*)+')
    list_block = re.compile(
        r'^( *)([*+-]|\d+\.) [\s\S]+?'
        r'(?:'
        r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'  # hrule
        r'|\n+(?=%s)'  # def links
        r'|\n+(?=%s)'  # def footnotes
        r'|\n{2,}'
        r'(?! )'
        r'(?!\1(?:[*+-]|\d+\.) )\n*'
        r'|'
        r'\s*$)' % (
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
        )
    )
    list_item = re.compile(
        r'^(( *)(?:[*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[*+-]|\d+\.) )[^\n]*)*)',
        flags=re.M
    )
    list_pure_bullet = re.compile(r'(?:[*+-]|\d\.)')
    list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
    paragraph = re.compile(
        r'^((?:[^\n]+\n?(?!'
        r'%s|%s|%s|%s|%s|%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(fences).replace(r'\1', r'\2'),
            _pure_pattern(list_block).replace(r'\1', r'\3'),
            _pure_pattern(hrule),
            _pure_pattern(heading),
            _pure_pattern(lheading),
            _pure_pattern(block_quote),
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
            '<' + _tag,
        )
    )
    block_html = re.compile(
        r'^ *(?:%s|%s|%s) *(?:\n{2,}|\s*$)' % (
            r'<!--[\s\S]*?-->',
            r'<(%s)[\s\S]+?<\/\1>' % _tag,
            r'''<%s(?:"[^"]*"|'[^']*'|[^'">])*?>''' % _tag,
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
    """Block level lexer for block grammars."""

    def __init__(self, rules=None, **kwargs):
        self.options = kwargs

        self.tokens = []
        self.def_links = {}
        self.def_footnotes = {}

        if not rules:
            rules = BlockGrammar()

        self.rules = rules

    def __call__(self, src, features=None):
        return self.parse(src, features)

    def parse(self, src, features=None):
        src = src.rstrip('\n')

        if not features:
            features = (
                'newline', 'block_code', 'fences', 'heading',
                'nptable', 'lheading', 'hrule', 'block_quote',
                'list_block', 'block_html', 'def_links',
                'def_footnotes', 'table', 'paragraph', 'text'
            )

        def manipulate(src):
            for key in features:
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
        code = pattern.sub('', code)
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
        features = (
            'newline', 'block_code', 'fences', 'lheading', 'hrule',
            'block_quote', 'list_block', 'block_html', 'text',
        )

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

            # determin whether item is loose or not
            loose = _next
            if not loose and re.search(r'\n\n(?!\s*$)', item):
                loose = True
            if i != length - 1:
                _next = item[len(item)-1] == '\n'
                if not loose:
                    loose = _next

            if loose:
                t = 'loose_item_start'
            else:
                t = 'list_item_start'

            self.tokens.append({'type': t})
            # recurse
            self.parse(item, features)
            self.tokens.append({'type': 'list_item_end'})

    def parse_block_quote(self, m):
        self.tokens.append({'type': 'block_quote_start'})
        cap = m.group(0)
        pattern = re.compile(r'^ *> ?', flags=re.M)
        cap = pattern.sub('', cap)
        self.parse(cap)
        self.tokens.append({'type': 'block_quote_end'})

    def parse_def_links(self, m):
        key = _keyify(m.group(1))
        self.def_links[key] = {
            'link': m.group(2),
            'title': m.group(3),
        }

    def parse_def_footnotes(self, m):
        key = _keyify(m.group(1))
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

        features = (
            'newline', 'block_code', 'fences', 'heading',
            'nptable', 'lheading', 'hrule', 'block_quote',
            'list_block', 'block_html', 'table', 'paragraph', 'text'
        )

        self.parse(text, features)

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
        pre = m.group(1) in ['pre', 'script', 'style']
        text = m.group(0)
        if self.options.get('escape'):
            text = escape(text)
            t = 'paragraph'
        else:
            t = 'block_html'
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
    """Grammars for inline level tokens."""

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
    double_emphasis = re.compile(
        r'^_{2}([\s\S]+?)_{2}(?!_)'  # __word__
        r'|'
        r'^\*{2}([\s\S]+?)\*{2}(?!\*)'  # **word**
    )
    emphasis = re.compile(
        r'^\b_((?:__|[\s\S])+?)_\b'  # _word_
        r'|'
        r'^\*((?:\*\*|[\s\S])+?)\*(?!\*)'  # *word*
    )
    code = re.compile(r'^(`+)\s*([\s\S]*?[^`])\s*\1(?!`)')
    linebreak = re.compile(r'^ {2,}\n(?!\s*$)')
    strikethrough = re.compile(r'^~~(?=\S)([\s\S]*?\S)~~')
    footnote = re.compile(r'^\[\^([^\]]+)\]')
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~]|https?://| {2,}\n|$)')


class InlineLexer(object):
    """Inline level lexer for inline grammars."""

    def __init__(self, renderer, rules=None, **kwargs):
        self.options = kwargs

        self.renderer = renderer
        self.links = {}
        self.footnotes = {}
        self.footnote_index = 0

        if not rules:
            rules = InlineGrammar()
            if self.options.get('hard_wrap'):
                # {2,} -> *
                rules.linebreak = re.compile(r'^ *\n(?!\s*$)')
                rules.text = re.compile(
                    r'^[\s\S]+?(?=[\\<!\[_*`~]|https?://| *\n|$)'
                )

        self.rules = rules

        self._in_link = False
        self._in_footnote = False

    def __call__(self, src):
        return self.output(src)

    def setup(self, links, footnotes):
        self.footnote_index = 0
        self.links = links or {}
        self.footnotes = footnotes or {}

    def output(self, src, features=None):
        src = src.rstrip('\n')
        if self.options.get('escape'):
            src = escape(src)

        if not features:
            features = [
                'escape', 'autolink', 'url', 'tag',
                'footnote', 'link', 'reflink', 'nolink',
                'double_emphasis', 'emphasis', 'code',
                'linebreak', 'strikethrough', 'text',
            ]

        if self._in_footnote and 'footnote' in features:
            features.remove('footnote')

        output = ''

        def manipulate(src):
            for key in features:
                pattern = getattr(self.rules, key)
                m = pattern.match(src)
                if not m:
                    continue
                self.line_match = m
                out = getattr(self, 'output_%s' % key)(m)
                if out is not None:
                    return m, out
            return False

        self.line_started = False
        while src:
            ret = manipulate(src)
            self.line_started = True
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
        if self._in_link:
            return link
        return self.renderer.autolink(link, False)

    def output_tag(self, m):
        text = m.group(0)
        lower_text = text.lower()
        if lower_text.startswith('<a '):
            self._in_link = True
        if lower_text.startswith('</a>'):
            self._in_link = False
        return text

    def output_footnote(self, m):
        key = _keyify(m.group(1))
        if key not in self.footnotes:
            return None
        if self.footnotes[key]:
            return None
        self.footnote_index += 1
        self.footnotes[key] = self.footnote_index
        return self.renderer.footnote_ref(key, self.footnote_index)

    def output_link(self, m):
        return self._process_link(m, m.group(2), m.group(3))

    def output_reflink(self, m):
        key = _keyify(m.group(2) or m.group(1))
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def output_nolink(self, m):
        key = _keyify(m.group(1))
        if key not in self.links:
            return None
        ret = self.links[key]
        return self._process_link(m, ret['link'], ret['title'])

    def _process_link(self, m, link, title=None):
        line = m.group(0)

        if title:
            title = escape(title, quote=True)

        text = m.group(1)

        if line[0] == '!':
            text = escape(text, quote=True)
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
        text = escape(m.group(2), smart_amp=False)
        return self.renderer.codespan(text)

    def output_linebreak(self, m):
        return self.renderer.linebreak()

    def output_strikethrough(self, m):
        text = self.output(m.group(1))
        return self.renderer.strikethrough(text)

    def output_text(self, m):
        text = m.group(0)
        return self.renderer.text(text)


class Renderer(object):
    """The default HTML renderer for rendering Markdown.
    """

    def __init__(self, **kwargs):
        self.options = kwargs

    def block_code(self, code, lang=None):
        """Rendering block level code. ``pre > code``.

        :param code: text content of the code block.
        :param lang: language of the given code.
        """
        code = code.rstrip()
        if not lang:
            code = escape(code, smart_amp=False)
            return '<pre><code>%s\n</code></pre>\n' % code
        code = escape(code, quote=True, smart_amp=False)
        return '<pre><code class="lang-%s">%s\n</code>\n</pre>' % (lang, code)

    def block_quote(self, text):
        """Rendering <blockquote> with the given text.

        :param text: text content of the blockquote.
        """
        return '<blockquote>%s\n</blockquote>' % text

    def block_html(self, html):
        """Rendering block level pure html content.

        :param html: text content of the html snippet.
        """
        if self.options.get('skip_style'):
            if html.lower().startswith('<style'):
                return ''
        return html

    def header(self, text, level, raw=None):
        """Rendering header/heading tags like ``<h1>`` ``<h2>``.

        :param text: rendered text content for the header.
        :param level: a number for the header level, for example: 1.
        :param raw: raw text content of the header.
        """
        return '<h%d>%s</h%d>\n' % (level, text, level)

    def hrule(self):
        """Rendering method for ``<hr>`` tag."""
        if self.options.get('use_xhtml'):
            return '<hr />\n'
        return '<hr>\n'

    def list(self, body, ordered=True):
        """Rendering list tags like ``<ul>`` and ``<ol>``.

        :param body: body contents of the list.
        :param ordered: whether this list is ordered or not.
        """
        tag = 'ul'
        if ordered:
            tag = 'ol'
        return '<%s>\n%s</%s>\n' % (tag, body, tag)

    def list_item(self, text):
        """Rendering list item snippet. Like ``<li>``."""
        return '<li>%s</li>\n' % text

    def paragraph(self, text):
        """Rendering paragraph tags. Like ``<p>``."""
        return '<p>%s</p>\n' % text

    def table(self, header, body):
        """Rendering table element. Wrap header and body in it.

        :param header: header part of the table.
        :param body: body part of the table.
        """
        return (
            '<table>\n<thead>%s</thead>\n'
            '<tbody>\n%s</tbody>\n</table>\n'
        ) % (header, body)

    def table_row(self, content):
        """Rendering a table row. Like ``<tr>``.

        :param content: content of current table row.
        """
        return '<tr>\n%s</tr>\n' % content

    def table_cell(self, content, **flags):
        """Rendering a table cell. Like ``<th>`` ``<td>``.

        :param content: content of current table cell.
        :param header: whether this is header or not.
        :param align: align of current table cell.
        """
        if flags['header']:
            tag = 'th'
        else:
            tag = 'td'
        align = flags['align']
        if not align:
            return '<%s>%s</%s>\n' % (tag, content, tag)
        return '<%s style="text-align:%s">%s</%s>\n' % (
            tag, align, content, tag
        )

    def double_emphasis(self, text):
        """Rendering **strong** text.

        :param text: text content for emphasis.
        """
        return '<strong>%s</strong>' % text

    def emphasis(self, text):
        """Rendering *emphasis* text.

        :param text: text content for emphasis.
        """
        return '<em>%s</em>' % text

    def codespan(self, text):
        """Rendering inline `code` text.

        :param text: text content for inline code.
        """
        return '<code>%s</code>' % text

    def linebreak(self):
        """Rendering line break like ``<br>``."""
        if self.options.get('use_xhtml'):
            return '<br />'
        return '<br>'

    def strikethrough(self, text):
        """Rendering ~~strikethrough~~ text.

        :param text: text content for strikethrough.
        """
        return '<del>%s</del>' % text

    def text(self, text):
        """Rendering unformatted text.

        :param text: text content.
        """
        return escape(text)

    def autolink(self, link, is_email=False):
        """Rendering a given link or email address.

        :param link: link content or email address.
        :param is_email: whether this is an email or not.
        """
        text = link
        if is_email:
            link = 'mailto:%s' % link
        return '<a href="%s">%s</a>' % (link, text)

    def link(self, link, title, text):
        """Rendering a given link with content and title.

        :param link: href link for ``<a>`` tag.
        :param title: title content for `title` attribute.
        :param text: text content for description.
        """
        if 'javascript:' in link:
            # for safety
            return ''
        if not title:
            return '<a href="%s">%s</a>' % (link, text)
        return '<a href="%s" title="%s">%s</a>' % (link, title, text)

    def image(self, src, title, text):
        """Rendering a image with title and text.

        :param src: source link of the image.
        :param title: title text of the image.
        :param text: alt text of the image.
        """
        if not title:
            html = '<img src="%s" alt="%s"' % (src, text)
        else:
            html = '<img src="%s" alt="%s" title="%s"' % (src, text, title)
        if self.options.get('use_xhtml'):
            return '%s />' % html
        return '%s>' % html

    def raw_html(self, html):
        """Rendering span level html snippet.

        :param html: html snippet.
        """
        if self.options.get('skip_html'):
            return escape(html)
        return html

    def footnote_ref(self, key, index):
        """Rendering the ref anchor of a footnote.

        :param key: identity key for the footnote.
        :param index: the index count of current footnote.
        """
        html = (
            '<sup class="footnote-ref" id="fnref-%s">'
            '<a href="#fn-%s" rel="footnote">%d</a></sup>'
        ) % (escape(key), escape(key), index)
        return html

    def footnote_item(self, key, text):
        """Rendering a footnote item.

        :param key: identity key for the footnote.
        :param text: text content of the footnote.
        """
        back = (
            '<a href="#fnref-%s" rev="footnote">&#8617;</a>'
        ) % escape(key)
        text = text.rstrip()
        if text.endswith('</p>'):
            text = re.sub(r'<\/p>$', r'%s</p>' % back, text)
        else:
            text = '%s<p>%s</p>' % (text, back)
        html = '<li id="fn-%s">%s</li>\n' % (escape(key), text)
        return html

    def footnotes(self, text):
        """Wrapper for all footnotes.

        :param text: contents of all footnotes.
        """
        html = '<div class="footnotes">\n%s<ol>%s</ol>\n</div>\n'
        return html % (self.hrule(), text)


class Markdown(object):
    """The Markdown parser.

    :param renderer: An instance of ``Renderer``.
    """

    def __init__(self, renderer=None, **kwargs):
        inline = kwargs.pop('inline', None)
        block = kwargs.pop('block', None)

        if not renderer:
            renderer = Renderer()

        self.renderer = renderer
        self.options = kwargs

        self.inline = inline or InlineLexer(renderer, **kwargs)
        self.block = block or BlockLexer(**kwargs)

        self.footnotes = []
        self.tokens = []

    def __call__(self, text):
        return self.parse(text)

    def render(self, text):
        """Render the Markdown text.

        :param text: markdown formatted text content.
        """
        return self.parse(text)

    def parse(self, src):
        out = self.output(src)
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

        body = ''
        while self.footnotes:
            note = self.footnotes.pop()
            body += self.renderer.footnote_item(
                note['key'], note['text']
            )

        out += self.renderer.footnotes(body)
        return out

    def output(self, src, features=None):
        src = preprocessing(src)

        self.tokens = self.block(src, features)
        self.tokens.reverse()

        self.inline.setup(self.block.def_links, self.block.def_footnotes)

        out = ''
        while self.pop():
            out += self.tok()

        return out

    def pop(self):
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
            text += '\n' + self.pop()['text']
        return self.inline(text)

    def parse_space(self):
        return ''

    def parse_hrule(self):
        return self.renderer.hrule()

    def parse_heading(self):
        return self.renderer.header(
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

    def parse_block_quote(self):
        body = ''
        while self.pop()['type'] != 'block_quote_end':
            body += self.tok()
        return self.renderer.block_quote(body)

    def parse_list(self):
        ordered = self.token['ordered']
        body = ''
        while self.pop()['type'] != 'list_end':
            body += self.tok()
        return self.renderer.list(body, ordered)

    def parse_list_item(self):
        body = ''
        while self.pop()['type'] != 'list_item_end':
            if self.token['type'] == 'text':
                body += self.tok_text()
            else:
                body += self.tok()

        return self.renderer.list_item(body)

    def parse_loose_item(self):
        body = ''
        while self.pop()['type'] != 'list_item_end':
            body += self.tok()
        return self.renderer.list_item(body)

    def parse_footnote(self):
        self.inline._in_footnote = True
        body = ''
        key = self.token['key']
        while self.pop()['type'] != 'footnote_end':
            body += self.tok()
        self.footnotes.append({'key': key, 'text': body})
        self.inline._in_footnote = False
        return ''

    def parse_block_html(self):
        text = self.token['text']
        if 'pre' not in self.token or not self.token['pre']:
            text = self.inline(text)
        return self.renderer.block_html(text)

    def parse_paragraph(self):
        return self.renderer.paragraph(self.inline(self.token['text']))

    def parse_text(self):
        return self.renderer.paragraph(self.tok_text())


def markdown(text, **kwargs):
    """Render markdown formatted text to html.

    :param text: markdown formatted text content.
    :param escape: if set to True, all html tags will be escaped.
    :param use_xhtml: output with xhtml tags.
    """
    m = Markdown(**kwargs)
    return m.parse(text)
