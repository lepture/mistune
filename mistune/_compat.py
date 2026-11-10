class Scanner:
    """Partial copy of re.Scanner from python 3.14.

    Python >=3.15 (as well as 3.14.1 and 3.13.10) break re.Scanner for our purposes
    by strictly enforcing that patterns not contain capturing groups. The motivation
    for this change appears to be that the use of *named* capturing groups cause
    trouble (https://github.com/lepture/mistune/issues/551).

    This version should work with python >= 3.11. Before that, though the code was
    fundamentally unchanged as least as far back as python 2.7, there were modules and
    bits that were renamed.

    """
    def __init__(self, lexicon, flags=0):
        from re import RegexFlag
        from re._constants import BRANCH, SUBPATTERN  # type: ignore[ty:unresolved-import]
        from re import _compiler, _parser  # type: ignore[ty:unresolved-import]
        if isinstance(flags, RegexFlag):
            flags = flags.value
        self.lexicon = lexicon
        # combine phrases into a compound pattern
        p = []
        s = _parser.State()
        s.flags = flags
        for phrase, _action in lexicon:
            gid = s.opengroup()
            p.append(_parser.SubPattern(s, [
                (SUBPATTERN, (gid, 0, 0, _parser.parse(phrase, flags))),
                ]))
            s.closegroup(gid, p[-1])
        p = _parser.SubPattern(s, [(BRANCH, (None, p))])
        self.scanner = _compiler.compile(p)

    def scan(self, string):
        # mistune doesn't use Scanner.scan
        raise NotImplementedError
