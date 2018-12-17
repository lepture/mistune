import re
from .scanner import ScannerParser, escape, escape_url

PUNCTUATION = r'''\\!"#$%&'()*+,./:;<=>?@\[\]^`{}|_~-'''
ESCAPE = r'\\[' + PUNCTUATION + ']'
HTML_TAGNAME = r'[A-Za-z][A-Za-z0-9-]*'
HTML_ATTRIBUTES = (
    r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*'
    r'(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'
)
ESCAPE_CHAR = re.compile(r'''\\([\\!"#$%&'()*+,.\/:;<=>?@\[\]^`{}|_~-])''')


class InlineParser(ScannerParser):
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

    RULE_NAMES = (
        'escape', 'inline_html', 'auto_link', 'url_link', 'footnote',
        'std_link', 'ref_link', 'ref_link2', 'strong', 'emphasis',
        'codespan', 'strikethrough', 'linebreak',
    )

    def __init__(self, renderer):
        super(InlineParser, self).__init__()
        self.renderer = renderer

    def parse_escape(self, m, state):
        text = m.group(0)[1:]
        return 'text', escape(text)

    def parse_auto_link(self, m, state):
        text = m.group(1)
        if '@' in text and not text.lower().startswith('mailto:'):
            link = 'mailto:' + text
        else:
            link = text
        return 'link', escape_url(link), text

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
            return 'image', link, text, title

        text = self._process_link_text(text, state)
        return 'link', escape_url(link), text, title

    def parse_ref_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        key = (m.group(2) or text).lower()
        def_links = state.get('def_links')
        if not def_links or key not in def_links:
            return 'text', line

        link, title = def_links.get(key)
        link = ESCAPE_CHAR.sub(r'\1', link)
        if title:
            title = ESCAPE_CHAR.sub(r'\1', title)

        if line[0] == '!':
            return 'image', link, text, title

        if m.group(2):
            text = self._process_link_text(text, state)
        return 'link', escape_url(link), text, title

    def parse_ref_link2(self, m, state):
        return self.parse_ref_link(m, state)

    def _process_link_text(self, text, state):
        if state.get('_in_link'):
            return text
        state['_in_link'] = True
        text = self.parse(text, state)
        state['_in_link'] = False
        return text

    def parse_url_link(self, m, state):
        return 'link', escape_url(m.group(0))

    def parse_footnote(self, m, state):
        key = m.group(1).lower()
        def_footnotes = state.get('def_footnotes')
        if not def_footnotes or key not in def_footnotes:
            return 'text', m.group(0)

        index = state.get('footnote_index', 0)
        index += 1
        state['footnote_index'] = index
        state['footnotes'].append(key)
        return 'footnote_ref', key, index

    def parse_emphasis(self, m, state):
        text = m.group(0)[1:-1]
        return 'emphasis', self.parse(text, state)

    def parse_strong(self, m, state):
        text = m.group(0)[2:-2]
        return 'strong', self.parse(text, state)

    def parse_codespan(self, m, state):
        code = re.sub(r'[ \n]+', ' ', m.group(2).strip())
        return 'codespan', code

    def parse_strikethrough(self, m, state):
        text = m.group(1)
        return 'strikethrough', self.parse(text, state)

    def parse_linebreak(self, m, state):
        return 'linebreak',

    def parse_inline_html(self, m, state):
        html = m.group(0)
        return 'inline_html', html

    def parse_text(self, text, state):
        return 'text', escape(text)

    def parse(self, s, state, rules=None):
        if rules is None:
            rules = self.default_rules

        tokens = (
            self.renderer._get_method(t[0])(*t[1:])
            for t in self._scan(s, state, rules)
        )
        if self.renderer.IS_TREE:
            return list(tokens)
        return ''.join(tokens)

    def __call__(self, s, state):
        return self.parse(s, state)


def expand_leading_tab(text):
    return ''.join(_expand_lines_leading_tab(text.splitlines(True)))


def _expand_lines_leading_tab(lines):
    for line in lines:
        if ' \t' not in line:
            yield line
            continue
        spaces = len(line) - len(line.lstrip(' '))
        if spaces < 4 and line[spaces] == '\t':
            yield line.replace('\t', ' ' * (4 - spaces), 1)
        else:
            yield line
