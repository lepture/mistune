import re
try:
    import html
    from urllib.parse import quote
except ImportError:
    from urllib import quote
    html = None
from .scanner import Scanner

PUNCTUATION = r'''\\!"#$%&'()*+,./:;<=>?@\[\]^`{}|_~-'''
ESCAPE = r'\\[' + PUNCTUATION + ']'
HTML_TAGNAME = r'[A-Za-z][A-Za-z0-9-]*'
HTML_ATTRIBUTES = (
    r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*'
    r'(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'
)
ESCAPE_CHAR = re.compile(r'''\\([\\!"#$%&'()*+,.\/:;<=>?@\[\]^`{}|_~-])''')


class InlineParser(object):
    ESCAPE = ESCAPE

    #: link or email syntax::
    #:
    #: <https://example.com>
    AUTO_LINK = r'<([^ >]+(@|:)[^ >]+)>'

    #: link or image syntax::
    #:
    #: [text](/link "title")
    #: ![alt](/src "title")
    STD_LINK = (
        r'!?\[('
        r'(?:\[[^^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*'
        r')\]\(\s*'

        r'(<(?:\\[<>]?|[^\s<>\\])*>|'
        r'(?:\\[()]?|\([^\s\x00-\x1f\\]*\)|[^\s\x00-\x1f()\\])*?)'

        r'(?:\s+('
        r'''"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)'''
        r'))?\s*\)'
    )

    #: Get link from references. References are defined in DEF_LINK in blocks.
    #: The syntax looks like::
    #:
    #:    [an example][id]
    #:
    #:    [id]: https://example.com "optional title"
    REF_LINK = (
        r'!?\[((?:[^\\\[\]]|' + ESCAPE + '){0,1000})\]'
        r'\s*\[((?:[^\\\[\]]|' + ESCAPE + '){0,1000})\]'
    )

    #: Simple form of reference link::
    #:
    #:    [an example]
    #:
    #:    [an example]: https://example.com "optional title"
    REF_LINK2 = r'!?\[((?:[^\\\[\]]|' + ESCAPE + '){0,1000})\]'

    URL_LINK = r'''(https?:\/\/[^\s<]+[^<.,:;"')\]\s])'''

    #: emphasis with * or _::
    #:
    #:    *text*
    #:    _text_
    EMPHASIS = (
        r'\b_[^\s_]_(?!_)\b|'  # _s_
        r'\*[^\s*"<\[]\*(?!\*)|'  # *s*
        r'\b_[^\s][\s\S]*?[^\s_]_(?!_|[^\s' + PUNCTUATION + r'])\b|'
        r'\b_[^\s_][\s\S]*?[^\s]_(?!_|[^\s' + PUNCTUATION + r'])\b|'
        r'\*[^\s"<\[][\s\S]*?[^\s*]\*(?!\*)|'
        r'\*[^\s*"<\[][\s\S]*?[^\s]\*(?!\*)'
    )

    #: strong with ** or __::
    #:
    #:    **text**
    #:    __text__
    STRONG = (
        r'\b__[^\s]__(?!_)\b|'
        r'\*\*[^\s]\*\*(?!\*)|'
        r'\b__[^\s][\s\S]*?[^\s]__(?!_)\b|'
        r'\*\*[^\s][\s\S]*?[^\s]\*\*(?!\*)'
    )

    #: codespan with `::
    #:
    #:    `code`
    CODESPAN = (
        r'(?<!\\|`)(?:\\\\)*(`+)(?!`)([\s\S]+?)(?<!`)\1(?!`)'
    )

    #: linebreak leaves two spaces at the end of line
    LINEBREAK = r'(?:\\| {2,})\n(?!\s*$)'

    #: strike through syntax looks like: ``~~word~~``
    STRIKETHROUGH = r'~~(?=\S)([\s\S]*?\S)~~'

    #: footnote syntax looks like::
    #:
    #:    [^key]
    FOOTNOTE = r'\[\^([^\]]+)\]'

    INLINE_HTML = (
        r'(?<!\\)<' + HTML_TAGNAME + HTML_ATTRIBUTES + r'\s*/?>|'  # open tag
        r'(?<!\\)</' + HTML_TAGNAME + r'\s*>|'  # close tag
        r'(?<!\\)<!--(?!>|->)(?:(?!--)[\s\S])+?(?<!-)-->|'  # comment
        r'(?<!\\)<\?[\s\S]+?\?>|'
        r'(?<!\\)<![A-Z][\s\S]+?>|'  # doctype
        r'(?<!\\)<!\[CDATA[\s\S]+?\]\]>'  # cdata
    )

    def __init__(self, renderer):
        self.renderer = renderer
        self.rules = {
            'escape': (self.ESCAPE, self.parse_escape),
            'auto_link': (self.AUTO_LINK, self.parse_auto_link),
            'url_link': (self.URL_LINK, self.parse_url_link),
            'std_link': (self.STD_LINK, self.parse_std_link),
            'ref_link': (self.REF_LINK, self.parse_ref_link),
            'ref_link2': (self.REF_LINK2, self.parse_ref_link),
            'footnote': (self.FOOTNOTE, self.parse_footnote),
            'strong': (self.STRONG, self.parse_strong),
            'emphasis': (self.EMPHASIS, self.parse_emphasis),
            'codespan': (self.CODESPAN, self.parse_codespan),
            'strikethrough': (self.STRIKETHROUGH, self.parse_strikethrough),
            'linebreak': (self.LINEBREAK, self.parse_linebreak),
            'inline_html': (self.INLINE_HTML, self.parse_inline_html),
        }

        self.default_rules = (
            'escape', 'inline_html', 'auto_link', 'url_link', 'footnote',
            'std_link', 'ref_link', 'ref_link2', 'strong', 'emphasis',
            'codespan', 'strikethrough', 'linebreak',
        )
        self._cached_sc = {}

    def register_rule(self, name, pattern, method):
        self.rules[name] = (pattern, lambda m, state: method(self, m, state))

    def parse_escape(self, m, state):
        text = m.group(0)[1:]
        return self.renderer.text(text)

    def parse_auto_link(self, m, state):
        text = m.group(1)
        if '@' in text:
            link = 'mailto:' + text
        else:
            link = text
        return self.renderer.link(escape_url(link), text)

    def parse_std_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        link = ESCAPE_CHAR.sub(r'\1', m.group(2))
        if link.startswith('<') and link.endswith('>'):
            link = link[1:-1]

        title = m.group(3)
        if title:
            title = ESCAPE_CHAR.sub(r'\1', title[1:-1])

        if line[0] == '!':
            return self.renderer.image(link, text, title)

        text = self._process_link_text(text, state)
        return self.renderer.link(escape_url(link), text, title)

    def parse_ref_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        key = m.group(2)
        if not key:
            key = text

        def_links = state.get('def_links')
        if not def_links or key not in def_links:
            return self.renderer.text(line)

        link, title = def_links.get(key)
        if line[0] == '!':
            return self.renderer.image(link, text, title)

        if m.group(2):
            text = self._process_link_text(text, state)
        return self.renderer.link(escape_url(link), text, title)

    def _process_link_text(self, text, state):
        if state.get('_in_link'):
            return text
        state['_in_link'] = True
        text = self.parse(text)
        state['_in_link'] = False
        return text

    def parse_url_link(self, m, state):
        return self.renderer.link(escape_url(m.group(0)))

    def parse_footnote(self, m, state):
        key = m.group(1)
        def_footnotes = state.get('def_footnotes')
        if not def_footnotes or key not in def_footnotes:
            return self.renderer.text(m.group(0))

        index = state.get('footnote_index', 0)
        index += 1
        state['footnote_index'] = index

        if 'footnotes' not in state:
            state['footnotes'] = [key]
        else:
            state['footnotes'].append(key)
        return self.renderer.footnote_ref(key, index)

    def parse_emphasis(self, m, state):
        text = m.group(0)[1:-1]
        return self.renderer.emphasis(self.parse(text))

    def parse_strong(self, m, state):
        text = m.group(0)[2:-2]
        return self.renderer.strong(self.parse(text))

    def parse_codespan(self, m, state):
        code = re.sub(r'[ \n]+', ' ', m.group(2).strip())
        return self.renderer.codespan(code)

    def parse_strikethrough(self, m, state):
        text = m.group(1)
        return self.renderer.strikethrough(self.parse(text))

    def parse_linebreak(self, m, state):
        return self.renderer.linebreak()

    def parse_inline_html(self, m, state):
        return self.renderer.inline_html(m.group(0))

    def parse_text(self, text):
        text = escape(text)
        return self.renderer.text(text)

    def parse(self, text, state=None, rules=None):
        if rules is None:
            rules = self.default_rules
        if state is None:
            state = {}

        sc = self._create_scanner(rules)
        tokens = self._scan(sc, text, state)
        if self.renderer.IS_TREE:
            return list(tokens)
        return ''.join(tokens)

    def _scan(self, sc, text, state):
        for name, m in sc.iter(text):
            if name == '_text_':
                yield self.parse_text(m)
            else:
                method = self.rules.get(name)[1]
                yield method(m, state)

    def _create_scanner(self, rules):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        lexicon = [(self.rules[n][0], n) for n in rules]
        sc = Scanner(lexicon)
        self._cached_sc[sc_key] = sc
        return sc

    def __call__(self, text, state=None):
        return self.parse(text, state)


def escape(s, quote=True):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace("'", "&#x27;")
    return s


def escape_url(link):
    safe = '/#:()*?=%@+,&'
    if html is None:
        return quote(link, safe=safe)
    return html.escape(quote(html.unescape(link), safe=safe))
