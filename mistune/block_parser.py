import re
from .util import unikey, ESCAPE_CHAR, LINK_LABEL

_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)
_LIST_SPACE = re.compile(r'^( {0,4})\S')
_LIST_BULLET = re.compile(r'^ *([\*\+-]|\d+[.)])')

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
        self.list_tight = False
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
        'list',
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

    def parse_block_quote(self, line, cursor, state):
        m = self.BLOCK_QUOTE.match(line)
        if not m:
            return

        start_line = cursor

        # cleanup at first to detect if it is code block
        text = m.group(2)
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

    def parse_list(self, line, cursor, state):
        m = self.LIST.match(line)
        if not m:
            return

        start_line = cursor
        marker = m.group(2)
        text = m.group(3)

        ordered = len(marker) != 1
        if ordered:
            leading_spaces = len(m.group(1)) + 2
        else:
            leading_spaces = len(m.group(1)) + 1

        trim_space = r'^ {0,' + str(leading_spaces) + '}'
        bullet = _get_list_bullet(marker)
        trim_pattern = re.compile(trim_space)
        next_pattern = re.compile(trim_space + bullet + r'([ \t]*|[ \t].+)$')

        m2 = _LIST_SPACE.match(text)
        if m2:
            prev_blank_line = False
            current_item = text[1:]
            total_spaces = leading_spaces + len(m2.group(1))
        else:
            prev_blank_line = True
            current_item = ''
            total_spaces = leading_spaces + 1

        child = State()
        child.parent = state
        child.in_block = 'list'
        child.cursor_root = start_line

        # same list item
        continue_pattern = re.compile(r'^( {' + str(total_spaces) + '}) *\S')
        list_loose = False
        list_items = []

        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]

            m3 = next_pattern.match(line)
            if m3:
                list_items.append(current_item)
                current_item = m3.group(1)
                if _LIST_SPACE.match(current_item):
                    current_item = current_item[1:]
                else:
                    current_item = ''
                continue

            m4 = continue_pattern.match(line)
            if m4:
                current_item += '\n' + line[len(m4.group(1)):]
                continue
            elif prev_blank_line:
                cursor = cursor - 1
                break

            prev_blank_line = bool(self.BLANK_LINE.match(line))
            if prev_blank_line and not list_loose:
                list_loose = True
            current_item += '\n' + trim_pattern.sub('', line)

        list_items.append(current_item)
        child.list_tight = not list_loose

        depth = state.depth()
        if depth >= self.max_block_depth:
            rules = list(self.list_rules)
            rules.remove('list')
        else:
            rules = self.list_rules

        children = [self._parse_list_item(item, child, rules) for item in list_items]

        attrs = {'depth': depth}
        if ordered:
            start = int(marker[:-1])
            if start != 1:
                attrs['start'] = start

        token = {'type': 'list', 'children': children, 'attrs': attrs}
        state.add_token(token, start_line, cursor)
        return cursor + 1

    def _parse_list_item(self, text, state, rules):
        lines = text.splitlines()
        state.tokens = []
        state.lines = lines
        state.cursor_end = len(lines) - 1
        self.scan(state.cursor_start, state, rules)
        # reset cursor root for counting
        state.cursor_root += len(lines)
        return {'type': 'list_item', 'children': state.tokens}

    def parse_block_html(self, m, state):
        html = m.group(0).rstrip()
        return {'type': 'block_html', 'raw': html}

    def parse_paragraph(self, line, cursor, state):
        if state.list_tight:
            token_type = 'block_text'
        else:
            token_type = 'paragraph'

        if state.tokens:
            prev_token = state.tokens[-1]
            if prev_token['type'] == token_type:
                prev_token['text'] += '\n' + line
                prev_token['end_line'] = cursor + state.cursor_root
                return cursor + 1

        state.add_token({'type': token_type, 'text': line}, cursor, cursor)
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



def expand_leading_tab(text):
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


def _expand_tab_repl(m):
    s = m.group(1)
    return s + ' ' * (4 - len(s))


def _get_list_bullet(marker):
    c = marker[-1]
    if c == '.':
        bullet = r'\d{0,9}\.'
    elif c == ')':
        bullet = r'\d{0,9}\)'
    elif marker == '*':
        bullet = r'\*'
    elif marker == '+':
        bullet = r'\+'
    else:
        bullet = '-'
    return bullet



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
