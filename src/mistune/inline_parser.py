import re
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Match,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    cast,
)

from .core import InlineState, Parser
from .helpers import (
    HTML_ATTRIBUTES,
    HTML_TAGNAME,
    PUNCTUATION,
    parse_link,
    parse_link_label,
    unescape_char,
)
from .util import escape_url, unikey

_REGEX_META_CHARS = set(r"()[]{}?*+|.^$")
_CHARREF_PREFIX = re.compile(r"(#[0-9]{1,7};|#[xX][0-9a-fA-F]+;|[^\t\n\f <&#;]{1,32};)")

AUTO_EMAIL = (
    r"""<[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9]"""
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*>"
)

INLINE_HTML = (
    r"<" + HTML_TAGNAME + HTML_ATTRIBUTES + r"\s*/?>|"  # open tag
    r"</" + HTML_TAGNAME + r"\s*>|"  # close tag
    r"<!--(?!>|->)(?:(?!--)[\s\S])+?(?<!-)-->|"  # comment
    r"<\?[\s\S]+?\?>|"  # script like <?php?>
    r"<![A-Z][\s\S]+?>|"  # doctype
    r"<!\[CDATA[\s\S]+?\]\]>"  # cdata
)


class InlineParser(Parser[InlineState]):
    sc_flag = 0
    state_cls = InlineState

    #: linebreak leaves two spaces at the end of line
    STD_LINEBREAK = r"(?:\\| {2,})\n\s*"

    #: every new line becomes <br>
    HARD_LINEBREAK = r" *\n\s*"

    # we only need to find the start pattern of an inline token
    SPECIFICATION = {
        # e.g. \`, \$
        "escape": r"(?:\\" + PUNCTUATION + ")+",
        # `code, ```code
        "codespan": r"`{1,}",
        # *w, **w, _w, __w
        "emphasis": r"\*{1,3}(?=[^\s*])|\b_{1,3}(?=[^\s_])",
        # [link], ![img]
        "link": r"!?\[",
        # <https://example.com>. regex copied from commonmark.js
        "auto_link": r"<[A-Za-z][A-Za-z0-9.+-]{1,31}:[^<>\x00-\x20]*>",
        "auto_email": AUTO_EMAIL,
        "inline_html": INLINE_HTML,
        "linebreak": STD_LINEBREAK,
        "softbreak": HARD_LINEBREAK,
        "prec_auto_link": r"<[A-Za-z][A-Za-z\d.+-]{1,31}:",
        "prec_inline_html": r"</?" + HTML_TAGNAME + r"|<!|<\?",
    }
    DEFAULT_RULES = (
        "escape",
        "codespan",
        "emphasis",
        "link",
        "auto_link",
        "auto_email",
        "inline_html",
        "linebreak",
    )

    def __init__(self, hard_wrap: bool = False) -> None:
        super(InlineParser, self).__init__()

        self.hard_wrap = hard_wrap
        self._fast_trigger_chars: Optional[Set[str]] = None
        self._fast_trigger_re: Optional[re.Pattern[str]] = None
        self._fast_trigger_re_chars: Optional[Tuple[str, ...]] = None
        # lazy add linebreak
        if hard_wrap:
            self.specification["linebreak"] = self.HARD_LINEBREAK
        else:
            self.rules.append("softbreak")

        self._methods = {name: getattr(self, "parse_" + name) for name in self.rules}

    def register(
        self,
        name: str,
        pattern: Optional[str],
        func: Any,
        before: Optional[str] = None,
    ) -> None:
        super().register(name, pattern, func, before=before)
        self._fast_trigger_chars = None
        self._fast_trigger_re = None
        self._fast_trigger_re_chars = None

    def parse_escape(self, m: Match[str], state: InlineState) -> int:
        text = m.group(0)
        text = unescape_char(text)
        self.process_text(text, state, parse_emphasis=False)
        return m.end()

    def parse_link(self, m: Match[str], state: InlineState) -> Optional[int]:
        pos = m.end()

        marker = m.group(0)
        is_image = marker[0] == "!"
        if not is_image and state.in_link:
            state.append_token({"type": "text", "raw": marker})
            return pos

        text = None
        label, end_pos = parse_link_label(state.src, pos)
        if label is None:
            if pos <= state.no_close_bracket_before:
                state.append_token({"type": "text", "raw": marker})
                return pos
            text, end_pos = _parse_link_text(state, pos)
            if text is None:
                if end_pos > state.no_close_bracket_before:
                    state.no_close_bracket_before = end_pos
                return None

        assert end_pos is not None

        if text is None:
            text = label

        assert text is not None

        if end_pos >= len(state.src) and label is None:
            return None

        if not is_image and self._contains_nested_link(text, state):
            return None

        rules = ["codespan", "prec_auto_link", "prec_inline_html"]
        prec_pos = self.precedence_scan(m, state, end_pos, rules)
        if prec_pos:
            return prec_pos

        if end_pos < len(state.src):
            c = state.src[end_pos]
            if c == "(":
                # standard link [text](<url> "title")
                attrs, pos2 = parse_link(state.src, end_pos + 1)
                if pos2:
                    token = self.__parse_link_token(is_image, text, attrs, state)
                    state.append_token(token)
                    return pos2

            elif c == "[":
                # standard ref link [text][label]
                label2, pos2 = parse_link_label(state.src, end_pos + 1)
                if pos2:
                    end_pos = pos2
                    if label2:
                        label = label2

        if label is None:
            return None

        ref_links = state.env.get("ref_links")
        if not ref_links:
            return None

        key = unikey(label)
        env = ref_links.get(key)
        if env:
            attrs = {"url": env["url"], "title": env.get("title")}
            token = self.__parse_link_token(is_image, text, attrs, state)
            token["ref"] = key
            token["label"] = label
            state.append_token(token)
            return end_pos
        return None

    def _contains_nested_link(self, text: str, state: InlineState) -> bool:
        if "[" not in text:
            return False
        if "](" not in text and "][" not in text and not state.env.get("ref_links"):
            return False

        sc = self.compile_sc(["link"])
        nested_state = state.copy()
        nested_state.src = text
        pos = 0
        while pos < len(text):
            m = sc.search(text, pos)
            if not m:
                return False

            marker = m.group(0)
            if marker == "[" and (m.start() == 0 or text[m.start() - 1] != "!"):
                if _is_link_like(text, m.end(), nested_state):
                    return True
            pos = m.start() + 1

        return False

    def __parse_link_token(
        self,
        is_image: bool,
        text: str,
        attrs: Optional[Dict[str, Any]],
        state: InlineState,
    ) -> Dict[str, Any]:
        new_state = state.copy()
        new_state.src = text
        if is_image:
            new_state.in_image = True
            token = {
                "type": "image",
                "children": self.render(new_state),
                "attrs": attrs,
            }
        else:
            new_state.in_link = True
            token = {
                "type": "link",
                "children": self.render(new_state),
                "attrs": attrs,
            }
        return token

    def parse_auto_link(self, m: Match[str], state: InlineState) -> int:
        text = m.group(0)
        pos = m.end()
        if state.in_link:
            self.process_text(text, state)
            return pos

        text = text[1:-1]
        self._add_auto_link(text, text, state)
        return pos

    def parse_auto_email(self, m: Match[str], state: InlineState) -> int:
        text = m.group(0)
        pos = m.end()
        if state.in_link:
            self.process_text(text, state)
            return pos

        text = text[1:-1]
        url = "mailto:" + text
        self._add_auto_link(url, text, state)
        return pos

    def _add_auto_link(self, url: str, text: str, state: InlineState) -> None:
        state.append_token(
            {
                "type": "link",
                "children": [{"type": "text", "raw": text}],
                "attrs": {"url": escape_url(url)},
            }
        )

    def parse_emphasis(self, m: Match[str], state: InlineState) -> int:
        self.process_text(m.group(0), state)
        return m.end()

    def parse_codespan(self, m: Match[str], state: InlineState) -> int:
        marker = m.group(0)
        # require same marker with same length at end

        pattern = re.compile(r"(.*?[^`])" + marker + r"(?!`)", re.S)

        pos = m.end()
        m2 = pattern.match(state.src, pos)
        if m2:
            end_pos = m2.end()
            code = m2.group(1)
            # Line endings are treated like spaces
            code = code.replace("\n", " ")
            if len(code.strip()):
                if code.startswith(" ") and code.endswith(" "):
                    code = code[1:-1]
            state.append_token({"type": "codespan", "raw": code})
            return end_pos
        else:
            state.append_token({"type": "text", "raw": marker})
            return pos

    def parse_linebreak(self, m: Match[str], state: InlineState) -> int:
        state.append_token({"type": "linebreak"})
        return m.end()

    def parse_softbreak(self, m: Match[str], state: InlineState) -> int:
        state.append_token({"type": "softbreak"})
        return m.end()

    def parse_inline_html(self, m: Match[str], state: InlineState) -> int:
        end_pos = m.end()
        html = m.group(0)
        state.append_token({"type": "inline_html", "raw": html})
        if html.startswith(("<a ", "<a>", "<A ", "<A>")):
            state.in_link = True
        elif html.startswith(("</a ", "</a>", "</A ", "</A>")):
            state.in_link = False
        return end_pos

    def process_text(self, text: str, state: InlineState, parse_emphasis: bool = True) -> None:
        if (
            parse_emphasis
            and state.tokens
            and state.tokens[-1]["type"] == "text"
            and state.tokens[-1].get("_emphasis", True)
            and not _is_entity_boundary(state.tokens[-1]["raw"], text)
        ):
            state.tokens[-1]["raw"] += text
        else:
            token: Dict[str, Any] = {"type": "text", "raw": text}
            if not parse_emphasis:
                token["_emphasis"] = False
            state.append_token(token)

    def parse(self, state: InlineState) -> List[Dict[str, Any]]:
        pos = 0
        sc = self.compile_sc()
        while pos < len(state.src):
            fast_end = self._find_fast_text_end(state.src, pos)
            if fast_end is None:
                m = sc.search(state.src, pos)
            else:
                if fast_end > pos:
                    self.process_text(state.src[pos:fast_end], state)
                    pos = fast_end
                if pos >= len(state.src):
                    break
                m = sc.match(state.src, pos)

            if not m:
                if fast_end is not None:
                    self.process_text(state.src[pos : pos + 1], state)
                    pos += 1
                    continue
                break

            end_pos = m.start()
            if end_pos > pos:
                hole = state.src[pos:end_pos]
                self.process_text(hole, state)

            new_pos = self.parse_method(m, state)
            if not new_pos:
                # move cursor 1 character forward
                pos = end_pos + 1
                hole = state.src[end_pos:pos]
                self.process_text(hole, state)
            else:
                pos = new_pos

        if pos == 0:
            # special case, just pure text
            self.process_text(state.src, state)
        elif pos < len(state.src):
            self.process_text(state.src[pos:], state)
        state.tokens = _finalize_emphasis_tokens(state.tokens, "emphasis" in self.rules)
        return state.tokens

    def _find_fast_text_end(self, src: str, pos: int) -> Optional[int]:
        chars = self._get_fast_trigger_chars()
        if chars is None:
            return None

        trigger_re = self._get_fast_trigger_re(chars)
        m = trigger_re.search(src, pos)
        if m is None:
            return len(src)

        if m.group(0) == "\n":
            return self._find_linebreak_start(src, pos, m.start())
        return m.start()

    def _get_fast_trigger_re(self, chars: Set[str]) -> re.Pattern[str]:
        key = tuple(sorted(chars))
        if self._fast_trigger_re is None or self._fast_trigger_re_chars != key:
            pattern = "[" + re.escape("".join(key)) + "]"
            self._fast_trigger_re = re.compile(pattern)
            self._fast_trigger_re_chars = key
        assert self._fast_trigger_re is not None
        return self._fast_trigger_re

    def _find_linebreak_start(self, src: str, min_pos: int, newline_pos: int) -> int:
        pos = newline_pos
        while pos > min_pos and src[pos - 1] == " ":
            pos -= 1
        if pos == newline_pos and pos > min_pos and src[pos - 1] == "\\":
            return pos - 1
        return pos

    def _get_fast_trigger_chars(self) -> Optional[Set[str]]:
        chars = self._fast_trigger_chars
        if chars is not None:
            return chars

        chars = set()
        for name in self.rules:
            pattern = self.specification.get(name)
            rule_chars = _get_rule_start_chars(name, pattern)
            if rule_chars is None:
                self._fast_trigger_chars = None
                return None
            chars.update(rule_chars)
        self._fast_trigger_chars = chars
        return chars

    def precedence_scan(
        self,
        m: Match[str],
        state: InlineState,
        end_pos: int,
        rules: Optional[List[str]] = None,
    ) -> Optional[int]:
        if rules is None:
            rules = ["codespan", "link", "prec_auto_link", "prec_inline_html"]

        mark_pos = m.end()
        sc = self.compile_sc(rules)
        m1 = sc.search(state.src, mark_pos, end_pos)
        if not m1:
            return None

        lastgroup = m1.lastgroup
        if not lastgroup:
            return None
        rule_name = lastgroup.replace("prec_", "")
        sc = self.compile_sc([rule_name])
        m2 = sc.match(state.src, m1.start())
        if not m2:
            return None

        func = self._methods[rule_name]
        new_state = state.copy()
        new_state.src = state.src
        m2_pos = func(m2, new_state)
        if not m2_pos or m2_pos < end_pos:
            return None

        raw_text = state.src[m.start() : m2.start()]
        state.append_token({"type": "text", "raw": raw_text})
        for token in new_state.tokens:
            state.append_token(token)
        return m2_pos

    def render(self, state: InlineState) -> List[Dict[str, Any]]:
        self.parse(state)
        return state.tokens

    def __call__(self, s: str, env: MutableMapping[str, Any]) -> List[Dict[str, Any]]:
        state = self.state_cls(env)
        state.src = s
        return self.render(state)


def _get_rule_start_chars(name: str, pattern: Optional[str]) -> Optional[Set[str]]:
    known = {
        "escape": {"\\"},
        "codespan": {"`"},
        "emphasis": {"*", "_"},
        "link": {"!", "["},
        "auto_link": {"<"},
        "auto_email": {"<"},
        "inline_html": {"<"},
        "linebreak": {"\n"},
        "softbreak": {"\n"},
        "prec_auto_link": {"<"},
        "prec_inline_html": {"<"},
        # built-in plugins
        "url_link": {"h"},
        "strikethrough": {"~"},
        "mark": {"="},
        "insert": {"^"},
        "superscript": {"^"},
        "subscript": {"~"},
        "footnote": {"["},
        "inline_math": {"$"},
        "ruby": {"["},
        "inline_spoiler": {">"},
    }
    if name in known:
        return known[name]
    if not pattern:
        return set()
    return _guess_pattern_start_chars(pattern)


def _guess_pattern_start_chars(pattern: str) -> Optional[Set[str]]:
    if not pattern:
        return set()

    if pattern.startswith("\\") and len(pattern) > 1:
        c = pattern[1]
        if c in _REGEX_META_CHARS or c in PUNCTUATION:
            return {c}
        return None

    c = pattern[0]
    if c in _REGEX_META_CHARS or c.isspace():
        return None
    return {c}


def _is_entity_boundary(left: str, right: str) -> bool:
    return left.endswith("&") and _CHARREF_PREFIX.match(right) is not None


@dataclass
class _Delimiter:
    index: int
    marker: str
    length: int
    can_open: bool
    can_close: bool


def _finalize_emphasis_tokens(tokens: List[Dict[str, Any]], enabled: bool) -> List[Dict[str, Any]]:
    if not enabled:
        return _clean_emphasis_tokens(tokens)
    if not _contains_emphasis_marker(tokens):
        return _clean_emphasis_tokens(tokens)

    parts: List[Dict[str, Any]] = []
    delimiters: List[_Delimiter] = []
    source = _emphasis_source_text(tokens)
    source_pos = 0
    for token in tokens:
        if token["type"] == "text" and token.get("_emphasis", True):
            _split_text_token(token, source, source_pos, parts, delimiters)
        else:
            parts.append(_clean_emphasis_token(token))
        source_pos += _emphasis_source_length(token)

    _process_emphasis_delimiters(parts, delimiters)
    return _merge_text_tokens(parts)


def _contains_emphasis_marker(tokens: List[Dict[str, Any]]) -> bool:
    for token in tokens:
        if token["type"] == "text" and token.get("_emphasis", True):
            raw = token["raw"]
            if "*" in raw or "_" in raw:
                return True
    return False


def _clean_emphasis_tokens(tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_clean_emphasis_token(token) for token in tokens]


def _clean_emphasis_token(token: Dict[str, Any]) -> Dict[str, Any]:
    if "_emphasis" not in token:
        return token
    token = token.copy()
    token.pop("_emphasis", None)
    return token


def _emphasis_source_text(tokens: List[Dict[str, Any]]) -> str:
    values = []
    for token in tokens:
        if token["type"] == "text":
            values.append(token["raw"])
        elif token["type"] in ("softbreak", "linebreak"):
            values.append("\n")
        else:
            values.append("\ufffc")
    return "".join(values)


def _emphasis_source_length(token: Dict[str, Any]) -> int:
    if token["type"] == "text":
        return len(token["raw"])
    return 1


def _split_text_token(
    token: Dict[str, Any],
    source: str,
    source_start: int,
    parts: List[Dict[str, Any]],
    delimiters: List[_Delimiter],
) -> None:
    text = token["raw"]
    pos = 0
    while pos < len(text):
        if text[pos] not in "*_":
            end = _next_delimiter_run(text, pos)
            parts.append({"type": "text", "raw": text[pos:end]})
            pos = end
            continue

        marker = text[pos]
        end = pos
        while end < len(text) and text[end] == marker:
            end += 1
        length = end - pos
        absolute = source_start + pos
        can_open = _can_open_emphasis(source, absolute, length, marker)
        can_close = _can_close_emphasis(source, absolute, length, marker)
        index = len(parts)
        parts.append({"type": "text", "raw": text[pos:end]})
        if can_open or can_close:
            delimiters.append(_Delimiter(index, marker, length, can_open, can_close))
        pos = end


def _next_delimiter_run(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] not in "*_":
        pos += 1
    return pos


def _process_emphasis_delimiters(parts: List[Dict[str, Any]], delimiters: List[_Delimiter]) -> None:
    closer_pos = 0
    openers_bottom: Dict[Tuple[str, int, bool], int] = {}
    while closer_pos < len(delimiters):
        closer = delimiters[closer_pos]
        if not closer.can_close or closer.length == 0:
            closer_pos += 1
            continue

        opener_key = (closer.marker, closer.length % 3, closer.can_open)
        opener_pos = closer_pos - 1
        opener_bottom = openers_bottom.get(opener_key, 0)
        opener = None
        while opener_pos >= opener_bottom:
            candidate = delimiters[opener_pos]
            if (
                candidate.marker == closer.marker
                and candidate.can_open
                and candidate.length > 0
                and _can_match_emphasis_delimiters(candidate, closer)
            ):
                opener = candidate
                break
            opener_pos -= 1

        if opener is None:
            openers_bottom[opener_key] = closer_pos
            closer_pos += 1
            continue

        if opener.length >= 2 and closer.length >= 2:
            use_length = 2
        else:
            use_length = 1
        if use_length == 2 and not _has_strong_enabled(parts, opener, closer):
            use_length = 1
        if use_length == 1 and not _has_emphasis_enabled(parts, opener, closer):
            closer_pos += 1
            continue
        if not _has_emphasis_content(parts, opener.index + 1, closer.index):
            closer_pos += 1
            continue

        opener_text = parts[opener.index]
        closer_text = parts[closer.index]
        if opener_text["type"] != "text" or closer_text["type"] != "text":
            closer_pos += 1
            continue

        opener_text["raw"] = opener_text["raw"][:-use_length]
        closer_text["raw"] = closer_text["raw"][use_length:]
        children = parts[opener.index + 1 : closer.index]
        if use_length == 2:
            node = {"type": "strong", "children": children}
        else:
            node = {"type": "emphasis", "children": children}

        old_closer_index = closer.index
        parts[opener.index + 1 : old_closer_index] = [node]

        removed = old_closer_index - opener.index - 2
        closer.index = opener.index + 2
        if removed:
            for delimiter in delimiters:
                if opener.index < delimiter.index < old_closer_index:
                    delimiter.length = 0
                elif delimiter.index >= old_closer_index:
                    delimiter.index -= removed

        opener.length -= use_length
        closer.length -= use_length
        if opener.length == 0:
            opener.can_open = False
        if closer.length == 0:
            closer.can_close = False

        if opener.can_open or closer.can_close:
            closer_pos = max(opener_pos, openers_bottom.get(opener_key, 0))
        else:
            closer_pos += 1


def _has_strong_enabled(parts: List[Dict[str, Any]], opener: _Delimiter, closer: _Delimiter) -> bool:
    return len(_text_raw(parts[opener.index])) >= 2 and len(_text_raw(parts[closer.index])) >= 2


def _has_emphasis_enabled(parts: List[Dict[str, Any]], opener: _Delimiter, closer: _Delimiter) -> bool:
    return bool(_text_raw(parts[opener.index]) and _text_raw(parts[closer.index]))


def _text_raw(token: Dict[str, Any]) -> str:
    if token["type"] == "text":
        return cast(str, token["raw"])
    return ""


def _has_emphasis_content(parts: List[Dict[str, Any]], start: int, end: int) -> bool:
    for part in parts[start:end]:
        if part["type"] != "text" or part["raw"] != "":
            return True
    return False


def _can_match_emphasis_delimiters(opener: _Delimiter, closer: _Delimiter) -> bool:
    if opener.can_close or closer.can_open:
        return (opener.length + closer.length) % 3 != 0 or opener.length % 3 == 0 and closer.length % 3 == 0
    return True


def _can_open_emphasis(text: str, start: int, size: int, marker: str) -> bool:
    if start > 0:
        previous = text[start - 1]
    else:
        previous = "\n"
    if start + size < len(text):
        next_char = text[start + size]
    else:
        next_char = "\n"
    if marker == "_" and previous.isalnum() and next_char.isalnum():
        return False
    if next_char.isspace():
        return False
    if _is_punctuation(next_char) and not previous.isspace() and not _is_punctuation(previous):
        return False
    return True


def _can_close_emphasis(text: str, start: int, size: int, marker: str) -> bool:
    if start > 0:
        previous = text[start - 1]
    else:
        previous = "\n"
    if start + size < len(text):
        next_char = text[start + size]
    else:
        next_char = "\n"
    if marker == "_" and previous.isalnum() and next_char.isalnum():
        return False
    if previous.isspace():
        return False
    if _is_punctuation(previous) and not next_char.isspace() and not _is_punctuation(next_char):
        return False
    return True


def _is_punctuation(c: str) -> bool:
    return not c.isspace() and not c.isalnum()


def _merge_text_tokens(tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for token in tokens:
        if token["type"] == "text" and token["raw"] == "":
            continue
        if token["type"] == "text" and result and result[-1]["type"] == "text":
            if not _is_entity_boundary(result[-1]["raw"], token["raw"]):
                result[-1]["raw"] += token["raw"]
                continue
        result.append(_clean_emphasis_token(token))
    return result


def _parse_link_text(state: InlineState, pos: int) -> Tuple[Optional[str], int]:
    close_pos = _find_closing_bracket(state, pos)
    if close_pos is None:
        return None, len(state.src)
    return state.src[pos:close_pos], close_pos + 1


def _find_closing_bracket(state: InlineState, pos: int) -> Optional[int]:
    cache = state.link_brackets.get(id(state.src))
    if cache is not None and cache[0] is state.src:
        return cache[1].get(pos)

    pairs = _build_closing_bracket_map(state.src)
    state.link_brackets[id(state.src)] = (state.src, pairs)
    return pairs.get(pos)


def _is_link_like(src: str, pos: int, state: InlineState) -> bool:
    label, end_pos = parse_link_label(src, pos)
    if label is None:
        label, end_pos = _parse_link_text(state, pos)
        if label is None:
            return False

    assert label is not None
    assert end_pos is not None

    if end_pos >= len(src):
        ref_links = state.env.get("ref_links")
        return bool(ref_links and unikey(label) in ref_links)

    marker = src[end_pos]
    if marker == "(":
        _attrs, new_pos = parse_link(src, end_pos + 1)
        return bool(new_pos)

    if marker == "[":
        label2, new_pos = parse_link_label(src, end_pos + 1)
        if not new_pos:
            return False
        if label2:
            label = label2

    ref_links = state.env.get("ref_links")
    return bool(ref_links and unikey(label) in ref_links)


def _build_closing_bracket_map(src: str) -> Dict[int, int]:
    pairs: Dict[int, int] = {}
    stack: List[int] = []
    pos = 0
    while pos < len(src):
        c = src[pos]
        if c == "\\":
            pos += 2
            continue
        if c == "[":
            stack.append(pos + 1)
        elif c == "]" and stack:
            pairs[stack.pop()] = pos
        pos += 1
    return pairs
