import re
from .util import unikey, ESCAPE_CHAR, LINK_LABEL

_NEW_LINES = re.compile(r'\r\n|\r')
_BLANK_LINES = re.compile(r'^ +$', re.M)

_TRIM_4 = re.compile(r'^ {1,4}')
_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
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

_PARAGRAPH_SPLIT = re.compile(r'\n{2,}')
_LIST_BULLET = re.compile(r'^ *([\*\+-]|\d+[.)])')


class State:
    def __init__(self):
        self.lines = []
        self.tokens = []

        self.cursor_root = 0
        self.cursor_start = 0
        self.cursor_end = 0

        # for saving def references
        self.def_links = {}
        self.def_footnotes = {}
        self.footnotes = {}

        # for list and block quote chain
        self.in_block = None
        self.parent = None

    def add_token(self, token, start_line, end_line):
        token['start_line'] = start_line + self.cursor_root
        token['end_line'] = end_line + self.cursor_root
        self.tokens.append(token)

    def depth(self):
        d = 0
        parent = self.parent
        while parent:
            d += 1
            parent = parent.parent
        return d


class BlockParser:

    BLANK_LINE = re.compile(r'^\s*$')
    AXT_HEADING = re.compile(r'^ {0,3}(#{1,6})(?!#+)(.*)')
    SETEX_HEADING = re.compile(r'^ *(=|-){2,}[ \t]*$')
    THEMATIC_BREAK = re.compile(
        r'^ {0,3}((?:-[ \t]*){3,}|'
        r'(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$'
    )

    INDENT_CODE = re.compile(r'^(?: {4}| *\t).+$')
    FENCED_CODE = re.compile(r'^( {0,3})(`{3,}|~{3,})([^`]*)$')

    DEF_LINK = re.compile(r'^ {0,3}\[((?:[^\\[\]]|\.){0,1000})\]:')

    BLOCK_QUOTE = re.compile(r'^( {0,3})>(.*)')
    LIST = re.compile(r'^( {0,3})([\*\+-]|\d{1,9}[.)])([ \t]*|[ \t].+)$')

    BLOCK_HTML = re.compile((
        r' {0,3}(?:'
        r'<(script|pre|style)[\s>][\s\S]*?(?:</\1>[^\n]*\n+|$)|'
        r'<!--(?!-?>)[\s\S]*?-->[^\n]*\n+|'
        r'<\?[\s\S]*?\?>[^\n]*\n+|'
        r'<![A-Z][\s\S]*?>[^\n]*\n+|'
        r'<!\[CDATA\[[\s\S]*?\]\]>[^\n]*\n+'
        r'|' + _BLOCK_HTML_RULE6 + '|' + _BLOCK_HTML_RULE7 + ')'
    ), re.I)

    RULE_NAMES = (
        'newline',
        'axt_heading',
        'setex_heading',
        'fenced_code',
        'thematic_break',
        'indent_code',
        'block_quote',
        # 'list',
        # 'def_link',
        # 'block_html',
    )

    def __init__(self, rules=None, block_quote_rules=None, list_rules=None, max_block_depth=6):
        if rules is None:
            rules = list(self.RULE_NAMES)

        if block_quote_rules is None:
            block_quote_rules = list(self.RULE_NAMES)

        if list_rules is None:
            list_rules = list(self.RULE_NAMES)

        self.rules = rules
        self.block_quote_rules = block_quote_rules
        self.list_rules = list_rules
        self.max_block_depth = max_block_depth

        self.__methods = {
            name: getattr(self, 'parse_' + name) for name in self.RULE_NAMES
        }

    def register_rule(self, name, func):
        self.__methods[name] = lambda state, cursor: func(self, state, cursor)

    def parse_newline(self, line, cursor, state):
        if self.BLANK_LINE.match(line):
            state.add_token({'type': 'newline'}, cursor, cursor)
            return cursor + 1

    def parse_thematic_break(self, line, cursor, state):
        if self.THEMATIC_BREAK.match(line):
            state.add_token({'type': 'thematic_break'}, cursor, cursor)
            return cursor + 1

    def parse_indent_code(self, line, cursor, state):
        if not self.INDENT_CODE.match(line):
            return

        start_line = cursor
        code = line

        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]
            if self.INDENT_CODE.match(line) or self.BLANK_LINE.match(line):
                code += '\n' + line
            else:
                cursor = cursor - 1
                break

        code = expand_leading_tab(code)
        code = _INDENT_CODE_TRIM.sub('', code)
        state.add_token({'type': 'block_code', 'raw': code}, start_line, cursor)
        return cursor + 1

    def parse_fenced_code(self, line, cursor, state):
        m = self.FENCED_CODE.match(line)
        if not m:
            return

        start_line = cursor
        spaces = m.group(1)
        marker = m.group(2)
        info = ESCAPE_CHAR.sub(r'\1', m.group(3))
        _end = re.compile('^ {0,3}' + marker[0] + '{' + str(len(marker)) + r',}\s*$')

        code = ''
        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]
            if _end.match(line):
                break
            code += line + '\n'

        if spaces and code:
            _trim_pattern = re.compile('^' + spaces, re.M)
            code = _trim_pattern.sub('', code)

        token = {'type': 'block_code', 'raw': code}
        if info:
            token['attrs'] = {'info': info}

        state.add_token(token, start_line, cursor)
        return cursor + 1

    def parse_axt_heading(self, line, cursor, state):
        m = self.AXT_HEADING.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2) or ''
            text = text.strip()
            if set(text) == {'#'}:
                text = ''

            token = {'type': 'heading', 'text': text, 'attrs': {'level': level}}
            state.add_token(token, cursor, cursor)
            return cursor + 1

    def parse_setex_heading(self, line, cursor, state):
        if state.tokens:
            m = self.SETEX_HEADING.match(line)
            if m:
                prev_token = state.tokens[-1]
                if prev_token['type'] == 'paragraph':
                    level = 1 if m.group(2) == '=' else 2
                    prev_token['type'] = 'heading'
                    prev_token['attrs'] = {'level': level}
                    prev_token['end_line'] = cursor + state.cursor_root
                    return cursor + 1

    def parse_def_link(self, line, cursor, state):
        m = self.DEF_LINK.match(line)
        if not m:
            return
        # TODO
        text = line[m.end()]
        key = unikey(m.group(1))
        link = ''
        title = ''
        if key not in state.def_links:
            state.def_links[key] = (link, title)
        return cursor + 1

    def get_block_quote_rules(self, depth):
        if depth > self.BLOCK_QUOTE_MAX_DEPTH - 1:
            rules = list(self.block_quote_rules)
            rules.remove('block_quote')
            return rules
        return self.block_quote_rules

    def parse_block_quote(self, line, cursor, state):
        m = self.BLOCK_QUOTE.match(line)
        if not m:
            return

        start_line = cursor

        # cleanup at first to detect if it is code block
        text = _BLOCK_QUOTE_LEADING.sub('', line)
        text = expand_leading_tab(text)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        require_marker = bool(
            self.BLANK_LINE.match(text)
            or self.INDENT_CODE.match(text)
            or self.FENCED_CODE.match(text)
        )

        cursor_next = None
        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]

            if require_marker and not self.BLOCK_QUOTE.match(line):
                cursor = cursor - 1
                break

            # blank line break block quote
            cursor_next = self.parse_newline(line, cursor, state)
            if cursor_next:
                break

            # hr break block quote
            cursor_next = self.parse_thematic_break(line, cursor, state)
            if cursor_next:
                break
            # TODO: list

            text += '\n' + line

        text = _BLOCK_QUOTE_LEADING.sub('', text)
        text = expand_leading_tab(text)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        # scan children state
        lines = text.splitlines()
        child = State()
        child.cursor_root = start_line
        child.in_block = 'block_quote'
        child.parent = state
        child.lines = lines
        child.cursor_end = len(lines) - 1

        if state.depth() >= self.max_block_depth:
            rules = list(self.block_quote_rules)
            rules.remove('block_quote')
        else:
            rules = self.block_quote_rules

        self.scan(child.cursor_start, child, rules)
        token = {'type': 'block_quote', 'children': child.tokens}

        if cursor_next:
            last_token = state.tokens.pop()
            state.add_token(token, start_line, cursor - 1)
            state.tokens.append(last_token)
            return cursor_next

        state.add_token(token, start_line, cursor)
        return cursor + 1

    def get_list_rules(self, depth):
        if depth > self.LIST_MAX_DEPTH - 1:
            rules = list(self.list_rules)
            rules.remove('list_start')
            return rules
        return self.list_rules

    def parse_list_start(self, m, state, string):
        items = []
        spaces = m.group(1)
        marker = m.group(2)
        items, pos = _find_list_items(string, m.start(), spaces, marker)
        tight = '\n\n' not in ''.join(items).strip()

        ordered = len(marker) != 1
        if ordered:
            start = int(marker[:-1])
            if start == 1:
                start = None
        else:
            start = None

        list_tights = state.get('list_tights', [])
        list_tights.append(tight)
        state['list_tights'] = list_tights

        depth = len(list_tights)
        rules = self.get_list_rules(depth)
        children = [
            self.parse_list_item(item, depth, state, rules)
            for item in items
        ]
        list_tights.pop()
        params = (ordered, depth, start)
        token = {'type': 'list', 'children': children, 'params': params}
        return token, pos

    def parse_list_item(self, text, depth, state, rules):
        text = self.normalize_list_item_text(text)
        if not text:
            children = [{'type': 'block_text', 'text': ''}]
        else:
            children = self.parse(text, state, rules)
        return {
            'type': 'list_item',
            'params': (depth,),
            'children': children,
        }

    @staticmethod
    def normalize_list_item_text(text):
        text_length = len(text)
        text = _LIST_BULLET.sub('', text)

        if not text.strip():
            return ''

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
        return text

    def parse_block_html(self, m, state):
        html = m.group(0).rstrip()
        return {'type': 'block_html', 'raw': html}

    def parse_paragraph(self, line, cursor, state):
        if state.tokens:
            prev_token = state.tokens[-1]
            if prev_token['type'] == 'paragraph':
                prev_token['text'] += '\n' + line
                prev_token['end_line'] = cursor + state.cursor_root
                return cursor + 1

        state.add_token({'type': 'paragraph', 'text': line}, cursor, cursor)
        return cursor + 1

    def parse(self, state):
        self.scan(state.cursor_start, state, self.rules)

    def scan(self, cursor, state, rules):
        while cursor <= state.cursor_end:
            cursor = self._scan_rules(cursor, state, rules)

    def _scan_rules(self, cursor, state, rules):
        line = state.lines[cursor]

        for name in rules:
            func = self.__methods[name]
            cursor_next = func(line, cursor, state)
            if cursor_next:
                return cursor_next

        cursor_next = self.parse_paragraph(line, cursor, state)
        return cursor_next


    def render(self, tokens, inline, state):
        data = self._iter_render(tokens, inline, state)
        return inline.renderer.finalize(data)

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



def cleanup_lines(s):
    s = _NEW_LINES.sub('\n', s)
    s = _BLANK_LINES.sub('', s)
    return s


def expand_leading_tab(text):
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


def _expand_tab_repl(m):
    s = m.group(1)
    return s + ' ' * (4 - len(s))


def _create_list_item_pattern(spaces, marker):
    prefix = r'( {0,' + str(len(spaces) + len(marker)) + r'})'

    if len(marker) > 1:
        if marker[-1] == '.':
            prefix = prefix + r'\d{0,9}\.'
        else:
            prefix = prefix + r'\d{0,9}\)'
    else:
        if marker == '*':
            prefix = prefix + r'\*'
        elif marker == '+':
            prefix = prefix + r'\+'
        else:
            prefix = prefix + r'-'

    s1 = ' {' + str(len(marker) + 1) + ',}'
    if len(marker) > 4:
        s2 = ' {' + str(len(marker) - 4) + r',}\t'
    else:
        s2 = r' *\t'
    return re.compile(
        prefix + r'(?:[ \t]*|[ \t]+[^\n]+)\n+'
        r'(?:\1(?:' + s1 + '|' + s2 + ')'
        r'[^\n]+\n+)*'
    )


def _find_list_items(string, pos, spaces, marker):
    items = []

    if marker in {'*', '-'}:
        is_hr = re.compile(
            r' *((?:-[ \t]*){3,}|(?:\*[ \t]*){3,})\n+'
        )
    else:
        is_hr = None

    pattern = _create_list_item_pattern(spaces, marker)
    while 1:
        m = pattern.match(string, pos)
        if not m:
            break

        text = m.group(0)
        if is_hr and is_hr.match(text):
            break

        new_spaces = m.group(1)
        if new_spaces != spaces:
            spaces = new_spaces
            pattern = _create_list_item_pattern(spaces, marker)

        items.append(text)
        pos = m.end()
    return items, pos
