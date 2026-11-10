import re

class Scanner(re.Scanner):
    def __init__(self, lexicon, flags=0):
        self._patterns = None
        try:
            re.Scanner.__init__(self, lexicon, flags)
        except ValueError as exc:
            if str(exc) != 'Cannot use capturing groups in re.Scanner':
                raise
            # New Python versions reject captures in re.Scanner. Compile
            # rules independently so local groups and backreferences survive.
            self.lexicon = lexicon
            # re.Scanner does not enable Unicode character classes by default.
            if not flags & re.UNICODE:
                flags |= re.ASCII
            self._patterns = [re.compile(phrase, flags) for phrase, _ in lexicon]

    def _iter_patterns(self, string):
        scanners = [pattern.scanner(string) for pattern in self._patterns]
        matches = [scanner.search() for scanner in scanners]
        pos = 0
        empty_at = None
        while True:
            for index, match in enumerate(matches):
                if match is not None and match.start() < pos:
                    # A consumed token can overlap a candidate. Restart at
                    # its end rather than dropping a later overlapping match.
                    scanners[index] = self._patterns[index].scanner(string, pos)
                    match = scanners[index].search()
                while match is not None and match.start() == match.end() == empty_at:
                    match = scanners[index].search()
                matches[index] = match
            candidates = [(match.start(), index) for index, match in enumerate(matches)
                          if match is not None]
            if not candidates:
                return
            _, index = min(candidates)
            match = matches[index]
            yield index, match
            pos = match.end()
            empty_at = pos if match.start() == pos else None
            matches[index] = scanners[index].search()

    def scan(self, string):
        if self._patterns is None:
            return re.Scanner.scan(self, string)
        result = []
        pos = 0
        for index, match in self._iter_patterns(string):
            if match.start() != pos or match.end() == pos:
                break
            action = self.lexicon[index][1]
            if callable(action):
                self.match = match
                action = action(self, match.group())
            if action is not None:
                result.append(action)
            pos = match.end()
        return result, string[pos:]

    def iter(self, string, state, parse_text):
        if self._patterns is None:
            sc = self.scanner.scanner(string)
            matches = ((match.lastindex - 1, match) for match in iter(sc.search, None))
        else:
            matches = self._iter_patterns(string)

        pos = 0
        for index, match in matches:
            name, method = self.lexicon[index][1]
            hole = string[pos:match.start()]
            if hole:
                yield parse_text(hole, state)

            yield method(match, state)
            pos = match.end()

        hole = string[pos:]
        if hole:
            yield parse_text(hole, state)


class ScannerParser(object):
    scanner_cls = Scanner
    RULE_NAMES = tuple()

    def __init__(self):
        self.rules = list(self.RULE_NAMES)
        self.rule_methods = {}
        self._cached_sc = {}

    def register_rule(self, name, pattern, method):
        self.rule_methods[name] = (pattern, lambda m, state: method(self, m, state))

    def get_rule_pattern(self, name):
        if name not in self.RULE_NAMES:
            return self.rule_methods[name][0]
        return getattr(self, name.upper())

    def get_rule_method(self, name):
        if name not in self.RULE_NAMES:
            return self.rule_methods[name][1]
        return getattr(self, 'parse_' + name)

    def parse_text(self, text, state):
        raise NotImplementedError

    def _scan(self, s, state, rules):
        sc = self._create_scanner(rules)
        for tok in sc.iter(s, state, self.parse_text):
            if isinstance(tok, list):
                for t in tok:
                    yield t
            elif tok:
                yield tok

    def _create_scanner(self, rules):
        sc_key = '|'.join(rules)
        sc = self._cached_sc.get(sc_key)
        if sc:
            return sc

        lexicon = [
            (self.get_rule_pattern(n), (n, self.get_rule_method(n)))
            for n in rules
        ]
        sc = self.scanner_cls(lexicon)
        self._cached_sc[sc_key] = sc
        return sc


class Matcher(object):
    PARAGRAPH_END = re.compile(
        r'(?:\n{2,})|'
        r'(?:\n {0,3}#{1,6})|'  # axt heading
        r'(?:\n {0,3}(?:`{3,}|~{3,}))|'  # fenced code
        r'(?:\n {0,3}>)|'  # blockquote
        r'(?:\n {0,3}(?:[\*\+-]|1[.)]))|'  # list
        r'(?:\n {0,3}<)'  # block html
    )

    def __init__(self, lexicon):
        self.lexicon = lexicon

    def search_pos(self, string, pos):
        m = self.PARAGRAPH_END.search(string, pos)
        if not m:
            return None
        if set(m.group(0)) == {'\n'}:
            return m.end()
        return m.start() + 1

    def iter(self, string, state, parse_text):
        pos = 0
        endpos = len(string)
        last_end = 0
        while 1:
            if pos >= endpos:
                break
            for rule, (name, method) in self.lexicon:
                match = rule.match(string, pos)
                if match is not None:
                    start, end = match.span()
                    if start > last_end:
                        yield parse_text(string[last_end:start], state)

                    if name.endswith('_start'):
                        token = method(match, state, string)
                        yield token[0]
                        end = token[1]
                    else:
                        yield method(match, state)
                    last_end = pos = end
                    break
            else:
                found = self.search_pos(string, pos)
                if found is None:
                    break
                pos = found

        if last_end < endpos:
            yield parse_text(string[last_end:], state)
