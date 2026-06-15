import re
from textwrap import indent
from typing import Any, Dict, Iterable, cast

from ..core import BaseRenderer, BlockState
from ..util import strip_end
from ._list import render_list

fenced_re = re.compile(r"^[`~]+", re.M)

#: leading markers that would be parsed as a new block (list, heading, block
#: quote) if they appear unescaped at the start of a line.
_block_prefix_re = re.compile(r"^(\s*)(>|[-+*]|#{1,6}|\d{1,9}[.)])(\s|$)")


class MarkdownRenderer(BaseRenderer):
    """A renderer to re-format Markdown text."""

    NAME = "markdown"

    def __call__(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> str:
        out = self.render_tokens(tokens, state)
        # special handle for line breaks
        out += "\n\n".join(self.render_referrences(state)) + "\n"
        return strip_end(out)

    def render_referrences(self, state: BlockState) -> Iterable[str]:
        ref_links = state.env["ref_links"]
        for key in ref_links:
            attrs = ref_links[key]
            text = "[" + attrs["label"] + "]: " + attrs["url"]
            title = attrs.get("title")
            if title:
                text += ' "' + title + '"'
            yield text

    def render_children(self, token: Dict[str, Any], state: BlockState) -> str:
        children = token["children"]
        return self.render_tokens(children, state)

    def text(self, token: Dict[str, Any], state: BlockState) -> str:
        # a backtick always opens a code span, so it must stay escaped to
        # survive a re-parse as literal text.
        return cast(str, token["raw"]).replace("`", "\\`")

    def emphasis(self, token: Dict[str, Any], state: BlockState) -> str:
        return "*" + self.render_children(token, state) + "*"

    def strong(self, token: Dict[str, Any], state: BlockState) -> str:
        return "**" + self.render_children(token, state) + "**"

    def link(self, token: Dict[str, Any], state: BlockState) -> str:
        label = cast(str, token.get("label"))
        text = self.render_children(token, state)
        out = "[" + text + "]"
        if label:
            return out + "[" + label + "]"

        attrs = token["attrs"]
        url: str = attrs["url"]
        title = attrs.get("title")
        if text == url and not title:
            return "<" + text + ">"
        elif "mailto:" + text == url and not title:
            return "<" + text + ">"

        out += "("
        if "(" in url or ")" in url:
            out += "<" + url + ">"
        else:
            out += url
        if title:
            out += ' "' + title + '"'
        return out + ")"

    def image(self, token: Dict[str, Any], state: BlockState) -> str:
        return "!" + self.link(token, state)

    def codespan(self, token: Dict[str, Any], state: BlockState) -> str:
        return "`" + cast(str, token["raw"]) + "`"

    def linebreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return "  \n"

    def softbreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return "\n"

    def blank_line(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def inline_html(self, token: Dict[str, Any], state: BlockState) -> str:
        return cast(str, token["raw"])

    def paragraph(self, token: Dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        return _escape_block_prefix(text) + "\n\n"

    def heading(self, token: Dict[str, Any], state: BlockState) -> str:
        level = cast(int, token["attrs"]["level"])
        marker = "#" * level
        text = self.render_children(token, state)
        return marker + " " + text + "\n\n"

    def thematic_break(self, token: Dict[str, Any], state: BlockState) -> str:
        return "***\n\n"

    def block_text(self, token: Dict[str, Any], state: BlockState) -> str:
        return _escape_block_prefix(self.render_children(token, state)) + "\n"

    def block_code(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token.get("attrs", {})
        info = cast(str, attrs.get("info", ""))
        code = cast(str, token["raw"])
        if code and code[-1] != "\n":
            code += "\n"

        marker = token.get("marker")
        if not marker:
            marker = _get_fenced_marker(code)
        marker2 = cast(str, marker)
        return marker2 + info + "\n" + code + marker2 + "\n\n"

    def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
        text = indent(self.render_children(token, state), "> ", lambda _: True)
        text = text.rstrip("> \n")
        return text + "\n\n"

    def block_html(self, token: Dict[str, Any], state: BlockState) -> str:
        return cast(str, token["raw"]) + "\n\n"

    def block_error(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def list(self, token: Dict[str, Any], state: BlockState) -> str:
        return render_list(self, token, state)


def _escape_block_prefix(text: str) -> str:
    """Backslash-escape a leading block marker on each line so that literal
    text is not re-parsed as a list, heading or block quote."""
    return "\n".join(_escape_line_prefix(line) for line in text.split("\n"))


def _escape_line_prefix(line: str) -> str:
    m = _block_prefix_re.match(line)
    if not m:
        return line
    indent_, marker = m.group(1), m.group(2)
    return indent_ + marker[:-1] + "\\" + marker[-1] + line[m.end(2) :]


def _get_fenced_marker(code: str) -> str:
    found = fenced_re.findall(code)
    if not found:
        return "```"

    ticks = []  # `
    waves = []  # ~
    for s in found:
        if s[0] == "`":
            ticks.append(len(s))
        else:
            waves.append(len(s))

    if not ticks:
        return "```"

    if not waves:
        return "~~~"
    return "`" * (max(ticks) + 1)
