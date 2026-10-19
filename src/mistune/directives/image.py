import re
from typing import TYPE_CHECKING, Any, Dict, List, Match, Optional

from ..util import escape_url
from ._base import BaseDirective, DirectivePlugin

if TYPE_CHECKING:
    from ..block_parser import BlockParser
    from ..core import BlockState
    from ..markdown import Markdown
    from ..renderers.html import HTMLRenderer

__all__ = ["Image", "Figure"]

_num_re = re.compile(r"^\d+(?:\.\d+)?(?:px|ch|em|rem|ex|rex|vw|vh|%)?$")
_allowed_aligns = ["top", "middle", "bottom", "left", "center", "right"]


def _parse_attrs(options: Dict[str, Any]) -> Dict[str, Any]:
    attrs = {}
    if "alt" in options:
        attrs["alt"] = options["alt"]

    # validate align
    align = options.get("align")
    if align and align in _allowed_aligns:
        attrs["align"] = align

    height = options.get("height")
    width = options.get("width")
    if height and _num_re.fullmatch(height):
        attrs["height"] = height
    if width and _num_re.fullmatch(width):
        attrs["width"] = width
    if "target" in options:
        attrs["target"] = escape_url(options["target"])
    return attrs


class Image(DirectivePlugin):
    NAME = "image"

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        options = dict(self.parse_options(m))
        attrs = _parse_attrs(options)
        attrs["src"] = self.parse_title(m)
        return {"type": "block_image", "attrs": attrs}

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register(self.NAME, self.parse)
        assert md.renderer is not None
        if md.renderer.NAME == "html":
            md.renderer.register("block_image", render_block_image)


def render_block_image(
    self: "HTMLRenderer",
    src: str,
    alt: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    **attrs: Any,
) -> str:
    image_attrs: Dict[str, object] = {"src": self.sanitize_url(src)}
    style = ""
    if alt:
        image_attrs["alt"] = alt
    if width and _num_re.fullmatch(width):
        if width.isdigit():
            image_attrs["width"] = width
        else:
            style += "width:" + width + ";"
    if height and _num_re.fullmatch(height):
        if height.isdigit():
            image_attrs["height"] = height
        else:
            style += "height:" + height + ";"
    if style:
        image_attrs["style"] = style

    img = "<img" + self.render_attrs(image_attrs) + " />"

    _cls = "block-image"
    align = attrs.get("align")
    if align:
        _cls += " align-" + align

    target = attrs.get("target")
    if target:
        outer = "<a" + self.render_attrs({"class": _cls, "href": self.sanitize_url(target)}) + ">"
        return outer + img + "</a>\n"
    else:
        return "<div" + self.render_attrs({"class": _cls}) + ">" + img + "</div>\n"


class Figure(DirectivePlugin):
    NAME = "figure"

    def parse_directive_content(
        self, block: "BlockParser", m: Match[str], state: "BlockState"
    ) -> Optional[List[Dict[str, Any]]]:
        content = self.parse_content(m)
        if not content:
            return None

        tokens = list(self.parse_tokens(block, content, state))
        caption = tokens[0]
        if caption["type"] == "paragraph":
            caption["type"] = "figcaption"
            children = [caption]
            if len(tokens) > 1:
                children.append({"type": "legend", "children": tokens[1:]})
            return children
        return None

    def parse(self, block: "BlockParser", m: Match[str], state: "BlockState") -> Dict[str, Any]:
        options = dict(self.parse_options(m))
        image_attrs = _parse_attrs(options)
        image_attrs["src"] = self.parse_title(m)

        align = image_attrs.pop("align", None)
        fig_attrs = {}
        if align:
            fig_attrs["align"] = align
        figwidth = options.get("figwidth")
        if figwidth and _num_re.fullmatch(figwidth):
            fig_attrs["figwidth"] = figwidth
        if "figclass" in options:
            fig_attrs["figclass"] = options["figclass"]

        children = [{"type": "block_image", "attrs": image_attrs}]
        content = self.parse_directive_content(block, m, state)
        if content:
            children.extend(content)
        return {
            "type": "figure",
            "attrs": fig_attrs,
            "children": children,
        }

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register(self.NAME, self.parse)

        assert md.renderer is not None
        if md.renderer.NAME == "html":
            md.renderer.register("figure", render_figure)
            md.renderer.register("block_image", render_block_image)
            md.renderer.register("figcaption", render_figcaption)
            md.renderer.register("legend", render_legend)


def render_figure(
    self: "HTMLRenderer",
    text: str,
    align: Optional[str] = None,
    figwidth: Optional[str] = None,
    figclass: Optional[str] = None,
) -> str:
    _cls = "figure"
    if align:
        _cls += " align-" + align
    if figclass:
        _cls += " " + figclass

    figure_attrs: Dict[str, object] = {"class": _cls}
    if figwidth and _num_re.fullmatch(figwidth):
        figure_attrs["style"] = "width:" + figwidth
    return "<figure" + self.render_attrs(figure_attrs) + ">\n" + text + "</figure>\n"


def render_figcaption(self: Any, text: str) -> str:
    return "<figcaption>" + text + "</figcaption>\n"


def render_legend(self: Any, text: str) -> str:
    return '<div class="legend">\n' + text + "</div>\n"
