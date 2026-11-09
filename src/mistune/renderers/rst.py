from textwrap import indent
from typing import Any, Dict, Iterable, List, cast

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

    def iter_tokens(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> Iterable[str]:
        prev = None
        for tok in tokens:
            # ignore blank line
            if tok["type"] == "blank_line":
                continue
            tok["prev"] = prev
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

    def strikethrough(self, token: Dict[str, Any], state: BlockState) -> str:
        # reStructuredText has no native strikethrough; keep the text
        # visible with its original markers instead of failing
        return "~~" + self.render_children(token, state) + "~~"

    def table(self, token: Dict[str, Any], state: BlockState) -> str:
        children = token["children"]
        head = children[0]
        body_rows = children[1]["children"] if len(children) > 1 else []
        lines = [".. list-table::"]
        if head["children"]:
            lines.append("   :header-rows: 1")
        lines.append("")
        head_first = True
        for cell in head["children"]:
            lines.append(self._list_table_cell(cell, state, head_first))
            head_first = False
        for row in body_rows:
            first = True
            for cell in row["children"]:
                lines.append(self._list_table_cell(cell, state, first))
                first = False
        return "\n".join(lines) + "\n\n"

    def _list_table_cell(self, token: Dict[str, Any], state: BlockState, first: bool) -> str:
        text = self.render_children(token, state).replace("<linebreak>", " ").strip()
        return ("   * - " if first else "     - ") + text

    def table_head(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def table_body(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def table_row(self, token: Dict[str, Any], state: BlockState) -> str:
        return ""

    def table_cell(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state)

    def footnote_ref(self, token: Dict[str, Any], state: BlockState) -> str:
        return "[#" + cast(str, token["raw"]) + "]_"

    def footnotes(self, token: Dict[str, Any], state: BlockState) -> str:
        return "\n" + self.render_children(token, state)

    def footnote_item(self, token: Dict[str, Any], state: BlockState) -> str:
        key = cast(str, token["attrs"]["key"])
        text = self.render_children(token, state).rstrip("\n")
        first, *rest = text.splitlines()
        item = ".. [#" + key + "] " + first
        if rest:
            item += "\n" + "\n".join("   " + line for line in rest)
        return item + "\n"

    def def_list(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state) + "\n\n"

    def def_list_head(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_children(token, state) + "\n"

    def def_list_item(self, token: Dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state).rstrip("\n")
        return indent(text, "    ") + "\n"
