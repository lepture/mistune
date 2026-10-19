"""Indexes of closing delimiters for one inline source.

Each delimiter family scans its source once. These are lexical positions, not
memoized parse failures, and are never shared with copied or sliced sources.
"""

import re
from bisect import bisect_left, bisect_right
from typing import Dict, List, Optional, Tuple

_BACKTICKS = re.compile(r"`+")


class DelimiterScanner:
    def __init__(self, src: str) -> None:
        self.src = src
        self._code: Optional[Dict[int, List[int]]] = None
        self._ends: Dict[Tuple[str, bool], List[int]] = {}

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
