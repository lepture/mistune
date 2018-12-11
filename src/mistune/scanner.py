from re import Scanner as _Scanner


class Scanner(_Scanner):
    def iter(self, string, render_text):
        sc = self.scanner.scanner(string)

        pos = 0
        for match in iter(sc.search, None):
            method = self.lexicon[match.lastindex - 1][1]
            hole = string[pos:match.start()]
            if hole:
                yield render_text(hole)

            yield method(match)
            pos = match.end()

        hole = string[pos:]
        if hole:
            yield render_text(hole)
