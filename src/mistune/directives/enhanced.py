import re
from typing import List, Match, Optional, Dict, Any

from ._base import BaseDirective, DirectiveParser, DirectivePlugin

if False:
    from ..block_parser import BlockParser
    from ..core import BlockState
    from ..markdown import Markdown


__all__ = ["EnhancedDirective", "TabsDirective", "TipDirective"]


def parse_options(text: str) -> Dict[str, str]:
    """Parse options from directive content."""
    options = {}
    if not text:
        return options
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith(':'):
            continue
        parts = line.split(':', 2)
        if len(parts) < 3:
            continue
        key = parts[1].strip()
        value = parts[2].strip()
        options[key] = value
    return options


class EnhancedParser(DirectiveParser):
    name = "enhanced_directive"

    @staticmethod
    def parse_type(m: Match[str]) -> str:
        return m.group("type")

    @staticmethod
    def parse_title(m: Match[str]) -> str:
        return m.group("title").strip() if m.group("title") else ""

    @staticmethod
    def parse_content(m: Match[str]) -> str:
        return m.group("text").strip() if m.group("text") else ""

    @staticmethod
    def parse_options(m: Match[str]) -> Dict[str, str]:
        return parse_options(m.group("options"))


class TabsDirective(DirectivePlugin):
    """Directive for tabs container."""

    name = "tabs"

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> None:
        title = m.group("title").strip() if m.group("title") else ""
        options = parse_options(m.group("options"))
        content = m.group("text").strip() if m.group("text") else ""

        # Create a child state to parse the content
        child = state.child_state(content, container_type="tabs")
        block.parse(child)

        token = {
            "type": "tabs",
            "title": title,
            "options": options,
            "children": child.tokens,
        }
        state.append_token(token)

    def __call__(self, directive: BaseDirective, md: "Markdown") -> None:
        directive.register(self.name, self.parse)


class TipDirective(DirectivePlugin):
    """Directive for tip container."""

    name = "tip"

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> None:
        title = m.group("title").strip() if m.group("title") else ""
        options = parse_options(m.group("options"))
        content = m.group("text").strip() if m.group("text") else ""

        # Create a child state to parse the content
        child = state.child_state(content, container_type="tip")
        block.parse(child)

        token = {
            "type": "tip",
            "title": title,
            "options": options,
            "children": child.tokens,
        }
        state.append_token(token)

    def __call__(self, directive: BaseDirective, md: "Markdown") -> None:
        directive.register(self.name, self.parse)


class EnhancedDirective(BaseDirective):
    """Enhanced directive parser for block-level containers like ::: tabs and ::: tip."""

    parser = EnhancedParser

    def __init__(self, plugins: List[DirectivePlugin], markers: str = ":") -> None:
        super(EnhancedDirective, self).__init__(plugins)
        self.markers = markers
        _marker_pattern = "|".join(re.escape(c) for c in markers)
        self.directive_pattern = (
            r"^(?P<enhanced_directive_mark>(?:" + _marker_pattern + r"){3,})"
            r"[ \t]*(?P<type>[a-zA-Z0-9_-]+)"
            r"[ \t]*(?P<title>[^\n]*)"
            r"(?:\n|$)"
            r"(?P<options>(?:\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)"
            r"\n*(?P<text>(?:[^\n]*\n+)*)"
        )
        self._directive_re = re.compile(self.directive_pattern, re.M)

    def _process_directive(self, block: "BlockParser", marker: str, start: int, state: "BlockState") -> Optional[int]:
        mlen = len(marker)
        cursor_start = start + len(marker)

        _end_pattern = (
            r"^ {0,3}" + marker[0] + "{" + str(mlen) + r",}"
            r"[ \t]*(?:\n|$)"
        )
        _end_re = re.compile(_end_pattern, re.M)

        _end_m = _end_re.search(state.src, cursor_start)
        if _end_m:
            text = state.src[cursor_start : _end_m.start()]
            end_pos = _end_m.end()
        else:
            text = state.src[cursor_start:]
            end_pos = state.cursor_max

        # Parse the directive content
        directive_re = re.compile(
            r"^[ \t]*(?P<type>[a-zA-Z0-9_-]+)[ \t]*(?P<title>[^\n]*)(?:\n|$)(?P<options>(?:\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)\n*(?P<text>(?:[^\n]*\n+)*)",
            re.DOTALL
        )
        m = directive_re.match(text)
        if not m:
            return None

        self.parse_method(block, m, state)
        return end_pos

    def parse_directive(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
        marker = m.group("enhanced_directive_mark")
        return self._process_directive(block, marker, m.start(), state)

    def __call__(self, md: "Markdown") -> None:
        super(EnhancedDirective, self).__call__(md)
        # Register the directive pattern
        md.block.register(
            "enhanced_directive",
            r"^(?P<enhanced_directive_mark>:{3,})[ \t]*(?P<type>[a-zA-Z0-9_-]+)",
            self.parse_directive,
            before="fenced_code"
        )
