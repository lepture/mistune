from textwrap import indent
from typing import Any, Dict, Iterable, List, Optional, cast

from ..core import BaseRenderer, BlockState
from ..util import strip_end
from ._list import render_list, render_list_item


class RSTRenderer(BaseRenderer):
    """A renderer for converting Markdown to ReST."""

    NAME = "rst"

    #: marker symbols for heading
    HEADING_MARKERS = {
        1: "=",
        2: "-",
        3: "~",
        4: "^",
        5: '"',
        6: "'",
    }
    INLINE_IMAGE_PREFIX = "img-"

    #: inline token types whose rendered output never glues to an adjacent
    #: inline role: softbreak renders as a space, inline_html renders as
    #: nothing, and the <linebreak> marker is consumed by the paragraph
    #: line-break split before docutils parses the output
    ROLE_SAFE_NEIGHBORS = frozenset({"softbreak", "linebreak", "inline_html"})

    def iter_tokens(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> Iterable[str]:
        prev = None
        # ignore blank line
        tokens = [tok for tok in tokens if tok["type"] != "blank_line"]
        for index, tok in enumerate(tokens):
            tok["prev"] = prev
            tok["next"] = tokens[index + 1] if index + 1 < len(tokens) else None
            prev = tok
            yield self.render_token(tok, state)

    def __call__(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> str:
        state.env["inline_images"] = []
        out = self.render_tokens(tokens, state)
        # special handle for line breaks
        out += "\n\n".join(self.render_referrences(state)) + "\n"
        return strip_end(out)

    def render_referrences(self, state: BlockState) -> Iterable[str]:
        images = state.env["inline_images"]
        for index, token in enumerate(images):
            attrs = token["attrs"]
            alt = self.render_children(token, state)
            ident = self.INLINE_IMAGE_PREFIX + str(index)
            yield ".. |" + ident + "| image:: " + attrs["url"] + "\n   :alt: " + alt

    def render_children(self, token: Dict[str, Any], state: BlockState) -> str:
        children = token["children"]
        return self.render_tokens(children, state)

    def text(self, token: Dict[str, Any], state: BlockState) -> str:
        text = cast(str, token["raw"])
        return text.replace("|", r"\|")

    def emphasis(self, token: Dict[str, Any], state: BlockState) -> str:
        return "*" + self.render_children(token, state) + "*"

    def strong(self, token: Dict[str, Any], state: BlockState) -> str:
        return "**" + self.render_children(token, state) + "**"

    def link(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token["attrs"]
        text = self.render_children(token, state)
        return "`" + text + " <" + cast(str, attrs["url"]) + ">`__"

    def image(self, token: Dict[str, Any], state: BlockState) -> str:
        refs: List[Dict[str, Any]] = state.env["inline_images"]
        index = len(refs)
        refs.append(token)
        return "|" + self.INLINE_IMAGE_PREFIX + str(index) + "|"

    def codespan(self, token: Dict[str, Any], state: BlockState) -> str:
        return "``" + cast(str, token["raw"]) + "``"

    @classmethod
    def needs_role_boundary(
        cls, token: Optional[Dict[str, Any]], edge: str
    ) -> bool:
        """Tell whether an inline role touching this neighbor needs an
        escaped-space boundary to stay recognizable by docutils.

        ``edge`` is the side of the neighbor facing the role: ``"tail"``
        for the preceding token, ``"head"`` for the following one.
        """
        if token is None:
            return False
        tok_type = token["type"]
        if tok_type in cls.ROLE_SAFE_NEIGHBORS:
            return False
        if tok_type == "text":
            raw = cast(str, token["raw"])
            if not raw:
                return False
            char = raw[-1] if edge == "tail" else raw[0]
            return not char.isspace()
        # every other inline token (emphasis, strong, codespan, link,
        # image, inline_math, mark, insert) emits non-whitespace markup
        # that would glue to the role
        return True

    def inline_math(self, token: Dict[str, Any], state: BlockState) -> str:
        # docutils math role; a backtick inside the content would close the
        # role early, escape it
        raw = cast(str, token["raw"]).replace("`", "\\`")
        role = ":math:`" + raw + "`"
        # docutils only recognizes inline markup delimited by whitespace or
        # punctuation from a short allowed set; a role glued to neighboring
        # text is swallowed into it or not recognized at all. Mark the
        # boundary with an escaped space, which docutils drops from the
        # output, so "a$x$b" renders as a\ :math:`x`\ b and displays "axb".
        # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#character-level-inline-markup
        prefix = "\\ " if self.needs_role_boundary(token.get("prev"), "tail") else ""
        suffix = "\\ " if self.needs_role_boundary(token.get("next"), "head") else ""
        return prefix + role + suffix

    def block_math(self, token: Dict[str, Any], state: BlockState) -> str:
        lines = [".. math::", ""]
        lines.extend("   " + line for line in cast(str, token["raw"]).splitlines())
        return "\n".join(lines) + "\n\n"

    def mark(self, token: Dict[str, Any], state: BlockState) -> str:
        # reStructuredText has no native highlight; keep the text visible
        # with its original markers instead of failing
        return "==" + self.render_children(token, state) + "=="

    def insert(self, token: Dict[str, Any], state: BlockState) -> str:
        # reStructuredText has no native insertion/underline; keep the text
        # visible with its original markers instead of failing
        return "^^" + self.render_children(token, state) + "^^"

    def linebreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return "<linebreak>"

    def softbreak(self, token: Dict[str, Any], state: BlockState) -> str:
        return " "

    def inline_html(self, token: Dict[str, Any], state: BlockState) -> str:
        # rst does not support inline html
        return ""

    def paragraph(self, token: Dict[str, Any], state: BlockState) -> str:
        children = token["children"]
        if len(children) == 1 and children[0]["type"] == "image":
            image = children[0]
            attrs = image["attrs"]
            title = cast(str, attrs.get("title"))
            alt = self.render_children(image, state)
            text = ".. figure:: " + cast(str, attrs["url"])
            if title:
                text += "\n   :alt: " + title
            text += "\n\n" + indent(alt, "   ")
        else:
            text = self.render_tokens(children, state)
            lines = text.split("<linebreak>")
            if len(lines) > 1:
                text = "\n".join("| " + line for line in lines)
        return text + "\n\n"

    def heading(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token["attrs"]
        text = self.render_children(token, state)
        marker = self.HEADING_MARKERS[attrs["level"]]
        return text + "\n" + marker * len(text) + "\n\n"

    def thematic_break(self, token: Dict[str, Any], state: BlockState) -> str:
        return "--------------\n\n"

    def block_text(self, token: Dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        lines = text.split("<linebreak>")
        if len(lines) > 1:
            text = "\n".join("| " + line for line in lines)
        return text + "\n"

    def block_code(self, token: Dict[str, Any], state: BlockState) -> str:
        attrs = token.get("attrs", {})
        info = cast(str, attrs.get("info"))
        code = indent(cast(str, token["raw"]), "   ")
        if info:
            lang = info.split()[0]
            return ".. code:: " + lang + "\n\n" + code + "\n"
        else:
            return "::\n\n" + code + "\n\n"

    def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
        text = indent(self.render_children(token, state), "   ")
        prev = token.get("prev")
        ignore_blocks = (
            "paragraph",
            "block_text",
            "thematic_break",
            "linebreak",
            "heading",
        )
        if prev and prev["type"] not in ignore_blocks:
            text = "..\n\n" + text
        return text

    def block_html(self, token: Dict[str, Any], state: BlockState) -> str:
        raw = token["raw"]
        return ".. raw:: html\n\n" + indent(raw, "   ") + "\n\n"

    def block_error(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def list(self, token: Dict[str, Any], state: BlockState) -> str:
        return render_list(self, token, state)

    def list_item(self, token: Dict[str, Any], state: BlockState) -> str:
        return render_list_item(self, token, state)

    def task_list_item(self, token: Dict[str, Any], state: BlockState) -> str:
        checked = token.get("attrs", {}).get("checked")
        marker = "[x] " if checked else "[ ] "
        return render_list_item(self, token, state, marker)
