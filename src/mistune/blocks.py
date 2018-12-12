from .scanner import ScannerParser


class BlockParser(ScannerParser):
    AXT_HEADING = r'(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)'
    FENCED_CODE = (
        r' {0,3}(`{3,}|~{3,}) *([^`\s]+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )

    def __init__(self):
        super(BlockParser, self).__init__()
        self.rules = {
            'axt_heading': (self.AXT_HEADING, self.parse_axt_heading),
            'fenced_code': (self.FENCED_CODE, self.parse_fenced_code),
        }
        self.default_rules = (
            'axt_heading',
            'fenced_code',
        )

    def parse_axt_heading(self, m, state):
        level = len(m.group(1))
        text = m.group(2)
        return {'type': 'heading', 'level': level, 'text': text}

    def parse_fenced_code(self, m, state):
        lang = m.group(2).strip()
        text = m.group(3)
        return {'type': 'block_code', 'code': text, 'language': lang}

    def parse_text(self, text):
        return {'type': 'block_text', 'text': text}

    def parse(self, s, state=None, rules=None):
        if rules is None:
            rules = self.default_rules
        if state is None:
            state = {}
        return list(self._scan(s, state, rules))
