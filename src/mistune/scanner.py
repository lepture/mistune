from re import Scanner as _Scanner


class Scanner(_Scanner):
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


class ScannerParser(object):
    def __init__(self):
        self.rules = {}
        self._cached_sc = {}

    def register_rule(self, name, pattern, method):
        self.rules[name] = (pattern, lambda m, state: method(self, m, state))

    def parse(self, s, state=None, rules=None):
        raise NotImplementedError

    def parse_text(self, text):
        raise NotImplementedError

    def _scan(self, s, state, rules):
        sc = self._create_scanner(rules)
        for name, m in sc.iter(s):
            if name == '_text_':
                yield self.parse_text(m)
            else:
                method = self.rules.get(name)[1]
                yield method(m, state)

    def _create_scanner(self, rules):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        lexicon = [(self.rules[n][0], n) for n in rules]
        sc = Scanner(lexicon)
        self._cached_sc[sc_key] = sc
        return sc

    def __call__(self, s, state=None):
        return self.parse(s, state)
