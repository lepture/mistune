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
