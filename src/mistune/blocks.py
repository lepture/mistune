import re
from .scanner import ScannerParser, Matcher

_LINE_BREAK = re.compile(r'\n{2,}')

_TRIM_1 = re.compile(r'^ ')
_TRIM_4 = re.compile(r'^ {1,4}')
_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)
_BLOCK_TAGS = {
    'address', 'article', 'aside', 'base', 'basefont', 'blockquote',
    'body', 'caption', 'center', 'col', 'colgroup', 'dd', 'details',
    'dialog', 'dir', 'div', 'dl', 'dt', 'fieldset', 'figcaption',
    'figure', 'footer', 'form', 'frame', 'frameset', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'head', 'header', 'hr', 'html', 'iframe',
    'legend', 'li', 'link', 'main', 'menu', 'menuitem', 'meta', 'nav',
    'noframes', 'ol', 'optgroup', 'option', 'p', 'param', 'section',
    'source', 'summary', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
    'title', 'tr', 'track', 'ul'
}
_BLOCK_HTML_RULE6 = (
    r'</?(?:' + '|'.join(_BLOCK_TAGS) + r')'
    r'(?: +|\n|/?>)[\s\S]*?'
    r'(?:\n{2,}|\n*$)'
)
_BLOCK_HTML_RULE7 = (
    # open tag
    r'<(?!script|pre|style)([a-z][\w-]*)(?:'
    r' +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"|'
    r''' *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?'''
    r')*? */?>(?=\s*\n)[\s\S]*?(?:\n{2,}|\n*$)|'
    # close tag
    r'</(?!script|pre|style)[a-z][\w-]*\s*>(?=\s*\n)[\s\S]*?(?:\n{2,}|\n*$)'
)
_LIST_ITEM = re.compile(
    r'^(( {0,3})(?:[\*\+-]|\d+[.)])(?: *| +[^\n]+)\n+'
    r'(?:\2 {2,}[^\n]+\n+)*)',
    flags=re.M
)
_LIST_BULLET = re.compile(r'^ *([\*\+-]|\d+[.)])')


class BlockParser(ScannerParser):
    scanner_cls = Matcher

    DEF_LINK = re.compile(
        r' {0,3}\[([^^\]]+)\]:[ \t]*'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *\n+'
    )
    DEF_FOOTNOTE = re.compile(
        r'( {0,3})\[\^([^\]]+)\]:[ \t]*('
        r'[^\n]*\n+'  # [^key]:
        r'(?:\1 {1,3}[^\n]*\n+)*'
        r')'
    )

    AXT_HEADING = re.compile(
        r' {0,3}(#{1,6})(?!#+)(?: *\n+|'
        r'\s+([^\n]*?)(?:\n+|\s+?#+\s*\n+))'
    )
    SETEX_HEADING = re.compile(r'([^\n]+)\n *(=|-){2,}[ \t]*\n+')
    THEMATIC_BREAK = re.compile(
        r' {0,3}((?:-[ \t]*){3,}|'
        r'(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})\n+'
    )

    INDENT_CODE = re.compile(r'(?:(?: {4}| *\t)[^\n]+\n*)+')

    FENCED_CODE = re.compile(
        r' {0,3}(`{3,}|~{3,})([^`\n]*)\n'
        r'(?:|([\s\S]*?)\n)'
        r'(?: {0,3}\1[~`]* *\n+|$)'
    )
    BLOCK_QUOTE = re.compile(
        r'(?: {0,3}>[^\n]+(?:\n'
        r'(?! {0,3}(?:-[ \t]*){3,}\n+)'
        r'[^\n]+)*\n*)+'
    )

    BLOCK_HTML = re.compile((
        r' {0,3}(?:'
        r'<(script|pre|style)[\s>][\s\S]*?(?:</\1>[^\n]*\n+|$)|'
        r'<!--(?!-?>)[\s\S]*?-->[^\n]*\n+|'
        r'<\?[\s\S]*?\?>[^\n]*\n+|'
        r'<![A-Z][\s\S]*?>[^\n]*\n+|'
        r'<!\[CDATA\[[\s\S]*?\]\]>[^\n]*\n+'
        r'|' + _BLOCK_HTML_RULE6 + '|' + _BLOCK_HTML_RULE7 + ')'
    ), re.I)

    LIST = re.compile(
        # * list
        r'(?:( {0,3})\*(?:[ \t]*|[ \t]+(?!(?:\*[ \t]*){2,}\n+)[^\n]+)\n+'
        r'(?:\1(?: {2,}| *\t)[^\n]+\n+)*)+|'

        # - list
        r'(?:( {0,3})\-(?:[ \t]*|[ \t]+(?!(?:\-[ \t]*){2,}\n+)[^\n]+)\n+'
        r'(?:\2(?: {2,}| *\t)[^\n]+\n+)*)+|'

        # + list
        r'(?:( {0,3})\+(?:[ \t]*|[ \t]+[^\n]+)\n+'
        r'(?:\3(?: {2,}| *\t)[^\n]+\n+)*)+|'

        # 1. list
        r'(?:( {0,3})\d{0,9}\.(?:[ \t]*|[ \t]+[^\n]+)\n+'
        r'(?:\4(?: {3,}| *\t)[^\n]+\n+)*)+|'

        # 1) list
        r'(?:( {0,3})\d{0,9}\)(?:[ \t]*|[ \t]+[^\n]+)\n+'
        r'(?:\5(?: {3,}| *\t)[^\n]+\n+)*)+'
    )

    RULE_NAMES = (
        'thematic_break', 'fenced_code', 'indent_code',
        'block_quote', 'block_html', 'list',
        'axt_heading', 'setex_heading',
        'def_link', 'def_footnote',
    )

    def parse_indent_code(self, m, state):
        text = expand_leading_tab(m.group(0))
        code = _INDENT_CODE_TRIM.sub('', text)
        return self.tokenize_block_code(code, None, state)

    def parse_fenced_code(self, m, state):
        info = m.group(2)
        code = m.group(3) or ''
        return self.tokenize_block_code(code + '\n', info, state)

    def tokenize_block_code(self, code, info, state):
        token = {'type': 'block_code', 'raw': code}
        if info:
            token['params'] = (info, )
        return token

    def parse_axt_heading(self, m, state):
        level = len(m.group(1))
        text = m.group(2) or ''
        text = text.strip()
        if set(text) == {'#'}:
            text = ''
        return self.tokenize_heading(text, level, state)

    def parse_setex_heading(self, m, state):
        level = 1 if m.group(2) == '=' else 2
        text = m.group(1)
        text = text.strip()
        return self.tokenize_heading(text, level, state)

    def tokenize_heading(self, text, level, state):
        return {'type': 'heading', 'text': text, 'params': (level,)}

    def parse_thematic_break(self, m, state):
        return {'type': 'thematic_break', 'blank': True}

    def parse_block_quote(self, m, state):
        depth = state.get('in_block_quote', 0) + 1
        if depth > 5:
            rules = list(self.default_rules)
            rules.remove('block_quote')
        else:
            rules = None

        state['in_block_quote'] = depth

        # TODO: fix block quote text
        text = _BLOCK_QUOTE_LEADING.sub('', m.group(0))
        text = _TRIM_1.sub('', expand_leading_tab(text))

        children = self.parse(text, state, rules)
        state['in_block_quote'] = depth - 1
        return {'type': 'block_quote', 'children': children}

    def parse_list(self, m, state):
        text = m.group(0)
        m = _LIST_BULLET.match(text)

        tight = '\n\n' not in text.strip()
        state['tight'] = tight

        marker = m.group(1)
        ordered = len(marker) != 1
        params = (ordered, None)
        if ordered:
            start = int(marker[:-1])
            if start != 1:
                params = (ordered, start)

        depth = state.get('in_list', 0) + 1
        if depth > 5:
            rules = list(self.default_rules)
            rules.remove('list')
        else:
            rules = None

        state['in_list'] = depth
        children = list(self.parse_list_items(text, state, rules))
        state['in_list'] = depth - 1
        token = {'type': 'list', 'children': children, 'params': params}
        state['tight'] = None
        return token

    def parse_list_items(self, text, state, rules):
        items = _LIST_ITEM.findall(text)
        for text, leading in items:
            text_length = len(text)
            text = _LIST_BULLET.sub('', text)

            if not text.strip():
                yield {'type': 'list_item', 'text': ''}
                continue

            space = text_length - len(text)
            text = expand_leading_tab(text)
            if text.startswith('     '):
                text = text[1:]
                space += 1
            else:
                text_length = len(text)
                text = _TRIM_4.sub('', text)
                space += max(text_length - len(text), 1)

            # outdent
            if '\n ' in text:
                pattern = re.compile(r'\n {1,' + str(space) + r'}')
                text = pattern.sub(r'\n', text)

            text = text.lstrip('\n')
            children = self.parse(text, state, rules)
            yield {'type': 'list_item', 'children': children}

    def parse_block_html(self, m, state):
        html = m.group(0).rstrip()
        return {'type': 'block_html', 'raw': html}

    def parse_def_link(self, m, state):
        key = m.group(1).lower()
        link = m.group(2)
        title = m.group(3)
        if key not in state['def_links']:
            state['def_links'][key] = (link, title)

    def parse_def_footnote(self, m, state):
        key = m.group(2).lower()
        if key not in state['def_footnotes']:
            state['def_footnotes'][key] = m.group(3)

    def parse_footnote_item(self, k, i, state):
        def_footnotes = state['def_footnotes']
        text = def_footnotes[k]

        stripped_text = text.strip()
        if '\n' not in stripped_text:
            children = [{'type': 'paragraph', 'text': stripped_text}]
        else:
            lines = text.splitlines()
            for second_line in lines[1:]:
                if second_line:
                    break

            spaces = len(second_line) - len(second_line.lstrip())
            pattern = re.compile(r'^ {' + str(spaces) + r',}', flags=re.M)
            text = pattern.sub('', text)
            children = self.parse_text(text, state)
            if not isinstance(children, list):
                children = [children]

        return {
            'type': 'footnote_item',
            'children': children,
            'params': (k, i)
        }

    def parse_text(self, text, state):
        if state.get('tight') is True:
            return {'type': 'text', 'text': text.strip()}

        tokens = []
        for p in _LINE_BREAK.split(text):
            p = p.strip()
            if p:
                tokens.append({'type': 'paragraph', 'text': p})
        return tokens

    def parse(self, s, state, rules=None):
        if rules is None:
            rules = self.default_rules

        tokens = []
        for tok in self._scan(s, state, rules):
            if isinstance(tok, dict):
                tokens.append(tok)
            elif tok and isinstance(tok, list):
                tokens.extend(tok)

        return tokens

    def render(self, tokens, inline, state):
        data = self._iter_render(tokens, inline, state)
        if inline.renderer.IS_TREE:
            return list(data)
        return ''.join(data)

    def _iter_render(self, tokens, inline, state):
        for tok in tokens:
            method = inline.renderer._get_method(tok['type'])
            if 'blank' in tok:
                yield method()
                continue

            if 'children' in tok:
                children = self.render(tok['children'], inline, state)
            elif 'raw' in tok:
                children = tok['raw']
            else:
                children = inline(tok['text'], state)
            params = tok.get('params')
            if params:
                yield method(children, *params)
            else:
                yield method(children)


def expand_leading_tab(text):
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


def _expand_tab_repl(m):
    s = m.group(1)
    return s + ' ' * (4 - len(s))
