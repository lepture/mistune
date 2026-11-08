"""Indexes of closing delimiters for one inline source.

Each delimiter family scans its source once. These are lexical positions, not
memoized parse failures, and are never shared with copied or sliced sources.
"""

import re
from bisect import bisect_left, bisect_right
from typing import Dict, List, Optional, Tuple

_BACKTICKS = re.compile(r"`+")
_LINK_TAIL = re.compile(r"\]\(")
_TAG_OPEN = re.compile(r"<")
_BRACKET = re.compile(r"\[")
_LINK, _TAG = 0, 1


class DelimiterScanner:
    def __init__(self, src: str) -> None:
        self.src = src
        self._code: Optional[Dict[int, List[int]]] = None
        self._ends: Dict[Tuple[str, bool], List[int]] = {}
        self._openers: Optional[Tuple[List[int], List[int]]] = None
        self._outside_code: Dict[str, Dict[int, Optional[int]]] = {}
        self._wrappers: Optional[Tuple[List[int], List[int]]] = None
        self._wrapper_ends: Dict[Tuple[int, int], Optional[int]] = {}

    def code_end(self, marker: str, pos: int) -> Optional[int]:
        size = len(marker)
        if self._code is None:
            end = self.src.find(marker, pos)
            if end >= 0 and (end == 0 or self.src[end - 1] != "`"):
                after = end + size
                if after == len(self.src) or self.src[after] != "`":
                    return end
            self._code = {}
            for match in _BACKTICKS.finditer(self.src):
                self._code.setdefault(match.end() - match.start(), []).append(match.start())
        positions = self._code.get(size, [])
        index = bisect_left(positions, pos)
        return positions[index] if index < len(positions) else None

    def find(self, marker: str, pos: int, *, formatting: bool = False) -> Optional[int]:
        key = (marker, formatting)
        positions = self._ends.get(key)
        if positions is None:
            positions = []
            start = self.src.find(marker)
            while start >= 0:
                if not formatting or _formatting_closer(self.src, start, marker):
                    positions.append(start)
                start = self.src.find(marker, start + 1)
            self._ends[key] = positions
        index = bisect_right(positions, pos) if formatting else bisect_left(positions, pos)
        return positions[index] if index < len(positions) else None

    def find_outside_code(self, marker: str, pos: int) -> Optional[int]:
        """Find a formatting closer after ``pos`` that is not inside a code span.

        Code spans bind more tightly than formatting markers, so a closer such
        as the ``~~`` in ``~~a `b~~c` d~~`` belongs to the code span.
        """
        close = self.find(marker, pos, formatting=True)
        if close is None:
            return None
        starts, sizes = self._code_openers()
        # Once a scan reaches a backtick run, the rest of the search depends
        # only on that run, so every scan passing through it shares the result.
        known = self._outside_code.setdefault(marker, {})
        visited: List[int] = []
        index = bisect_left(starts, pos)
        result: Optional[int] = close
        while index < len(starts):
            start = starts[index]
            if start >= close:
                break
            if start in known:
                result = known[start]
                break
            visited.append(start)
            wrapper_end = self._wrapper_end(start)
            if wrapper_end is not None:
                index = bisect_left(starts, wrapper_end)
                continue
            size = sizes[index]
            end = self.code_end("`" * size, start + size)
            if end is None:
                index += 1
                continue
            after = end + size
            if after > close:
                result = close = self.find(marker, after - 1, formatting=True)
                if close is None:
                    break
            index = bisect_left(starts, after)
        for start in visited:
            known[start] = result
        return result

    def _code_openers(self) -> Tuple[List[int], List[int]]:
        if self._openers is None:
            starts: List[int] = []
            sizes: List[int] = []
            for match in _BACKTICKS.finditer(self.src):
                start, end = match.span()
                # An escaped first backtick is literal; the rest of the run can still open.
                if _escaped(self.src, start):
                    start += 1
                if start < end:
                    starts.append(start)
                    sizes.append(end - start)
            self._openers = (starts, sizes)
        return self._openers

    def _wrapper_end(self, pos: int) -> Optional[int]:
        """Return the end of a link destination, autolink or HTML tag around ``pos``.

        The inline parser consumes ``(destination "title")`` after a link label,
        ``<scheme:...>`` and ``<tag attr="...">`` as a whole, so a backtick in
        them never opens a code span.
        """
        if self._wrappers is None:
            src = self.src
            # Link text needs an unescaped "[" somewhere before its "](".
            first_bracket = next((m.start() for m in _BRACKET.finditer(src) if not _escaped(src, m.start())), len(src))
            links = [
                match.start() + 1
                for match in _LINK_TAIL.finditer(src, first_bracket)
                if not _escaped(src, match.start())
            ]
            tags = [match.start() for match in _TAG_OPEN.finditer(src) if not _escaped(src, match.start())]
            self._wrappers = (links, tags)
        for kind, opens in enumerate(self._wrappers):
            index = bisect_left(opens, pos) - 1
            if index < 0:
                continue
            key = (kind, index)
            if key not in self._wrapper_ends:
                self._wrapper_ends[key] = self._parse_wrapper(kind, opens, index)
            end = self._wrapper_ends[key]
            if end is not None and end > pos:
                return end
        return None

    def _parse_wrapper(self, kind: int, opens: List[int], index: int) -> Optional[int]:
        # Each candidate is parsed only up to the next candidate of its kind,
        # which keeps the total work linear. A destination or title holding a
        # literal "](", or an attribute value holding "<", is therefore missed.
        # Imported here because helpers and inline_parser import core, which
        # imports this module.
        from ..helpers import parse_link
        from ..inline_parser import _AUTO_EMAIL_RE, _AUTO_LINK_RE, _INLINE_HTML_TAG

        start = opens[index]
        limit = opens[index + 1] if index + 1 < len(opens) else len(self.src)
        if kind == _LINK:
            _attrs, end = parse_link(self.src[start + 1 : limit], 0)
            return None if end is None else start + 1 + end
        for pattern in (_AUTO_LINK_RE, _AUTO_EMAIL_RE, _INLINE_HTML_TAG):
            match = pattern.match(self.src, start, limit)
            if match:
                return match.end()
        return None


def _escaped(src: str, pos: int) -> bool:
    backslashes = 0
    while pos - backslashes > 0 and src[pos - backslashes - 1] == "\\":
        backslashes += 1
    return backslashes % 2 == 1


def _formatting_closer(src: str, start: int, marker: str) -> bool:
    char = marker[0]
    end = start + len(marker)
    if end < len(src) and src[end] == char and not src.startswith(marker, end):
        return False
    if not start:
        return False
    previous = src[start - 1]
    if previous != char:
        return not previous.isspace()
    # A literal escaped first character can precede a closing pair in a run.
    if start < 2 or src[start - 2] != "\\":
        return False
    backslashes = 0
    pos = start - 2
    while pos >= 0 and src[pos] == "\\":
        backslashes += 1
        pos -= 1
    return backslashes % 2 == 1
