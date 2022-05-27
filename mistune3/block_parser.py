import re
from .util import (
    unikey,
    escape,
    escape_url,
    safe_entity,
)
from .state import BlockState
from .helpers import (
    LINK_LABEL,
    HTML_TAGNAME,
    HTML_ATTRIBUTES,
    BLOCK_TAGS,
    PRE_TAGS,
    ESCAPE_CHAR_RE,
    EXPAND_TAB_RE,
    expand_leading_tab,
    parse_link_href,
    parse_link_title,
)

_INDENT_CODE_TRIM = re.compile(r'^ {1,4}', flags=re.M)
_AXT_HEADING_TRIM = re.compile(r'(\s+|^)#+\s*$')
_BLOCK_QUOTE_TRIM = re.compile(r'^ {0,1}', flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r'^ *>', flags=re.M)

_LINE_BLANK_END = re.compile(r'\n[ \t]*\n$')
_LINE_HAS_TEXT = re.compile(r'( *)\S')
_BLANK_TO_LINE = re.compile(r'[ \t]*\n')

_BLOCK_HTML_BREAK = re.compile(
    r' {0,3}(?:'
    r'(?:</?' + '|'.join(BLOCK_TAGS) + '|' + '|'.join(PRE_TAGS) + r'(?:[ \t]+|\n|$))'
    r'|<!--' # comment
    r'|<\?'  # script
    r'|<![A-Z]'
    r'|<!\[CDATA\[)'
)
_OPEN_TAG_END = re.compile(HTML_ATTRIBUTES + r'[ \t]*>[ \t]*(?:\n|$)')
_CLOSE_TAG_END = re.compile(r'[ \t]*>[ \t]*(?:\n|$)')



class BlockParser:
    state_cls = BlockState

    BLANK_LINE = re.compile(r'(^[ \t]*\n)+', re.M)
    AXT_HEADING = re.compile(r' {0,3}(#{1,6})(?!#+)([ \t]*|[ \t]+.*?)(?:\n|$)')
    SETEX_HEADING = re.compile(r' {0,3}(=|-){1,}[ \t]*(?:\n|$)')
    THEMATIC_BREAK = re.compile(
        r' {0,3}((?:-[ \t]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n|$)'
    )

    INDENT_CODE = re.compile(
        r'(?: {4}| *\t)[^\n]+(?:\n+|$)'
        r'((?:(?: {4}| *\t)[^\n]+(?:\n+|$))|\s)*'
    )
    FENCED_CODE = re.compile(r'( {0,3})(`{3,}|~{3,})[ \t]*(.*?)(?:\n|$)')

    BLOCK_QUOTE = re.compile(r' {0,3}>(.*?(?:\n|$))')
    STRICT_BLOCK_QUOTE = re.compile(r'( {0,3}>[^\n]*(?:\n|$))+')

    LIST = re.compile(r'( {0,3})([\*\+-]|\d{1,9}[.)])([ \t]*|[ \t].+)(?:\n|$)')

    REF_LINK = re.compile(r' {0,3}\[(' + LINK_LABEL + r')\]:')

    BLOCK_HTML = re.compile(
        r' {0,3}('
        r'</?' + HTML_TAGNAME + r'|'
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
        'ref_link',
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

    def register_rule(self, name, func, before=None):
        self.__methods[name] = lambda state: func(self, state)
        if before:
            index = self.rules.index(before)
            self.rules.insert(index, name)
        else:
            self.rules.append(name)

    def parse_blank_line(self, state):
        m = state.match(self.BLANK_LINE)
        if m:
            line_count = m.group(0).count('\n')
            state.add_token({'type': 'blank_line'}, line_count)
            state.cursor = m.end()
            return True

    def parse_thematic_break(self, state):
        m = state.match(self.THEMATIC_BREAK)
        if m:
            state.add_token({'type': 'thematic_break'}, 1)
            state.cursor = m.end()
            return True

    def parse_indent_code(self, state):
        m = state.match(self.INDENT_CODE)
        if not m:
            return

        # it is a part of the paragraph
        if state.append_paragraph():
            return True

        code = m.group(0)
        code = expand_leading_tab(code)
        code = _INDENT_CODE_TRIM.sub('', code)
        line_count = code.count('\n')
        code = escape(code.strip('\n'))
        state.add_token({'type': 'block_code', 'raw': code}, line_count)
        state.cursor = m.end()
        return True

    def parse_fenced_code(self, state):
        m = state.match(self.FENCED_CODE)
        if not m:
            return

        spaces = m.group(1)
        marker = m.group(2)
        info = m.group(3)

        c = marker[0]
        if info and c == '`':
            # CommonMark Example 145
            # Info strings for backtick code blocks cannot contain backticks
            if info.find(c) != -1:
                return

        _end = re.compile(
            r'^ {0,3}' + c + '{' + str(len(marker)) + r',}[ \t]*(?:\n|$)', re.M)
        cursor_start = m.end()

        m2 = _end.search(state.src, cursor_start)
        if m2:
            code = state.src[cursor_start:m2.start()]
            line_count = code.count('\n') + 2
            state.cursor = m2.end()
        else:
            code = state.src[cursor_start:]
            line_count = code.count('\n') + 1
            state.cursor = state.cursor_max

        if spaces and code:
            _trim_pattern = re.compile('^ {0,' + str(len(spaces)) + '}', re.M)
            code = _trim_pattern.sub('', code)

        token = {'type': 'block_code', 'raw': escape(code), 'fenced': True}
        if info:
            info = ESCAPE_CHAR_RE.sub(r'\1', info)
            token['attrs'] = {'info': safe_entity(info.strip())}

        state.add_token(token, line_count)
        return True

    def parse_axt_heading(self, state):
        m = state.match(self.AXT_HEADING)
        if not m:
            return

        level = len(m.group(1))
        text = m.group(2).strip()

        # remove last #
        if text:
            text = _AXT_HEADING_TRIM.sub('', text)

        token = {'type': 'heading', 'text': text, 'attrs': {'level': level}}
        state.add_token(token, 1)
        state.cursor = m.end()
        return True

    def parse_setex_heading(self, state):
        prev_token = state.prev_token()
        if prev_token and prev_token['type'] == 'paragraph':
            m = state.match(self.SETEX_HEADING)
            if m:
                level = 1 if m.group(1) == '=' else 2
                prev_token['type'] = 'heading'
                prev_token['attrs'] = {'level': level}
                prev_token['end_line'] += 1
                state.cursor = m.end()
                state.line += 1
                return True

    def parse_ref_link(self, state):
        m = state.match(self.REF_LINK)
        if not m:
            return

        if state.append_paragraph():
            return True

        key = unikey(m.group(1))
        if not key:
            return

        href, href_pos = parse_link_href(state.src, m.end(), block=True)
        if href is None:
            return

        _blank = self.BLANK_LINE.search(state.src, href_pos)
        if _blank:
            max_pos = _blank.start()
        else:
            max_pos = state.cursor_max

        title, title_pos = parse_link_title(state.src, href_pos, max_pos)
        next_pos = title_pos or href_pos
        m = _BLANK_TO_LINE.match(state.src, next_pos)
        if not m:
            return

        end_pos = m.end()
        text = state.get_text(end_pos)
        state.cursor = end_pos
        state.line += text.count('\n')

        if key not in state.env['ref_links']:
            attrs = {'url': escape_url(href)}
            if title:
                attrs['title'] = safe_entity(title)
            state.env['ref_links'][key] = attrs
        return True

    def parse_block_quote(self, state):
        m = state.match(self.BLOCK_QUOTE)
        if not m:
            return

        start_line = state.line

        # cleanup at first to detect if it is code block
        text = m.group(1)
        text = expand_leading_tab(text, 3)
        text = _BLOCK_QUOTE_TRIM.sub('', text)

        require_marker = bool(
            self.BLANK_LINE.match(text)
            or self.INDENT_CODE.match(text)
            or self.FENCED_CODE.match(text)
        )

        cursor = m.end()
        state.cursor = cursor
        state.line += 1

        if require_marker:
            m = state.match(self.STRICT_BLOCK_QUOTE)
            if m:
                quote = m.group(0)
                quote = _BLOCK_QUOTE_LEADING.sub('', quote)
                quote = expand_leading_tab(quote, 3)
                quote = _BLOCK_QUOTE_TRIM.sub('', quote)
                text += quote
                state.cursor = m.end()
        else:
            prev_blank_line = False
            while state.cursor < state.cursor_max:
                m = state.match(self.STRICT_BLOCK_QUOTE)
                if m:
                    quote = m.group(0)
                    quote = _BLOCK_QUOTE_LEADING.sub('', quote)
                    quote = expand_leading_tab(quote, 3)
                    quote = _BLOCK_QUOTE_TRIM.sub('', quote)
                    text += quote
                    state.cursor = m.end()
                    state.line += quote.count('\n')

                    if not quote.strip():
                        prev_blank_line = True
                    else:
                        prev_blank_line = bool(_LINE_BLANK_END.search(quote))
                    continue

                if prev_blank_line:
                    # CommonMark Example 249
                    # because of laziness, a blank line is needed between
                    # a block quote and a following paragraph
                    break

                # blank line break block quote
                if self.parse_blank_line(state):
                    break

                # hr break block quote
                if self.parse_thematic_break(state):
                    break

                # fenced code break block quote
                if self.parse_fenced_code(state):
                    break

                # list break block quote
                if self.parse_list(state):
                    break

                # block html break block quote (except rule 7)
                if state.match(_BLOCK_HTML_BREAK):
                    self.parse_block_html(state)
                    break

                # lazy continuation line
                line = state.get_line()
                line = expand_leading_tab(line, 3)
                text += line
                state.line += 1

        # according to CommonMark Example 6, the second tab should be
        # treated as 4 spaces
        text = EXPAND_TAB_RE.sub(r'\1    ', text)
        line_count = text.count('\n')

        # scan children state
        child = self.state_cls(state)
        child.line_root = start_line
        child.in_block = 'block_quote'
        child.process(text)

        if state.depth() >= self.max_block_depth:
            rules = list(self.block_quote_rules)
            rules.remove('block_quote')
        else:
            rules = self.block_quote_rules

        self.parse(child, rules)
        token = {'type': 'block_quote', 'children': child.tokens}
        state.add_token(token, line_count, start_line)
        return True

    def parse_list(self, state):
        m = state.match(self.LIST)
        if not m:
            return

        text = m.group(3)
        if not text.strip():
            # Example 285
            # an empty list item cannot interrupt a paragraph
            if state.append_paragraph():
                return True

        marker = m.group(2)
        ordered = len(marker) > 1
        attrs = {'ordered': ordered}
        if ordered:
            start = int(marker[:-1])
            if start != 1:
                # Example 304
                # we allow only lists starting with 1 to interrupt paragraphs
                if state.append_paragraph():
                    return True
                attrs['start'] = start

        depth = state.depth()
        if depth >= self.max_block_depth:
            rules = list(self.list_rules)
            rules.remove('list')
        else:
            rules = self.list_rules

        start_line = state.line
        children = []
        list_match = m
        while list_match:
            list_match = self._parse_list_item(state, list_match, children, rules)

        end_line = children[-1]['end_line']
        line_count = end_line - start_line - state.line_root

        attrs['depth'] = depth
        attrs['tight'] = state.list_tight
        token = {
            'type': 'list',
            'children': children,
            'attrs': attrs,
        }
        state.add_token(token, line_count, start_line)
        return True

    def _parse_list_item(self, parent_state, match, children, rules):
        has_next = False
        line_root = parent_state.line
        start_line = line_root + parent_state.line_root

        space_width = len(match.group(1))
        marker = match.group(2)
        leading_width = space_width + len(marker)

        bullet = _get_list_bullet(marker[-1])
        item_pattern = _compile_list_item_pattern(bullet, leading_width)

        pairs = [
            ('thematic_break', self.THEMATIC_BREAK.pattern),
            ('fenced_code', self.FENCED_CODE.pattern),
            ('axt_heading', self.AXT_HEADING.pattern),
            ('block_quote', self.BLOCK_QUOTE.pattern),
            ('block_html', _BLOCK_HTML_BREAK.pattern),
            ('list', self.LIST.pattern),
            ('break', r'[ \t]*\n {0,3}(?!' + bullet + r')\S'),
        ]
        if leading_width < 3:
            _repl_w = str(leading_width)
            pairs = [(n, p.replace('3', _repl_w, 1)) for n, p in pairs]

        pairs.insert(1, ('list_item', item_pattern))
        # ('continue', r'')

        sc = re.compile('|'.join(r'(?P<%s>(?<=\n)%s)' % pair for pair in pairs))
        m = sc.search(parent_state.src, match.end())
        if m:
            tok_type = m.lastgroup
            cursor = m.start()
            src = parent_state.src[match.end():cursor]
            line_count = src.count('\n') + 1
            parent_state.line += line_count
            parent_state.cursor = cursor
            if tok_type == 'list_item':
                has_next = True
            elif tok_type != 'break':
                func = getattr(self, 'parse_' + tok_type)
                func(parent_state)
        else:
            src = parent_state.src[match.end():]
            line_count = src.count('\n') + 1
            parent_state.line += line_count
            parent_state.cursor = parent_state.cursor_max

        state = self.state_cls(parent_state)
        state.line_root = line_root
        text = _clean_list_item_text(src, match)
        state.process(text)

        self.parse(state, rules)
        if parent_state.list_tight:
            if any((tok['type'] == 'blank_line' for tok in state.tokens)):
                parent_state.list_tight = False

        children.append({
            'type': 'list_item',
            'start_line':start_line,
            'end_line': start_line + line_count,
            'children': state.tokens,
        })
        if has_next:
            pattern = re.compile(item_pattern)
            return parent_state.match(pattern)

    def parse_block_html(self, state):
        m = state.match(self.BLOCK_HTML)
        if not m:
            return

        marker = m.group(1)

        # rule 2
        if marker == '<!--':
            return _parse_html_to_end(state, '-->', m.end())

        # rule 3
        if marker == '<?':
            return _parse_html_to_end(state, '?>', m.end())

        # rule 4
        if marker == '<!':
            return _parse_html_to_end(state, '>', m.end())

        # rule 5
        if marker == '<![CDATA[':
            return _parse_html_to_end(state, ']]>', m.end())

        close_tag = None
        open_tag = None
        if marker.startswith('</'):
            close_tag = marker[2:]
            # rule 6
            if close_tag in BLOCK_TAGS:
                return _parse_html_to_newline(state, self.BLANK_LINE)
        else:
            open_tag = marker[1:]
            # rule 1
            if open_tag in PRE_TAGS:
                end_tag = '</' + open_tag + '>'
                return _parse_html_to_end(state, end_tag, m.end())
            # rule 6
            if open_tag in BLOCK_TAGS:
                return _parse_html_to_newline(state, self.BLANK_LINE)

        # Blocks of type 7 may not interrupt a paragraph.
        if state.append_paragraph():
            return True

        # rule 7
        if open_tag:
            if _OPEN_TAG_END.match(state.src, m.end()):
                return _parse_html_to_newline(state, self.BLANK_LINE)
        elif close_tag:
            if _CLOSE_TAG_END.match(state.src, m.end()):
                return _parse_html_to_newline(state, self.BLANK_LINE)

    def parse_paragraph(self, state):
        if not state.append_paragraph():
            line = state.get_line()
            state.add_token({'type': 'paragraph', 'text': line}, 1)
        return True

    def postprocess_paragraph(self, token, is_tight):
        """A method to post process paragraph token. Developers CAN
        subclass BlockParser and rewrite this method to update the
        common paragraph token."""
        if is_tight:
            token['type'] = 'block_text'

    def parse(self, state, rules):
        while state.cursor < state.cursor_max:
            self._scan_rules(state, rules)

    def render(self, state, inline):
        return self._call_render(state.tokens, state, inline)

    def _scan_rules(self, state, rules):
        for name in rules:
            func = self.__methods[name]
            if func(state):
                return
        self.parse_paragraph(state)

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
                children = inline(text.strip(), state.env)
                tok['children'] = children
                if tok['type'] == 'paragraph':
                    self.postprocess_paragraph(tok, is_tight)
            yield tok


def _get_list_bullet(c):
    if c == '.':
        bullet = r'\d{0,9}\.'
    elif c == ')':
        bullet = r'\d{0,9}\)'
    elif c == '*':
        bullet = r'\*'
    elif c == '+':
        bullet = r'\+'
    else:
        bullet = '-'
    return bullet


def _compile_list_item_pattern(bullet, leading_width):
    if leading_width > 3:
        leading_width = 3
    return (
        r'( {0,' + str(leading_width) + '})'
        r'(' + bullet + ')'
        r'([ \t]*|[ \t][^\n]+)(?:\n|$)'
    )


def _clean_list_item_text(src, m):
    # according to Example 7, tab should be treated as 3 spaces
    text = expand_leading_tab(m.group(3), 3)
    text = EXPAND_TAB_RE.sub(r'\1    ', text)
    rv = []

    m2 = _LINE_HAS_TEXT.match(text)
    if m2:
        # indent code, startswith 5 spaces
        if text.startswith('     '):
            space_width = 1
        else:
            space_width = len(m2.group(1))

        rv.append(text[space_width:])
    else:
        space_width = 1
        rv.append('')

    continue_width = len(m.group(1)) + len(m.group(2)) + space_width
    trim_space = ' ' * continue_width
    lines = src.split('\n')
    for line in lines:
        if line.startswith(trim_space):
            line = line.replace(trim_space, '', 1)
            # according to CommonMark Example 5
            # tab should be treated as 4 spaces
            line = EXPAND_TAB_RE.sub(r'\1    ', line)
            rv.append(line)
        else:
            rv.append(line)
    return '\n'.join(rv)


def _parse_html_to_end(state, end_marker, start_pos):
    marker_pos = state.src.find(end_marker, start_pos)
    if marker_pos == -1:
        text = state.src[state.cursor:]
        state.cursor = state.cursor_max
    else:
        text = state.get_text(marker_pos)
        state.cursor = marker_pos
        text += state.get_line()

    line_count = text.count('\n')
    state.add_token({'type': 'block_html', 'raw': text}, line_count)
    return True


def _parse_html_to_newline(state, newline):
    m = newline.search(state.src, state.cursor)
    if m:
        end_pos = m.start()
        text = state.get_text(end_pos)
        state.cursor = end_pos
    else:
        text = state.src[state.cursor:]
        state.cursor = state.cursor_max

    line_count = text.count('\n')
    state.add_token({'type': 'block_html', 'raw': text}, line_count)
    return True
