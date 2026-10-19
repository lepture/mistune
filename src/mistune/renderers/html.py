import re
from typing import Any, ClassVar, Dict, Iterable, Literal, Mapping, Optional, Tuple, Union
from urllib.parse import unquote

from ..core import BaseRenderer, BlockState
from ..util import escape as escape_text
from ..util import safe_entity, striptags


class HTMLRenderer(BaseRenderer):
    """A renderer for converting Markdown to HTML."""

    _escape: bool
    _allow_harmful_protocols: Optional[Union[bool, Iterable[str]]]
    NAME: ClassVar[Literal["html"]] = "html"
    SAFE_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "http:",
        "https:",
        "mailto:",
        "tel:",
        "ftp:",
        "ftps:",
        "irc:",
        "ircs:",
    )
    GOOD_DATA_PROTOCOLS: ClassVar[Tuple[str, ...]] = (
        "data:image/gif;",
        "data:image/png;",
        "data:image/jpeg;",
        "data:image/webp;",
    )
    _attribute_name_re = re.compile(r"^[A-Za-z_:][A-Za-z0-9_.:-]*$")

    def __init__(
        self,
        escape: bool = True,
        allow_harmful_protocols: Optional[Union[bool, Iterable[str]]] = None,
    ) -> None:
        super(HTMLRenderer, self).__init__()
        self._allow_harmful_protocols = allow_harmful_protocols
        self._escape = escape

    @property
    def escape_enabled(self) -> bool:
        """Whether raw HTML nodes are escaped."""
        return self._escape

    @escape_enabled.setter
    def escape_enabled(self, enabled: bool) -> None:
        self._escape = enabled

    def escape_raw(self, value: str) -> str:
        """Escape raw HTML when raw HTML output is disabled."""
        if self.escape_enabled:
            return escape_text(value)
        return value

    def escape_attribute(self, value: object) -> str:
        """Escape a value for use in a generated HTML attribute."""
        return safe_entity(str(value))

    def render_attrs(self, attrs: Mapping[str, object]) -> str:
        """Render generated HTML attributes with escaped values."""
        rendered = []
        for name, value in attrs.items():
            if not self._attribute_name_re.fullmatch(name):
                raise ValueError("invalid HTML attribute name: " + name)
            if value is None or value is False:
                continue
            if value is True:
                rendered.append(" " + name)
            else:
                rendered.append(' ' + name + '="' + self.escape_attribute(value) + '"')
        return "".join(rendered)

    def sanitize_url(self, url: str) -> str:
        """Return a URL allowed by this renderer's protocol policy."""
        allow_harmful_protocols = self._allow_harmful_protocols
        if allow_harmful_protocols is True:
            return url

        normalized_url = _unquote_url(url).lower().lstrip()
        if allow_harmful_protocols and normalized_url.startswith(tuple(allow_harmful_protocols)):
            return url

        if _is_safe_url(normalized_url, self.SAFE_PROTOCOLS, self.GOOD_DATA_PROTOCOLS):
            return url
        return "#harmful-link"

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
        return self.escape_attribute(self.sanitize_url(url))

    def text(self, text: str) -> str:
        if self.escape_enabled:
            return escape_text(text)
        return safe_entity(text)

    def emphasis(self, text: str) -> str:
        return "<em>" + text + "</em>"

    def strong(self, text: str) -> str:
        return "<strong>" + text + "</strong>"

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        attrs: Dict[str, object] = {"href": self.sanitize_url(url)}
        if title:
            attrs["title"] = title
        return "<a" + self.render_attrs(attrs) + ">" + text + "</a>"

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        alt = striptags(text)
        attrs: Dict[str, object] = {"src": self.sanitize_url(url), "alt": alt}
        if title:
            attrs["title"] = title
        return "<img" + self.render_attrs(attrs) + " />"

    def codespan(self, text: str) -> str:
        return "<code>" + escape_text(text) + "</code>"

    def linebreak(self) -> str:
        return "<br />\n"

    def softbreak(self) -> str:
        return "\n"

    def inline_html(self, html: str) -> str:
        return self.escape_raw(html)

    def paragraph(self, text: str) -> str:
        return "<p>" + text + "</p>\n"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        tag = "h" + str(level)
        _id = attrs.get("id")
        rendered_attrs = self.render_attrs({"id": _id}) if _id else ""
        return "<" + tag + rendered_attrs + ">" + text + "</" + tag + ">\n"

    def blank_line(self) -> str:
        return ""

    def thematic_break(self) -> str:
        return "<hr />\n"

    def block_text(self, text: str) -> str:
        return text

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        attrs: Dict[str, object] = {}
        if info is not None:
            info = safe_entity(info.strip())
        if info:
            lang = info.split(None, 1)[0]
            attrs["class"] = "language-" + lang
        return "<pre><code" + self.render_attrs(attrs) + ">" + escape_text(code) + "</code></pre>\n"

    def block_quote(self, text: str) -> str:
        return "<blockquote>\n" + text + "</blockquote>\n"

    def block_html(self, html: str) -> str:
        if self.escape_enabled:
            return "<p>" + self.escape_raw(html.strip()) + "</p>\n"
        return html + "\n"

    def block_error(self, text: str) -> str:
        return '<div class="error"><pre>' + escape_text(text) + "</pre></div>\n"

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        if ordered:
            start = attrs.get("start")
            return "<ol" + self.render_attrs({"start": start}) + ">\n" + text + "</ol>\n"
        return "<ul>\n" + text + "</ul>\n"

    def list_item(self, text: str) -> str:
        return "<li>" + text + "</li>\n"


def _unquote_url(url: str) -> str:
    for _ in range(3):
        decoded = unquote(url)
        if decoded == url:
            break
        url = decoded
    return url


def _is_safe_url(url: str, safe_protocols: Tuple[str, ...], good_data_protocols: Tuple[str, ...]) -> bool:
    if url.startswith(safe_protocols):
        return True
    if url.startswith(good_data_protocols):
        return True
    if url.startswith(("/", "#", "?")):
        return True
    return ":" not in url.split("/", 1)[0]
