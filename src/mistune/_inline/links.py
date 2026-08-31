from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Match, Optional, Tuple

from ..core import InlineState
from ..helpers import parse_link as parse_link_destination
from ..helpers import parse_link_label, parse_link_with_end
from ..util import unikey

if TYPE_CHECKING:
    from ..inline_parser import InlineParser


@dataclass
class _LinkBody:
    label: Optional[str]
    text: Optional[str]
    text_start: int
    text_end: int
    end_pos: int
    body_end_pos: int


def parse_link(inline: "InlineParser", m: Match[str], state: InlineState) -> Optional[int]:
    pos = m.end()

    marker = m.group(0)
    is_image = marker[0] == "!"
    if is_image and inline.max_image_depth > 0 and state.image_depth >= inline.max_image_depth:
        state.append_token({"type": "text", "raw": marker + state.src[pos:]})
        return len(state.src)
    if not is_image and state.in_link:
        state.append_token({"type": "text", "raw": marker})
        return pos
    if not is_image and pos <= state.no_link_before:
        state.append_token({"type": "text", "raw": marker})
        return pos
    if is_image and pos <= state.no_image_before:
        state.append_token({"type": "text", "raw": marker})
        return pos

    label, end_pos = parse_link_label(state.src, pos)
    if label is None and pos <= state.no_close_bracket_before:
        state.append_token({"type": "text", "raw": marker})
        return pos

    body = _parse_link_body(state, pos, label, end_pos)
    if body is None:
        return None

    has_nested_link = not is_image and label_contains_link(state, body.text_start, body.text_end)
    if has_nested_link:
        return None
    if body.end_pos >= len(state.src) and body.label is None:
        mark_no_link_before(state, body.body_end_pos)
        return None

    direct_pos = _try_parse_direct_link(inline, m, state, is_image, body)
    if direct_pos is not None:
        return direct_pos
    return _parse_reference_link(inline, state, is_image, body)


def _parse_link_body(
    state: InlineState,
    pos: int,
    label: Optional[str],
    end_pos: Optional[int],
) -> Optional[_LinkBody]:
    if label is None:
        close_pos = find_closing_bracket(state, pos)
        if close_pos is None:
            if len(state.src) > state.no_close_bracket_before:
                state.no_close_bracket_before = len(state.src)
            return None
        end_pos = close_pos + 1
        return _LinkBody(None, None, pos, close_pos, end_pos, end_pos)

    assert end_pos is not None
    return _LinkBody(label, label, pos, end_pos - 1, end_pos, end_pos)


def _try_parse_direct_link(
    inline: "InlineParser",
    m: Match[str],
    state: InlineState,
    is_image: bool,
    body: _LinkBody,
) -> Optional[int]:
    if not is_image:
        rules = ["codespan", "prec_auto_link", "prec_inline_html"]
        prec_pos = inline.precedence_scan(m, state, body.end_pos, rules)
        if prec_pos:
            return prec_pos

    if body.end_pos >= len(state.src):
        return None
    char = state.src[body.end_pos]
    if char == "(":
        attrs, pos, scan_end = parse_link_with_end(state.src, body.end_pos + 1)
        if pos:
            state.append_token(_build_body_token(inline, state, is_image, body, attrs))
            return pos
        if scan_end > body.body_end_pos:
            if is_image:
                mark_no_image_before(state, scan_end)
            else:
                mark_no_link_before(state, scan_end)
    elif char == "[":
        label, pos = parse_link_label(state.src, body.end_pos + 1)
        if pos:
            body.end_pos = pos
            if label:
                body.label = label
    return None


def _parse_reference_link(
    inline: "InlineParser",
    state: InlineState,
    is_image: bool,
    body: _LinkBody,
) -> Optional[int]:
    ref_links = state.env.get("ref_links")
    if body.label is None:
        if not ref_links:
            mark_no_link_before(state, body.body_end_pos)
            return None
        body.label = _get_link_text(state, body)

    if not ref_links:
        mark_no_link_before(state, body.body_end_pos)
        return None

    key = unikey(body.label)
    env = ref_links.get(key)
    if env:
        attrs = {"url": env["url"], "title": env.get("title")}
        token = _build_body_token(inline, state, is_image, body, attrs)
        token["ref"] = key
        token["label"] = body.label
        state.append_token(token)
        return body.end_pos
    mark_no_link_before(state, body.body_end_pos)
    return None


def _get_link_text(state: InlineState, body: _LinkBody) -> str:
    if body.text is None:
        body.text = state.src[body.text_start : body.text_end]
    return body.text


def _build_body_token(
    inline: "InlineParser",
    state: InlineState,
    is_image: bool,
    body: _LinkBody,
    attrs: Optional[Dict[str, object]],
) -> Dict[str, object]:
    return build_link_token(inline, is_image, _get_link_text(state, body), attrs, state)


def build_link_token(
    inline: "InlineParser",
    is_image: bool,
    text: str,
    attrs: Optional[Dict[str, object]],
    state: InlineState,
) -> Dict[str, object]:
    new_state = state.copy()
    new_state.src = text
    if is_image:
        new_state.in_image = True
        new_state.image_depth += 1
        return {
            "type": "image",
            "children": inline.render(new_state),
            "attrs": attrs,
        }
    new_state.in_link = True
    return {
        "type": "link",
        "children": inline.render(new_state),
        "attrs": attrs,
    }


def mark_no_link_before(state: InlineState, end_pos: int) -> None:
    if end_pos > state.no_link_before:
        state.no_link_before = end_pos


def mark_no_image_before(state: InlineState, end_pos: int) -> None:
    if end_pos > state.no_image_before:
        state.no_image_before = end_pos


def find_closing_bracket(state: InlineState, pos: int) -> Optional[int]:
    return get_closing_bracket_map(state).get(pos)


def label_contains_link(state: InlineState, start: int, end: int) -> bool:
    if start >= end:
        return False

    starts, suffix_min_ends = get_link_range_index(state)
    index = bisect_left(starts, start)
    return index < len(starts) and starts[index] < end and suffix_min_ends[index] <= end


def get_link_range_index(state: InlineState) -> Tuple[List[int], List[int]]:
    cache = state.link_ranges.get(id(state.src))
    if cache is not None and cache[0] is state.src:
        return cache[1], cache[2]

    pairs = get_closing_bracket_map(state)
    ranges: List[Tuple[int, int]] = []
    for label_start, close_pos in pairs.items():
        opener = label_start - 1
        if opener > 0 and state.src[opener - 1] == "!":
            continue
        link_end = find_link_range_end(state.src, label_start, close_pos, state)
        if link_end is not None:
            ranges.append((opener, link_end))

    ranges.sort()
    starts = [start for start, _end in ranges]
    suffix_min_ends = [0] * len(ranges)
    min_end = len(state.src) + 1
    for index in range(len(ranges) - 1, -1, -1):
        end = ranges[index][1]
        if end < min_end:
            min_end = end
        suffix_min_ends[index] = min_end

    state.link_ranges[id(state.src)] = (state.src, starts, suffix_min_ends)
    return starts, suffix_min_ends


def get_closing_bracket_map(state: InlineState) -> Dict[int, int]:
    cache = state.link_brackets.get(id(state.src))
    if cache is not None and cache[0] is state.src:
        return cache[1]

    pairs = build_closing_bracket_map(state.src)
    state.link_brackets[id(state.src)] = (state.src, pairs)
    return pairs


def find_link_range_end(src: str, label_start: int, close_pos: int, state: InlineState) -> Optional[int]:
    end_pos = close_pos + 1
    if end_pos < len(src):
        marker = src[end_pos]
        if marker == "(":
            _attrs, new_pos = parse_link_destination(src, end_pos + 1)
            return new_pos

        if marker == "[":
            label, new_pos = parse_link_label(src, end_pos + 1)
            if not new_pos:
                return None
            ref_label = label or src[label_start:close_pos]
            ref_links = state.env.get("ref_links")
            if ref_links and unikey(ref_label) in ref_links:
                return new_pos
            return None

    ref_links = state.env.get("ref_links")
    if ref_links and unikey(src[label_start:close_pos]) in ref_links:
        return end_pos
    return None


def build_closing_bracket_map(src: str) -> Dict[int, int]:
    pairs: Dict[int, int] = {}
    stack: List[int] = []
    pos = 0
    while pos < len(src):
        char = src[pos]
        if char == "\\":
            pos += 2
            continue
        if char == "[":
            stack.append(pos + 1)
        elif char == "]" and stack:
            pairs[stack.pop()] = pos
        pos += 1
    return pairs
