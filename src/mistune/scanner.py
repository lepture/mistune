import re


class Scanner(re.Scanner):
    def iter(self, string):
        sc = self.scanner.scanner(string)

        pos = 0
        for match in iter(sc.search, None):
            name = self.lexicon[match.lastindex - 1][1]
            hole = string[pos:match.start()]
            if hole:
                yield '_text_', hole

            yield name, match
            pos = match.end()

        hole = string[pos:]
        if hole:
            yield '_text_', hole


class Matcher(object):
    NEWLINE = re.compile(r'\n+')

    def __init__(self, lexicon):
        self.lexicon = lexicon

    def iter(self, string):
        pos = 0
        endpos = len(string)
        last_end = 0
        while 1:
            if pos >= endpos:
                break
            for rule, name in self.lexicon:
                match = rule.match(string, pos)
                if match is not None:
                    start, end = match.span()
                    if start > last_end:
                        yield '_text_', string[last_end:start]
                    yield name, match
                    last_end = pos = match.end()
                    break
            else:
                m = self.NEWLINE.search(string, pos)
                if not m:
                    break
                pos = m.end()

        if last_end < endpos:
            yield '_text_', string[last_end:]


class ScannerParser(object):
    scanner_cls = Scanner
    RULE_NAMES = tuple()

    def __init__(self):
        self.rules = {}
        self.default_rules = list(self.RULE_NAMES)
        self._cached_sc = {}

    def register_rule(self, name, pattern, method):
        self.rules[name] = (pattern, lambda m, state: method(self, m, state))

    def get_rule_pattern(self, name):
        if name not in self.RULE_NAMES:
            return self.rules[name][0]
        return getattr(self, name.upper())

    def get_rule_method(self, name):
        if name not in self.RULE_NAMES:
            return self.rules[name][1]
        return getattr(self, 'parse_' + name)

    def parse_text(self, text, state):
        raise NotImplementedError

    def _scan(self, s, state, rules):
        sc = self._create_scanner(rules)
        for name, m in sc.iter(s):
            if name == '_text_':
                yield self.parse_text(m, state)
            else:
                method = self.get_rule_method(name)
                yield method(m, state)

    def _create_scanner(self, rules):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        lexicon = [(self.get_rule_pattern(n), n) for n in rules]
        sc = self.scanner_cls(lexicon)
        self._cached_sc[sc_key] = sc
        return sc
