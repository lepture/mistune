import re
from .util import unikey, ESCAPE_CHAR, LINK_LABEL

_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)
_LIST_HAS_TEXT = re.compile(r'^( {0,})\S')
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


class BlockState:
    def __init__(self):
        self.lines = []
        self.tokens = []

        self.cursor_root = 0
        self.cursor_start = 0
        self.cursor_end = 0

        # for saving def references
        self.def_links = {}

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

    def parse(self, state):
        self.scan(state.cursor_start, state, self.rules)

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

            cursor_next = self.parse_list(line, cursor, state)
            if cursor_next:
                break
            text += '\n' + line

        text = _BLOCK_QUOTE_LEADING.sub('', text)
        text = expand_leading_tab(text)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        # scan children state
        lines = text.splitlines()
        child = BlockState()
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
        m1 = self.LIST.match(line)
        if not m1:
            return

        start_line = cursor

        marker = m1.group(2)
        bullet = _get_list_bullet(marker)

        current = []
        trim, next_re, continue_re = _prepare_list_patterns(current, m1, bullet)
        prev_blank_line = not bool(current)

        child = BlockState()
        child.parent = state
        child.in_block = 'list'
        child.cursor_root = start_line

        list_loose = False
        list_items = []

        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]

            m3 = continue_re.match(line)
            if m3:
                _process_continue_line(current, line, trim)
                continue

            m1 = next_re.match(line)
            if m1:
                list_items.append(current)
                current = []
                trim, next_re, continue_re = _prepare_list_patterns(current, m1, bullet)
                prev_blank_line = not bool(current)
                continue

            if prev_blank_line and not m3:
                cursor = cursor - 1
                break

            if self.LIST.match(line):
                cursor = cursor - 1
                break

            prev_blank_line = bool(self.BLANK_LINE.match(line))
            if prev_blank_line and not list_loose:
                list_loose = True

            _process_continue_line(current, line, trim)

        list_items.append(current)
        child.list_tight = not list_loose

        depth = state.depth()
        if depth >= self.max_block_depth:
            rules = list(self.list_rules)
            rules.remove('list')
        else:
            rules = self.list_rules

        ordered = len(marker) != 1
        attrs = {'depth': depth, 'ordered': ordered}

        children = [
            self._parse_list_item(item, child, rules, attrs)
            for item in list_items
        ]

        if ordered:
            start = int(marker[:-1])
            if start != 1:
                # copy, because _parse_list_item is using it
                attrs = dict(attrs)
                attrs['start'] = start

        token = {'type': 'list', 'children': children, 'attrs': attrs}
        state.add_token(token, start_line, cursor)
        return cursor + 1

    def _parse_list_item(self, lines, state, rules, attrs):
        state.tokens = []
        state.lines = lines
        state.cursor_end = len(lines) - 1
        self.scan(state.cursor_start, state, rules)
        # reset cursor root for counting
        state.cursor_root += len(lines)
        return {'type': 'list_item', 'children': state.tokens, 'attrs': attrs}

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

    def render(self, state, inline, renderer=None):
        return self._call_render(state.tokens, state, inline, renderer)

    def _call_render(self, tokens, state, inline, renderer):
        data = self._iter_render(tokens, state, inline, renderer)
        if not renderer:
            return list(data)
        return renderer.finalize(data)

    def _iter_render(self, tokens, state, inline, renderer):
        for tok in tokens:
            if 'children' in tok:
                children = self._call_render(tok['children'], state, inline, renderer)
            elif 'raw' in tok:
                children = tok['raw']
            elif 'text' in tok:
                children = inline(tok['text'], state)
            else:
                if renderer:
                    func = renderer._get_method(tok['type'])
                    yield func()
                else:
                    yield tok
                continue

            if not renderer:
                # update children
                if isinstance(children, list):
                    tok['children'] = children

                yield tok
                continue

            func = renderer._get_method(tok['type'])
            attrs = tok.get('attrs')
            if attrs:
                yield func(children, **attrs)
            else:
                yield func(children)


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


def _process_continue_line(current, line, trim):
    if not current:
        current.append(line)
    elif line.startswith(trim):
        line = line.replace(trim, '', 1)
        current.append(line)
    else:
        current[-1] += '\n' + line.lstrip()


def _prepare_list_patterns(current, m1, bullet):
    text = m1.group(3)
    m2 = _LIST_HAS_TEXT.match(text)
    if m2:
        # indent code
        if text.startswith('     '):
            space_width = 1
        else:
            space_width = len(m2.group(1))

        text = text[space_width:]
        current.append(text)
    else:
        space_width = 1

    # space and marker
    leading_width = len(m1.group(1)) + len(m1.group(2))

    # check if line is new list item
    next_re = re.compile(
        r'^( {0,' + str(leading_width) + '})'
        r'(' + bullet + ')'
        r'([ \t]*|[ \t].+)$'
    )
    continue_width = leading_width + space_width
    trim = ' ' * continue_width

    # same list item
    if continue_width > 4:
        continue_width = 4

    continue_spaces = ' ' * continue_width
    continue_re = re.compile(r'^' + continue_spaces + ' *\S')
    return trim, next_re, continue_re
