from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Match, Optional, Tuple

from ..core import InlineState
from ..helpers import MAX_LINK_LABEL_LENGTH, parse_link, parse_link_label
from ..util import unikey

if TYPE_CHECKING:
    from ..inline_parser import InlineParser


@dataclass(slots=True)
class Bracket:
    start: int
    token_index: int
    image: bool
    previous_link: Optional[Bracket] = None
    active: bool = True
    nested: bool = False
    child_depth: int = 0


def parse_link_open(inline: InlineParser, m: Match[str], state: InlineState) -> int:
    if state.brackets:
        state.brackets[-1].nested = True
    bracket = Bracket(m.end(), len(state.tokens), m.group(0).startswith("!"), state.last_link)
    if not bracket.image:
        state.last_link = bracket
    state.append_token({"type": "text", "raw": m.group(0)})
    state.brackets.append(bracket)
    return m.end()


def parse_link_close(inline: InlineParser, m: Match[str], state: InlineState) -> int:
    pos = m.start()
    if not state.env.get("ref_links"):
        # Without references, only a ']' immediately followed by '(' can
        # produce a link. Retire the other openers without parsing candidates.
        literal_end = m.end() - int(state.src.startswith("(", m.end()))
        if literal_end > pos:
            _discard_brackets(state, literal_end - pos)
            inline.process_text(state.src[pos:literal_end], state)
            pos = literal_end
    while pos < m.end():
        if not state.brackets:
            inline.process_text(state.src[pos : m.end()], state)
            return m.end()
        pos = _close_bracket(inline, state, pos)
    return pos


def _discard_brackets(state: InlineState, count: int) -> None:
    if count >= len(state.brackets):
        state.brackets.clear()
        state.last_link = None
        return
    discarded = state.brackets[-count:]
    del state.brackets[-count:]
    parent = state.brackets[-1]
    found_link = False
    for bracket in discarded:
        parent.child_depth = max(parent.child_depth, bracket.child_depth)
        if not bracket.image and not found_link:
            state.last_link = bracket.previous_link
            found_link = True


def _close_bracket(inline: InlineParser, state: InlineState, close: int) -> int:
    opener = state.brackets.pop()
    if not opener.image:
        state.last_link = opener.previous_link
    if state.brackets:
        state.brackets[-1].child_depth = max(state.brackets[-1].child_depth, opener.child_depth)
    if not opener.active or (state.in_link and not opener.image):
        inline.process_text("]", state)
        return close + 1

    # A rejected outer wrapper must not repeatedly copy an already deep subtree.
    if state.depth + opener.child_depth >= inline.max_nested_level:
        inline.process_text("]", state)
        return close + 1

    attrs: Optional[Dict[str, Any]] = None
    end = close + 1
    label: Optional[str] = None
    if state.src.startswith("(", end):
        attrs, next_pos = parse_link(state.src, end + 1, max_nested_level=inline.max_nested_level)
        if next_pos is not None:
            end = next_pos
    if attrs is None:
        reference = _parse_reference(state, opener, close, close + 1)
        if reference is None:
            inline.process_text("]", state)
            return close + 1
        attrs, label, end = reference

    children = state.tokens[opener.token_index + 1 :]
    if not opener.image:
        # Automatic links inside explicit link text retain their literal text.
        children = [
            {"type": "text", "raw": child["_autolink"], "_emphasis": False} if "_autolink" in child else child
            for child in children
        ]
    children = inline.finalize_tokens(children, state.depth + 1)
    token: Dict[str, Any] = {"type": "image" if opener.image else "link", "children": children, "attrs": attrs}
    if label is not None:
        token.update(ref=unikey(label), label=label)
    del state.tokens[opener.token_index :]
    state.append_token(token)

    if not opener.image:
        # CommonMark: a successful link deactivates preceding link openers.
        # Each opener is deactivated at most once; images remain eligible.
        bracket = state.last_link
        while bracket is not None and bracket.active:
            bracket.active = False
            bracket = bracket.previous_link
    return end


def _parse_reference(
    state: InlineState, opener: Bracket, close: int, end: int
) -> Optional[Tuple[Dict[str, Any], str, int]]:
    refs = state.env.get("ref_links")
    if not refs:
        return None

    label = None
    next_pos = None
    if state.src.startswith("[", end):
        label, next_pos = parse_link_label(state.src, end + 1)
    if label is None or label == "":
        if opener.nested or close - opener.start > MAX_LINK_LABEL_LENGTH:
            return None
        label = state.src[opener.start : close]
    ref = refs.get(unikey(label))
    if ref is None:
        return None
    return {"url": ref["url"], "title": ref.get("title")}, label, next_pos or end
