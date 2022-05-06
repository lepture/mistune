import re
from .util import (
    unikey,
    ESCAPE_CHAR_RE,
    LINK_LABEL,
    LINK_BRACKET_RE,
)

_EXPAND_TAB = re.compile(r'^( {0,3})\t', flags=re.M)
_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_AXT_HEADING_TRIM = re.compile(r'\s+#+\s*$')
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)
_LINE_HAS_TEXT = re.compile(r'(\s*)\S')
_DEF_LINK_URL_END = re.compile(r'(\s+|$)')
_DEF_LINK_TITLE_START = re.compile(r'''\s*("|'|\()''')

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

# aggressive block html: comments, pre, script, style
_BLOCK_HTML_AGGRESSIVE = (
    r'(?:<(script|pre|style)(?:\s|>)|<!--)'
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
        self.def_footnotes = {}

        # for list and block quote chain
        self.in_block = None
        self.list_tight = False
        self.parent = None

    def prev_token(self):
        if self.tokens:
            return self.tokens[-1]

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
    state_cls = BlockState

    BLANK_LINE = re.compile(r'^\s*$')
    AXT_HEADING = re.compile(r'^( {0,3})(#{1,6})(?!#+)(?: *$|\s+\S)')
    SETEX_HEADING = re.compile(r'^ *(=|-){2,}[ \t]*$')
    THEMATIC_BREAK = re.compile(
        r'^ {0,3}((?:-[ \t]*){3,}|'
        r'(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$'
    )

    INDENT_CODE = re.compile(r'^(?: {4}| *\t).+$')
    FENCED_CODE = re.compile(r'^( {0,3})(`{3,}|~{3,})([^`]*)$')

    BLOCK_QUOTE = re.compile(r'^( {0,3})>(.*)')
    LIST = re.compile(r'^( {0,3})([\*\+-]|\d{1,9}[.)])([ \t]*|[ \t].+)$')

    DEF_LINK = re.compile(r'^ {0,3}(' + LINK_LABEL + '):')

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
        'blank_line',
        'axt_heading',
        'setex_heading',
        'fenced_code',
        'thematic_break',
        'indent_code',
        'block_quote',
        'list',
        'def_link',
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

        self.block_quote_rules = _filter_def_rules(block_quote_rules)
        self.list_rules = _filter_def_rules(list_rules)
        self.max_block_depth = max_block_depth

        # register default parse methods
        self.__methods = {
            name: getattr(self, 'parse_' + name) for name in self.RULE_NAMES
        }

    def register_rule(self, name, func):
        self.__methods[name] = lambda state, cursor: func(self, state, cursor)

    def parse_blank_line(self, line, cursor, state):
        if self.BLANK_LINE.match(line):
            state.add_token({'type': 'blank_line'}, cursor, cursor)
            return cursor + 1

    def parse_thematic_break(self, line, cursor, state):
        if self.THEMATIC_BREAK.match(line):
            state.add_token({'type': 'thematic_break'}, cursor, cursor)
            return cursor + 1

    def parse_indent_code(self, line, cursor, state):
        if not self.INDENT_CODE.match(line):
            return

        # it is a part of the paragraph
        prev_token = state.prev_token()
        if prev_token and prev_token['type'] == 'paragraph':
            prev_token['text'] += '\n' + line
            prev_token['end_line'] = cursor + state.cursor_root
            return cursor + 1

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
        info = ESCAPE_CHAR_RE.sub(r'\1', m.group(3))
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
        if not m:
            return

        spaces = len(m.group(1))
        level = len(m.group(2))
        text = line[spaces + level:]

        # remove last #
        text = _AXT_HEADING_TRIM.sub('', text).strip()

        token = {'type': 'heading', 'text': text, 'attrs': {'level': level}}
        state.add_token(token, cursor, cursor)
        return cursor + 1

    def parse_setex_heading(self, line, cursor, state):
        prev_token = state.prev_token()
        if prev_token and prev_token['type'] == 'paragraph':
            m = self.SETEX_HEADING.match(line)
            if m:
                level = 1 if m.group(1) == '=' else 2
                prev_token['type'] = 'heading'
                prev_token['attrs'] = {'level': level}
                prev_token['end_line'] = cursor + state.cursor_root
                return cursor + 1

    def parse_def_link(self, line, cursor, state):
        m = self.DEF_LINK.match(line)
        if not m:
            return

        # step 1, parse url
        m1 = _LINE_HAS_TEXT.match(line, m.end())
        if m1:
            url, title_pos = _parse_def_link_url(m1.end() - 1, line)
        else:
            cursor += 1
            line = state.lines[cursor]
            m2 = _LINE_HAS_TEXT.match(next_line)
            if not m2:
                # no url at all
                return
            url, title_pos = _parse_def_link_url(m2.end() - 1, line)

        # step 2, parse title
        title, cursor = _parse_def_link_title(title_pos, line, cursor, state)
        if not title:
            return

        key = unikey(m.group(1)[1:-1])
        if key not in state.def_links:
            state.def_links[key] = {'url': url, 'title': title}
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
            cursor_next = self.parse_blank_line(line, cursor, state)
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
        child = self.state_cls()
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

        self.parse(child.cursor_start, child, rules)
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

        child = self.state_cls()
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
        self.parse(state.cursor_start, state, rules)
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

        prev_token = state.prev_token()
        if prev_token and prev_token['type'] == token_type:
            prev_token['text'] += '\n' + line
            prev_token['end_line'] = cursor + state.cursor_root
            return cursor + 1

        state.add_token({'type': token_type, 'text': line}, cursor, cursor)
        return cursor + 1

    def parse(self, cursor, state, rules):
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

    def render(self, state, inline):
        return self._call_render(state.tokens, state, inline)

    def _call_render(self, tokens, state, inline):
        data = self._iter_render(tokens, state, inline)
        if inline.renderer:
            return inline.renderer.finalize(data)
        return list(data)

    def _iter_render(self, tokens, state, inline):
        for tok in tokens:
            if 'children' in tok:
                children = self._call_render(tok['children'], state, inline)
                tok['children'] = children
            elif 'text' in tok:
                text = tok.pop('text')
                children = inline(text, state)
                tok['children'] = children
            yield tok


def expand_leading_tab(text):
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


def _filter_def_rules(rules):
    return [rule for rule in rules if not rule.startswith('def_')]


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
    line = expand_leading_tab(line)
    if not current:
        current.append(line)
    elif line.startswith(trim):
        line = line.replace(trim, '', 1)
        current.append(line)
    else:
        current[-1] += '\n' + line.lstrip()


def _prepare_list_patterns(current, m1, bullet):
    text = expand_leading_tab(m1.group(3))
    m2 = _LINE_HAS_TEXT.match(text)
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


def _parse_def_link_url(pos, line):
    m1 = LINK_BRACKET_RE.match(line, pos)
    if m1:
        url = m1.group(0)[1:-1]
        return url, m1.end()

    m2 = _DEF_LINK_URL_END.search(line, pos)
    url = line[pos:m2.start()]
    return url, m2.end()


_BREAK_PATTERN = re.compile(r'|'.join([
    BlockParser.BLANK_LINE.pattern,
    BlockParser.SETEX_HEADING.pattern,
    BlockParser.AXT_HEADING.pattern,
    BlockParser.THEMATIC_BREAK.pattern,
    BlockParser.FENCED_CODE.pattern,
    BlockParser.BLOCK_QUOTE.pattern,
    BlockParser.LIST.pattern,
]))


def _parse_def_link_title(pos, line, cursor, state):
    if not _LINE_HAS_TEXT.match(line, pos):
        if cursor >= state.cursor_end:
            return None, cursor

        cursor += 1
        line = state.lines[cursor]
        pos = 0

    m = _DEF_LINK_TITLE_START.match(line, pos)
    if not m:
        return None, cursor

    start_pos = m.end()
    marker = m.group(1)
    end_pattern = re.compile(re.escape(marker) + r'\s*$')

    m2 = end_pattern.search(line, start_pos)
    if m2:
        title = line[start_pos:m2.start()]
        return title, cursor

    rv = line[start_pos:]
    while cursor < state.cursor_end:
        cursor += 1
        line = state.lines[cursor]
        if _BREAK_PATTERN.match(line):
            return None, cursor

        m3 = end_pattern.search(line)
        if m3:
            rv += '\n' + line[:m3.start()]
            return rv, cursor
        rv += '\n' + line
    return None, cursor
