from typing import Any, ClassVar, Dict, Optional, Tuple, Literal
from ..core import BaseRenderer, BlockState
from ..util import escape as escape_text
from ..util import safe_entity, striptags


class HTMLRenderer(BaseRenderer):
    """A renderer for converting Markdown to HTML."""

    _escape: bool
    NAME: ClassVar[Literal["html"]] = "html"
    HARMFUL_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "javascript:",
        "vbscript:",
        "file:",
        "data:",
    )
    GOOD_DATA_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "data:image/gif;",
        "data:image/png;",
        "data:image/jpeg;",
        "data:image/webp;",
    )

    def __init__(self, escape: bool = True, allow_harmful_protocols: Optional[bool] = None) -> None:
        super(HTMLRenderer, self).__init__()
        self._allow_harmful_protocols = allow_harmful_protocols
        self._escape = escape

    def render_token(self, token: Dict[str, Any], state: BlockState) -> str:
        # backward compitable with v2
        func = self._get_method(token["type"])
        attrs = token.get("attrs")

        if "raw" in token:
            text = token["raw"]
        elif "children" in token:
            text = self.render_tokens(token["children"], state)
        else:
            if attrs:
                return func(**attrs)
            else:
                return func()
        if attrs:
            return func(text, **attrs)
        else:
            return func(text)

    def safe_url(self, url: str) -> str:
        """Ensure the given URL is safe. This method is used for rendering
        links, images, and etc.
        """
        if self._allow_harmful_protocols is True:
            return escape_text(url)

        _url = url.lower()
        if self._allow_harmful_protocols and _url.startswith(tuple(self._allow_harmful_protocols)):
            return escape_text(url)

        if _url.startswith(self.HARMFUL_PROTOCOLS) and not _url.startswith(self.GOOD_DATA_PROTOCOLS):
            return "#harmful-link"
        return escape_text(url)

    def text(self, text: str) -> str:
        if self._escape:
            return escape_text(text)
        return safe_entity(text)

    def emphasis(self, text: str) -> str:
        return "<em>" + text + "</em>"

    def strong(self, text: str) -> str:
        return "<strong>" + text + "</strong>"

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        s = '<a href="' + self.safe_url(url) + '"'
        if title:
            s += ' title="' + safe_entity(title) + '"'
        return s + ">" + text + "</a>"

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        src = self.safe_url(url)
        alt = escape_text(striptags(text))
        s = '<img src="' + src + '" alt="' + alt + '"'
        if title:
            s += ' title="' + safe_entity(title) + '"'
        return s + " />"

    def codespan(self, text: str) -> str:
        return "<code>" + escape_text(text) + "</code>"

    def linebreak(self) -> str:
        return "<br />\n"

    def softbreak(self) -> str:
        return "\n"

    def inline_html(self, html: str) -> str:
        if self._escape:
            return escape_text(html)
        return html

    def paragraph(self, text: str) -> str:
        return "<p>" + text + "</p>\n"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        tag = "h" + str(level)
        html = "<" + tag
        _id = attrs.get("id")
        if _id:
            html += ' id="' + _id + '"'
        return html + ">" + text + "</" + tag + ">\n"

    def blank_line(self) -> str:
        return ""

    def thematic_break(self) -> str:
        return "<hr />\n"

    def block_text(self, text: str) -> str:
        return text

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        html = "<pre><code"
        if info is not None:
            info = safe_entity(info.strip())
        if info:
            lang = info.split(None, 1)[0]
            html += ' class="language-' + lang + '"'
        return html + ">" + escape_text(code) + "</code></pre>\n"

    def block_quote(self, text: str) -> str:
        return "<blockquote>\n" + text + "</blockquote>\n"

    def block_html(self, html: str) -> str:
        if self._escape:
            return "<p>" + escape_text(html.strip()) + "</p>\n"
        return html + "\n"

    def block_error(self, text: str) -> str:
        return '<div class="error"><pre>' + text + "</pre></div>\n"

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        if ordered:
            html = "<ol"
            start = attrs.get("start")
            if start is not None:
                html += ' start="' + str(start) + '"'
            return html + ">\n" + text + "</ol>\n"
        return "<ul>\n" + text + "</ul>\n"

    def list_item(self, text: str) -> str:
        return "<li>" + text + "</li>\n"

    def tabs(self, text: str, title: str = "", options: dict = None) -> str:
        """Render tabs container."""
        if options is None:
            options = {}
        tab_id = options.get('id', f"tabs-{hash(title)}")
        html = f'<div class="tabs-container" id="{tab_id}" data-tab-name="{title}">\n'
        if title:
            html += f'<div class="tabs-title">{title}</div>\n'
        html += '<div class="tabs-nav">\n'
        # Tab navigation will be generated by JavaScript based on code blocks
        html += '</div>\n'
        html += '<div class="tabs-content">\n'
        html += text
        html += '</div>\n'
        html += '</div>\n'
        return html

    def tip(self, text: str, title: str = "", options: dict = None) -> str:
        """Render tip container."""
        if options is None:
            options = {}
        tip_id = options.get('id', f"tip-{hash(title)}")
        html = f'<div class="tip-container" id="{tip_id}" data-tip-name="{title}">\n'
        if title:
            html += f'<div class="tip-title">{title}</div>\n'
        html += '<div class="tip-content">\n'
        html += text
        html += '</div>\n'
        html += '</div>\n'
        return html
