import re
from .util import (
    unikey,
    ESCAPE_CHAR_RE,
    LINK_LABEL,
    LINK_BRACKET_RE,
    HTML_TAGNAME,
    HTML_ATTRIBUTES,
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
_OPEN_TAG_END = re.compile(HTML_ATTRIBUTES + r'\s*>\s*$')
_CLOSE_TAG_END = re.compile(r'\s*>\s*$')


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
        self.list_tight = True
        self.parent = None

    def prev_token(self):
        if self.tokens:
            return self.tokens[-1]

    def add_token(self, token, start_line, end_line):
        token['start_line'] = start_line + self.cursor_root
        token['end_line'] = end_line + self.cursor_root
        self.tokens.append(token)

    def add_to_paragraph(self, line, cursor):
        prev_token = self.prev_token()
        if prev_token and prev_token['type'] == 'paragraph':
            prev_token['text'] += '\n' + line
            prev_token['end_line'] = cursor + self.cursor_root
            return cursor + 1

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
    SETEX_HEADING = re.compile(r'^ *(=|-){1,}[ \t]*$')
    THEMATIC_BREAK = re.compile(
        r'^ {0,3}((?:-[ \t]*){3,}|'
        r'(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$'
    )

    INDENT_CODE = re.compile(r'^(?: {4}| *\t).+$')
    FENCED_CODE = re.compile(r'^( {0,3})(`{3,}|~{3,})')

    BLOCK_QUOTE = re.compile(r'^( {0,3})>(.*)')
    LIST = re.compile(r'^( {0,3})([\*\+-]|\d{1,9}[.)])([ \t]*|[ \t].+)$')

    DEF_LINK = re.compile(r'^ {0,3}(' + LINK_LABEL + '):')

    BLOCK_HTML = re.compile(
        r'( {0,3})(?:'
        r'<(?P<open_tag>' + HTML_TAGNAME + r')|'  # open tag
        r'</(?P<close_tag>' + HTML_TAGNAME + r')|'  # close tag
        r'<!--|' # comment
        r'<\?|'  # script
        r'<![A-Z]|'
        r'<!\[CDATA\[)'
    )

    RULE_NAMES = (
        'blank_line',
        'fenced_code',
        'indent_code',
        'axt_heading',
        'setex_heading',
        'thematic_break',
        'block_quote',
        'list',
        'def_link',
        'block_html',
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
        cursor_next = state.add_to_paragraph(line, cursor)
        if cursor_next:
            return cursor_next

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
        info = line[len(spaces) + len(marker):]

        _c = marker[0]
        if _c == '`':
            # CommonMark Example 145
            # Info strings for backtick code blocks cannot contain backticks
            if info.find(_c) != -1:
                return

        info = ESCAPE_CHAR_RE.sub(r'\1', info)
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
            token['attrs'] = {'info': info.strip()}

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
        text = _AXT_HEADING_TRIM.sub('', text)

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
            m2 = _LINE_HAS_TEXT.match(line)
            if not m2:
                # no url at all
                return
            url, title_pos = _parse_def_link_url(m2.end() - 1, line)

        # step 2, parse title
        title, cursor = _parse_def_link_title(title_pos, line, cursor, state)
        if not cursor:
            return

        key = unikey(m.group(1)[1:-1])
        if key not in state.def_links:
            attrs = {'url': url}
            if title:
                attrs['title'] = title
            state.def_links[key] = attrs
        return cursor + 1

    def parse_block_quote(self, line, cursor, state):
        m = self.BLOCK_QUOTE.match(line)
        if not m:
            return

        start_line = cursor

        # cleanup at first to detect if it is code block
        text = m.group(2)
        text = expand_leading_tab(text, 3)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        require_marker = bool(
            self.BLANK_LINE.match(text)
            or self.INDENT_CODE.match(text)
            or self.FENCED_CODE.match(text)
        )

        prev_blank_line = False
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

            # fenced code brean block quote
            cursor_next = self.parse_fenced_code(line, cursor, state)
            if cursor_next:
                break

            cursor_next = self.parse_list(line, cursor, state)
            if cursor_next:
                break

            if _BLOCK_QUOTE_LEADING.match(line):
                line = _BLOCK_QUOTE_LEADING.sub('', line)
                line = expand_leading_tab(line, 3)
                line = _BLOCK_QUOTE_TRIM.sub('', line)
                prev_blank_line = bool(self.BLANK_LINE.match(line))
            elif prev_blank_line:
                # CommonMark Example 249
                # because of laziness, a blank line is needed between
                # a block quote and a following paragraph
                cursor = cursor - 1
                break
            else:
                # lazy continuation line
                line = expand_leading_tab(line, 3)
            text += '\n' + line

        # according to CommonMark Example 6, the second tab should be
        # treated as 4 spaces
        text = _EXPAND_TAB.sub(r'\1    ', text)

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

        marker = m1.group(2)
        ordered = len(marker) != 1

        attrs = {'ordered': ordered}
        if ordered:
            start = int(marker[:-1])
            if start != 1:
                # Example 304
                # we allow only lists starting with 1 to interrupt paragraphs
                cursor_next = state.add_to_paragraph(line, cursor)
                if cursor_next:
                    return cursor_next

                attrs['start'] = start

        bullet = _get_list_bullet(marker)
        current = []
        trim, next_re, continue_re = _prepare_list_patterns(current, m1, bullet)
        if not current:
            # Example 285
            # an empty list item cannot interrupt a paragraph
            cursor_next = state.add_to_paragraph(line, cursor)
            if cursor_next:
                return cursor_next

        start_line = cursor
        child_state = self.state_cls()
        child_state.parent = state
        child_state.in_block = 'list'
        child_state.cursor_root = start_line

        list_items = []
        prev_blank_line = False
        cursor_next = None
        while cursor < state.cursor_end:
            cursor += 1
            line = state.lines[cursor]

            # hr break at first
            cursor_next = self.parse_thematic_break(line, cursor, state)
            if cursor_next:
                break

            # this is a blank line, continue
            is_blank_line = bool(self.BLANK_LINE.match(line))
            if is_blank_line:
                prev_blank_line = True
                continue

            # expand tab for next_re and continue_re
            line = expand_leading_tab(line)

            # a new list item
            m1 = next_re.match(line)
            if m1:
                if prev_blank_line:
                    child_state.list_tight = False

                list_items.append(current)
                current = []  # reset, a new list item
                trim, next_re, continue_re = _prepare_list_patterns(current, m1, bullet)
                prev_blank_line = False
                continue

            # next line contains enough white space
            cm = continue_re.match(line)
            if cm:
                if prev_blank_line:
                    # Example 280
                    # A list item can begin with at most one blank line
                    if not current:
                        cursor = cursor - 1
                        break
                    current.append('')

                _process_continue_line(current, line, trim)
                prev_blank_line = False
                continue
            elif prev_blank_line:
                # not a continue line, and previous line is blank
                cursor = cursor - 2
                break

            # a new kind of list delemiter
            if self.LIST.match(line):
                cursor = cursor - 1
                break

            # lazy continue
            _process_continue_line(current, line, trim)

        # add the last list item into group
        list_items.append(current)

        depth = state.depth()
        if depth >= self.max_block_depth:
            rules = list(self.list_rules)
            rules.remove('list')
        else:
            rules = self.list_rules


        children = [
            self._parse_list_item(item, child_state, rules)
            for item in list_items
        ]

        attrs['depth'] = depth
        attrs['tight'] = child_state.list_tight
        token = {'type': 'list', 'children': children, 'attrs': attrs}
        if cursor_next:
            last_token = state.tokens.pop()
            state.add_token(token, start_line, cursor - 1)
            state.tokens.append(last_token)
            return cursor_next

        state.add_token(token, start_line, cursor)
        return cursor + 1

    def _parse_list_item(self, lines, state, rules):
        state.tokens = []
        state.lines = lines
        state.cursor_end = len(lines) - 1

        self.parse(state.cursor_start, state, rules)
        if state.list_tight and _is_loose_list(state.tokens):
            state.list_tight = False

        # reset cursor root for counting
        state.cursor_root += len(lines)
        return {'type': 'list_item', 'children': state.tokens}

    def parse_block_html(self, line, cursor, state):
        m = self.BLOCK_HTML.match(line)
        if not m:
            return

        start_cursor = cursor
        open_tag = m.group('open_tag')
        close_tag = m.group('close_tag')

        # rule 1
        if open_tag in ('pre', 'script', 'style', 'textarea'):
            end_tag = '</' + open_tag + '>'
            return _parse_html_to_end(end_tag, line, cursor, state)

        # rule 6
        if open_tag in _BLOCK_TAGS or close_tag in _BLOCK_TAGS:
            text = line
            while cursor < state.cursor_end:
                cursor += 1
                line = state.lines[cursor]
                if self.BLANK_LINE.match(line):
                    break
                text += '\n' + line
            state.add_token({'type': 'block_html', 'raw': text}, start_cursor, cursor)
            return cursor + 1

        spaces = m.group(1)
        # rule 2
        if line.startswith(spaces + '<!--'):
            return _parse_html_to_end('-->', line, cursor, state)

        # rule 3
        if line.startswith(spaces + '<?'):
            return _parse_html_to_end('?>', line, cursor, state)

        # rule 5
        if line.startswith(spaces + '<![CDATA['):
            return _parse_html_to_end(']]>', line, cursor, state)

        # rule 4
        if line.startswith(spaces + '<!'):
            return _parse_html_to_end('>', line, cursor, state)

        # Blocks of type 7 may not interrupt a paragraph.
        cursor_next = state.add_to_paragraph(line, cursor)
        if cursor_next:
            return cursor_next

        # rule 7
        if open_tag:
            pos = m.end()
            if _OPEN_TAG_END.match(line, pos):
                return _parse_html_to_newline(line, cursor, state)
        elif close_tag:
            pos = m.end()
            if _CLOSE_TAG_END.match(line, pos):
                return _parse_html_to_newline(line, cursor, state)

    def parse_paragraph(self, line, cursor, state):
        cursor_next = state.add_to_paragraph(line, cursor)
        if cursor_next:
            return cursor_next
        state.add_token({'type': 'paragraph', 'text': line}, cursor, cursor)
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

    def _call_render(self, tokens, state, inline, is_tight=False):
        data = self._iter_render(tokens, state, inline, is_tight)
        if inline.renderer:
            return inline.renderer(data)
        return list(data)

    def _iter_render(self, tokens, state, inline, is_tight):
        for tok in tokens:
            if 'children' in tok:
                children = tok['children']
                if tok['type'] == 'list':
                    _tight = tok['attrs']['tight']
                    children = self._call_render(children, state, inline, _tight)
                elif tok['type'] == 'list_item':
                    children = self._call_render(children, state, inline, is_tight)
                else:
                    children = self._call_render(children, state, inline)
                tok['children'] = children
            elif 'text' in tok:
                text = tok.pop('text')
                children = inline(text.strip(), state)
                tok['children'] = children
                if is_tight and tok['type'] == 'paragraph':
                    tok['type'] = 'block_text'
            yield tok


def expand_leading_tab(text, width=4):
    def _expand_tab_repl(m):
        s = m.group(1)
        return s + ' ' * (width - len(s))
    return _EXPAND_TAB.sub(_expand_tab_repl, text)


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
    if line.startswith(trim):
        line = line.replace(trim, '', 1)
        # according to CommonMark Example 5
        # tab should be treated as 4 spaces
        line = _EXPAND_TAB.sub(r'\1    ', line)
        current.append(line)
    else:
        current.append(line)


def _prepare_list_patterns(current, m1, bullet):
    # according to Example 7, tab should be treated as 3 spaces
    text = expand_leading_tab(m1.group(3), 3)
    text = _EXPAND_TAB.sub(r'\1    ', text)

    m2 = _LINE_HAS_TEXT.match(text)
    if m2:
        # indent code, startswith 5 spaces
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
    continue_width = leading_width + space_width

    if leading_width > 3:
        leading_width = 3

    # check if line is new list item
    next_re = re.compile(
        r'( {0,' + str(leading_width) + '})'
        r'(' + bullet + ')'
        r'([ \t]*|[ \t].+)$'
    )

    trim = ' ' * continue_width
    continue_re = re.compile(trim + r'\s*\S')
    return trim, next_re, continue_re


def _is_loose_list(tokens):
    for tok in tokens:
        if tok['type'] == 'blank_line':
            return True
    return False


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
    if _LINE_HAS_TEXT.match(line, pos):
        m = _DEF_LINK_TITLE_START.match(line)
        if not m:
            # case 1: [ref]: /url non-title
            return None, None

        title, cursor_next = _parse_def_link_continue_title(m, line, cursor, state)
        if title:
            # case 2: [ref] /url "title"
            # case 3: with multiple lines title
            return title, cursor_next
        return None, None

    # case 4: end of line, no title
    if cursor >= state.cursor_end:
        return None, cursor

    # case 5: title is in next line
    cursor += 1
    line = state.lines[cursor]
    m = _DEF_LINK_TITLE_START.match(line)
    if not m:
        # next line is not title, but def link has url
        return None, cursor - 1

    title, cursor_next = _parse_def_link_continue_title(m, line, cursor, state)
    if title:
        return title, cursor_next
    return None, cursor - 1


def _parse_def_link_continue_title(m, line, cursor, state):
    pos = m.end()
    marker = m.group(1)
    end_pattern = re.compile(re.escape(marker) + r'\s*$')

    m2 = end_pattern.search(line, pos)
    # title finished in one line
    if m2:
        title = line[pos:m2.start()]
        return title, cursor

    # title has multiple lines
    title = line[pos:]
    while cursor < state.cursor_end:
        cursor += 1
        line = state.lines[cursor]
        if _BREAK_PATTERN.match(line):
            return None, None

        m3 = end_pattern.search(line)
        if m3:
            title += '\n' + line[:m3.start()]
            return title, cursor
        rv += '\n' + line
    return None, None


def _parse_html_to_end(end, line, cursor, state):
    start = cursor
    text = line
    while end not in line and cursor < state.cursor_end:
        cursor += 1
        line = state.lines[cursor]
        text += '\n' + line

    state.add_token({'type': 'block_html', 'raw': text}, start, cursor)
    return cursor + 1


def _parse_html_to_newline(line, cursor, state):
    start = cursor
    text = line
    while cursor < state.cursor_end:
        cursor += 1
        line = state.lines[cursor]
        if BlockParser.BLANK_LINE.match(line):
            break
        text += '\n' + line
    state.add_token({'type': 'block_html', 'raw': text}, start, cursor)
    return cursor + 1
