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

    #: inline token types whose rendered output itself separates an
    #: adjacent inline role from anything beyond it: softbreak renders as
    #: a space, and the <linebreak> marker becomes a real line split
    #: before docutils parses the output. (inline_html also renders as
    #: nothing, but for the boundary check that means a role next to it
    #: touches the token beyond it, so needs_role_boundary walks past
    #: zero-output tokens like it instead.)
    ROLE_SAFE_NEIGHBORS = frozenset({"softbreak", "linebreak"})

    def iter_tokens(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> Iterable[str]:
        # ignore blank line
        tokens = [tok for tok in tokens if tok["type"] != "blank_line"]
        # link up the whole sibling list before rendering anything, so a
        # renderer can also walk past the current token (needs_role_boundary
        # looks beyond neighbors that emit no output, e.g. inline_html)
        for index, tok in enumerate(tokens):
            tok["prev"] = tokens[index - 1] if index else None
            tok["next"] = tokens[index + 1] if index + 1 < len(tokens) else None
        for tok in tokens:
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
    def token_emits_output(cls, token: Dict[str, Any]) -> bool:
        """Tell whether an inline token contributes text to the RST output.

        Only checked by the role-boundary logic: an ``inline_html`` token
        renders as nothing (rst has no inline html), so a role next to it
        actually touches whatever lies beyond it. A text token with empty
        raw also renders as nothing. Every other inline token emits
        non-empty output.
        """
        tok_type = token["type"]
        if tok_type == "inline_html":
            return False
        if tok_type == "text":
            return bool(cast(str, token["raw"]))
        return True

    @classmethod
    def needs_role_boundary(
        cls, token: Optional[Dict[str, Any]], edge: str
    ) -> bool:
        """Tell whether an inline role touching this neighbor needs an
        escaped-space boundary to stay recognizable by docutils.

        ``edge`` is the side of the neighbor facing the role: ``"tail"``
        for the preceding token, ``"head"`` for the following one.
        """
        while token is not None and not cls.token_emits_output(token):
            # a neighbor that emits no output vanishes from the RST, so
            # the role really touches the next token beyond it
            token = token.get("prev") if edge == "tail" else token.get("next")
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
