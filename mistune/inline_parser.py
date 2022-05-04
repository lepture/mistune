import re
from .scanner import ScannerParser
from .util import (
    PUNCTUATION,
    ESCAPE_TEXT,
    ESCAPE_CHAR,
    LINK_TEXT,
    LINK_LABEL,
    escape,
    escape_url,
    unikey,
)

HTML_TAGNAME = r'[A-Za-z][A-Za-z0-9-]*'
HTML_ATTRIBUTES = (
    r'(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*'
    r'(?:\s*=\s*(?:[^ "\'=<>`]+|\'[^\']*?\'|"[^\"]*?"))?)*'
)


class InlineState:
    def __init__(self, block_state):
        self.tokens = []
        self.block_state = block_state
        self.in_link = False
        self.in_emphasis = False
        self.in_strong = False

    def copy(self):
        state = InlineState(self)
        state.in_link = self.in_link
        state.in_emphasis = self.in_emphasis
        state.in_strong = self.in_strong
        return state


class InlineParser:
    PREVENT_BACKSLASH = r'(?<!\\)(?P<_slash>(?:\\\\)*)'

    AUTO_EMAIL = (
        r'''<[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9]'''
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*>'
    )

    # we only need to find the start pattern of an inline token
    SPECIFICATION = [
        # `code, ```code
        ('codespan', r'`{1,}'),

        # *w, **w, _w, __w
        ('emphasis', r'\*{1,3}(?=[^\s*])|\b_{1,}(?=[^\s_])'),

        # [link], ![img]
        ('link', r'!?\[' + LINK_TEXT + r'\]'),

        # <https://example.com>. regex copied from commonmark.js
        ('auto_link', r'<[A-Za-z][A-Za-z0-9.+-]{1,31}:[^<>\x00-\x20]*>'),
        ('auto_email', AUTO_EMAIL),
    ]

    ESCAPE = ESCAPE_TEXT


    #: link or image syntax::
    #:
    #: [text](/link "title")
    #: ![alt](/src "title")
    STD_LINK = (
        r'!?\[(' + LINK_TEXT + r')\]\(\s*'

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
        r'!?\[(' + LINK_TEXT + r')\]'
        r'\[(' + LINK_LABEL + r')\]'
    )

    #: linebreak leaves two spaces at the end of line
    SOFT_LINEBREAK = r'(?:\\| {2,})\n(?!\s*$)'

    #: every new line becomes <br>
    HARD_LINEBREAK = r' *\n(?!\s*$)'

    INLINE_HTML = (
        r'(?<!\\)<' + HTML_TAGNAME + HTML_ATTRIBUTES + r'\s*/?>|'  # open tag
        r'(?<!\\)</' + HTML_TAGNAME + r'\s*>|'  # close tag
        r'(?<!\\)<!--(?!>|->)(?:(?!--)[\s\S])+?(?<!-)-->|'  # comment
        r'(?<!\\)<\?[\s\S]+?\?>|'
        r'(?<!\\)<![A-Z][\s\S]+?>|'  # doctype
        r'(?<!\\)<!\[CDATA[\s\S]+?\]\]>'  # cdata
    )

    def __init__(self, renderer, hard_wrap=False):
        self.renderer = renderer
        self.specification = list(self.SPECIFICATION)
        if hard_wrap:
            self.specification.append(('linebreak', self.HARD_LINEBREAK))
        else:
            self.specification.append(('linebreak', self.SOFT_LINEBREAK))

        self.__methods = {
            name: getattr(self, 'parse_' + name) for name, _ in self.specification
        }
        self._sc = None

    def _compile_sc(self):
        regex = '|'.join('(?P<%s>%s)' % pair for pair in self.specification)
        self._sc = re.compile(self.PREVENT_BACKSLASH + regex)

    def register_rule(self, name, pattern, method):
        self.specification.append((name, pattern))
        self.__methods[name] = lambda s, pos, state: method(self, s, pos, state)

    def parse_escape(self, m, state):
        text = m.group(0)[1:]
        return 'text', text

    def parse_link(self, m, state):
        if state.in_link:
            # link can not be in link
            return

        pos = m.end()
        marker = m.group('link')
        def_links = state.block_state.def_links

        if pos < len(m.string):
            c = m.string[pos]
            is_simple = c not in {'[', '('}
        else:
            c = ''
            is_simple = True

        if marker[0] == '!':
            token_type = 'image'
            text = marker[2:-1]
        else:
            token_type = 'link'
            text = marker[1:-1]

        #: Simple form of reference link::
        #:
        #:    [an example]
        #:
        #:    [an example]: https://example.com "optional title"
        if is_simple:
            key = unikey(text)
            if key not in def_links:
                return
            new_state = state.copy()
            new_state.in_link = True
            token = {
                'type': token_type,
                'children': self.render(text, new_state),
                'attrs': def_links[key],
            }
            state.tokens.append(token)
            return pos

        #: Get link from references. The syntax looks like::
        #:
        #:    [an example][id]
        #:
        #:    [id]: https://example.com "optional title"
        if c == '[':
            pass

        #: Standard link or image syntax::
        #:
        #: [text](/link "title")
        #: ![alt](/src "title")


    def parse_auto_link(self, m, state):
        return self._parse_auto_link(False, m, state)

    def parse_auto_email(self, m, state):
        return self._parse_auto_email(True, m, state)

    def _parse_auto_link(self, is_email, m, state):
        if state.in_link:
            return

        if is_email:
            text = m.group('auto_email')[1:-1]
            link = 'mailto:' + text
        else:
            text = m.group('auto_link')[1:-1]
            link = text

        state.tokens.append({
            'type': 'link',
            'children': [{'type': 'text', 'raw': escape(text)}],
            'attrs': {'link': escape_url(link)},
        })
        return m.end()

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
            return 'image', escape_url(link), text, title

        return self.tokenize_link(line, link, text, title, state)

    def parse_ref_link(self, m, state):
        line = m.group(0)
        text = m.group(1)
        key = unikey(m.group(2) or text)
        def_links = state.get('def_links')
        if not def_links or key not in def_links:
            return list(self._scan(line, state, self.ref_link_rules))

        link, title = def_links.get(key)
        link = ESCAPE_CHAR.sub(r'\1', link)
        if title:
            title = ESCAPE_CHAR.sub(r'\1', title)

        if line[0] == '!':
            return 'image', escape_url(link), text, title

        return self.tokenize_link(line, link, text, title, state)

    def parse_emphasis(self, m, state):
        pos = m.end()

        marker = m.group('emphasis')
        if len(marker) > 3:
            if state.in_emphasis or state.in_strong:
                return

            _slice = len(marker) - 3
            hole = marker[:_slice]
            marker = marker[_slice:]
        else:
            if len(marker) == 1 and state.in_emphasis:
                return
            elif len(marker) == 2 and state.in_strong:
                return
            hole = None

        pattern = re.compile(r'(.+)(?<=[^\s])' + re.escape(marker), re.S)
        m = pattern.match(m.string, pos)
        if m:
            if hole:
                state.tokens.append({'type': 'text', 'raw': hole})

            new_state = state.copy()
            text = m.group(1)
            if len(marker) == 1:
                new_state.in_emphasis = True
                children = self.render(text, new_state)
                state.tokens.append({'type': 'emphasis', 'children': children})
            elif len(marker) == 2:
                new_state.in_strong = True
                children = self.render(text, new_state)
                state.tokens.append({'type': 'strong', 'children': children})
            else:
                new_state.in_emphasis = True
                new_state.in_strong = True
                children = self.render(text, new_state)
                state.tokens.append({
                    'type': 'emphasis',
                    'children': [
                        {'type': 'strong', 'children': children},
                    ]
                })
            return m.end()

    def parse_codespan(self, m, state):
        marker = m.group('codespan')
        # require same marker with same length at end
        pattern = re.compile(r'(.+)(?<!`)' + marker + r'(?!`)', re.S)
        pos = m.end()

        m = pattern.match(m.string, pos)
        if m:
            code = m.group(1)
            state.tokens.append({'type': 'codespan', 'raw': code})
            return m.end()

    def parse_linebreak(self, m, state):
        state.tokens.append({'type': 'linebreak'})
        return m.end()

    def parse_inline_html(self, m, state):
        html = m.group(0)
        return 'inline_html', html

    def parse_text(self, text, state):
        return 'text', text

    def parse(self, s, pos, state):
        if not self._sc:
            self._compile_sc()

        while pos < len(s):
            m = self._sc.search(s, pos)
            if not m:
                break

            end_pos = m.start()
            slash = m.group('_slash')
            if slash:
                end_pos += len(slash)

            if end_pos > pos:
                hole = s[pos:end_pos]
                state.tokens.append({'type': 'text', 'raw': hole})

            token_type = m.lastgroup
            func = self.__methods[token_type]
            new_pos = func(m, state)
            if not new_pos:
                pos = end_pos
                break
            pos = new_pos

        if pos < len(s):
            hole = s[pos:]
            state.tokens.append({'type': 'text', 'raw': hole})
        return state.tokens

    def render(self, s: str, state: InlineState):
        self.parse(s, 0, state)
        # return self.renderer.finalize(state.tokens)
        return state.tokens

    def __call__(self, s, state):
        tokens = self.render(s, InlineState(state))
        print(tokens)
        return tokens
