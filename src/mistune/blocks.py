import re
from .scanner import ScannerParser, Matcher

LINE_BREAK = re.compile(r'\n{2,}')
BLOCK_QUOTE_LEADING = re.compile(r'^ *> ?', flags=re.M)
_END = r'(?:\n+|$)'


class BlockParser(ScannerParser):
    scanner_cls = Matcher

    DEF_LINK = re.compile(
        r'^ *\[([^^\]]+)\]: *'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'
    )
    DEF_FOOTNOTE = re.compile(
        r'^\[\^([^\]]+)\]: *('
        r'[^\n]*(?:\n+|$)'  # [^key]:
        r'(?: {1,}[^\n]*(?:\n+|$))*'
        r')'
    )

    AXT_HEADING = re.compile(
        r' {0,3}(#{1,6})(?:' + _END + r'|'
        r'\s*(.*?)(?:' + _END + r'|\s+?#+\s*' + _END + r'))'
    )
    SETEX_HEADING = re.compile(r'([^\n]+)\n *(=|-){2,} *' + _END)
    THEMATIC_BREAK = re.compile(
        r' {0,3}((?:- *){3,}|'
        r'(?:_ *){3,}|(?:\* *){3,})' + _END
    )

    INDENT_CODE = re.compile(r'(?: {4}[^\n]+\n*)+')
    FENCED_CODE = re.compile(
        r' {0,3}(`{3,}|~{3,})([^`\n]*)\n'
        r'(?:|([\s\S]*?)\n)'
        r'(?: {0,3}\1[~`]* *(?:\n+|$)|$)'
    )
    BLOCK_QUOTE = re.compile(r'( {0,3}>[^\n]+(\n[^\n]+)*\n*)+')

    RULE_NAMES = (
        'indent_code', 'fenced_code',
        'axt_heading', 'setex_heading',
        'thematic_break', 'block_quote',
        'def_link', 'def_footnote',
    )

    # list
    # block html

    def parse_indent_code(self, m):
        # TODO: clean leading spaces
        code = m.group(0)
        return {'type': 'block_code', 'text': code}

    def parse_fenced_code(self, m, state):
        lang = m.group(2)
        code = m.group(3)
        token = {'type': 'block_code', 'text': code}
        if lang:
            token['params'] = (lang, )
        return token

    def parse_axt_heading(self, m, state):
        level = len(m.group(1))
        text = m.group(2)
        return {'type': 'heading', 'text': text, 'params': (level,)}

    def parse_setex_heading(self, m, state):
        level = 1 if m.group(2) == '=' else 2
        text = m.group(1)
        return {'type': 'heading', 'text': text, 'params': (level,)}

    def parse_thematic_break(self, m, state):
        return {'type': 'thematic_break'}

    def parse_block_quote(self, m, state):
        depth = state.get('in_block_quote', 0) + 1
        if depth > 5:
            rules = list(self.default_rules)
            rules.remove('block_quote')
        else:
            rules = None

        state['in_block_quote'] = depth
        text = BLOCK_QUOTE_LEADING.sub('', m.group(0))
        children = self.parse(text, state, rules)
        state['in_block_quote'] = depth - 1
        return {'type': 'block_quote', 'children': children}

    def parse_def_link(self, m, state):
        key = m.group(1).lower()
        link = m.group(2)
        title = m.group(3)
        if key not in state['def_links']:
            state['def_links'][key] = (link, title)

    def parse_def_footnotes(self, m, state):
        key = m.group(1).lower()
        if key not in state['def_footnotes']:
            state['def_footnotes'][key] = m.group(2)

    def parse_footnote_item(self, text):
        if '\n' not in text:
            children = [{'type': 'paragraph', 'text': text}]
        else:
            # TODO: parse again
            children = [{'type': 'paragraph', 'text': text}]
        return {'type': 'footnote_item', 'children': children}

    def parse_text(self, text, state):
        if state.get('tight') is True:
            return {'type': 'text', 'text': text.strip()}

        tokens = []
        for p in LINE_BREAK.split(text):
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
            if 'children' not in tok and 'text' not in tok:
                yield method()
                return

            if 'children' in tok:
                children = self.render(tok['children'], inline, state)
            else:
                children = inline(tok['text'], state)
            params = tok.get('params')
            if params:
                yield method(children, *params)
            else:
                yield method(children)
