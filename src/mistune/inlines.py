import re
from .scanner import Scanner

ESCAPE = r'''\\[\\!"#$%&'()*+,.\/:;<=>?@\[\]^`{}|_~-]'''
HTML_TAGNAME = r'[A-Za-z][A-Za-z0-9-]*'
HTML_ATTRIBUTES = (
    r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*'
    r'(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'
)
ESCAPE_CHAR = re.compile(r'''\\([\\!"#$%&'()*+,.\/:;<=>?@\[\]^`{}|_~-])''')


class InlineTokenizer(object):
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
        r'(?P<link_url><)?([\s\S]*?)(?(link_url)>)'
        r'''(?:\s+(?P<link_quote>['"])([\s\S]*?)(?P=link_quote))?\s*'''
        r'\)'
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

    #: simple form of reference link::
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
        r'\b_((?:__|[^_])+?)_\b'  # _word_
        r'|'
        r'\*((?:\*\*|[^\*])+?)\*(?!\*)'  # *word*
    )

    #: strong with ** or __::
    #:
    #:    **text**
    #:    __text__
    STRONG = (
        r'__([\s\S]+?)__(?!_)'  # __word__
        r'|'
        r'\*\*([\s\S]+?)\*\*(?!\*)'  # **word**
    )

    #: codespan with `::
    #:
    #:    `code`
    CODESPAN = (
        r'(`+)\s*((?:\\`|[^\1])*?)\s*\1(?!`)'
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
        self.rules[name] = (pattern, lambda m: method(self, m))

    def parse_escape(self, m, state):
        text = m.group(0)[1:]
        return self.renderer.text(text)

    def parse_auto_link(self, m, state):
        return self.renderer.link(m.group(1))

    def parse_std_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        link = ESCAPE_CHAR.sub(r'\1', m.group(3))
        title = m.group(5)
        if title:
            title = ESCAPE_CHAR.sub(r'\1', title)

        # TODO: parse text
        if line[0] == '!':
            return self.renderer.image(link, text, title)
        return self.renderer.link(link, text, title)

    def parse_ref_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        key = m.group(2)
        if not key:
            key = text

        def_links = state.get('def_links')
        if not def_links or key not in def_links:
            return self.renderer.text(line)

        # TODO: parse text
        link, title = def_links.get(key)
        if line[0] == '!':
            return self.renderer.image(link, text, title)
        return self.renderer.link(link, text, title)

    def parse_url_link(self, m, state):
        return self.renderer.link(m.group(0))

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
        text = m.group(1) or m.group(2)
        return self.renderer.emphasis(self.parse(text))

    def parse_strong(self, m, state):
        text = m.group(1) or m.group(2)
        return self.renderer.strong(self.parse(text))

    def parse_codespan(self, m, state):
        code = m.group(2)
        code = ESCAPE_CHAR.sub(r'\1', code)
        return self.renderer.codespan(code)

    def parse_strikethrough(self, m, state):
        text = m.group(1)
        return self.renderer.strikethrough(self.parse(text))

    def parse_linebreak(self, m, state):
        return self.renderer.linebreak()

    def parse_inline_html(self, m, state):
        return self.renderer.inline_html(m.group(0))

    def parse(self, text, state=None, rules=None):
        if rules is None:
            rules = self.default_rules
        if state is None:
            state = {}

        sc = self._create_scanner(rules, state)
        tokens = sc.iter(text, self.renderer.text)
        if self.renderer.IS_AST:
            return list(tokens)
        return ''.join(tokens)

    def _create_scanner(self, rules, state):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        def _lexicon():
            for n in rules:
                pattern, method = self.rules[n]
                yield pattern, lambda m: method(m, state)

        sc = Scanner(_lexicon())
        self._cached_sc[sc_key] = sc
        return sc
