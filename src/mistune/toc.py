import re
from html import unescape
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple

from .core import BlockState
from .helpers import HTML_TAGNAME
from .util import escape, striptags

if TYPE_CHECKING:
    from .markdown import Markdown

_HTML_ID_RE = re.compile(r"""\bid\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
_HTML_TAG_START_RE = re.compile("<" + HTML_TAGNAME)
_HTML_ATTRIBUTE_RE = re.compile(
    r"""[ \t\r\n\f]+([^ \t\r\n\f"'/=<>]+)"""
    r"""(?:[ \t\r\n\f]*=[ \t\r\n\f]*(?:"[^"]*"|'[^']*'|([^ \t\r\n\f"'=<>`]+)))?"""
)


def _iter_html_tags(source: str) -> Iterator[str]:
    pos = 0
    while pos < len(source):
        start = source.find("<", pos)
        if start < 0:
            return
        pos = start + 1
        if pos == len(source) or not ("A" <= source[pos] <= "Z" or "a" <= source[pos] <= "z"):
            continue
        quote = ""
        while pos < len(source):
            char = source[pos]
            pos += 1
            if quote:
                if char == quote:
                    quote = ""
            elif char in "\"'":
                quote = char
            elif char == ">":
                yield source[start:pos]
                break
            elif char == "<":
                pos -= 1
                break


def _iter_unquoted_html_ids(source: str) -> Iterator[str]:
    for tag in _iter_html_tags(source):
        start = _HTML_TAG_START_RE.match(tag)
        assert start is not None
        pos = start.end()
        while True:
            attr = _HTML_ATTRIBUTE_RE.match(tag, pos)
            if attr is None:
                break
            pos = attr.end()
            if attr.group(1).lower() == "id" and attr.group(2) is not None:
                yield unescape(attr.group(2))


def add_toc_hook(
    md: "Markdown",
    min_level: int = 1,
    max_level: int = 3,
    heading_id: Optional[Callable[[Dict[str, Any], int], str]] = None,
) -> None:
    """Add a hook to save toc items into ``state.env``. This is
    usually helpful for doc generator::

        import mistune
        from mistune.toc import add_toc_hook, render_toc_ul

        md = mistune.create_markdown(...)
        add_toc_hook(md)

        html, state = md.parse(text)
        toc_items = state.env['toc_items']
        toc_html = render_toc_ul(toc_items)

    By default, generated heading IDs avoid collisions with IDs in raw HTML,
    including unquoted attribute values. IDs are conservatively reserved from
    the Markdown source, so literal HTML examples may also reserve an ID.

    :param md: Markdown instance
    :param min_level: min heading level
    :param max_level: max heading level
    :param heading_id: a function to generate heading_id
    """
    if heading_id is None:
        auto_heading_id = True

        def heading_id(token: Dict[str, Any], index: int) -> str:
            return "toc_" + str(index + 1)

    else:
        auto_heading_id = False

    def toc_hook(md: "Markdown", state: "BlockState") -> None:
        headings = []

        for tok in state.tokens:
            if tok["type"] == "heading":
                level = tok["attrs"]["level"]
                if min_level <= level <= max_level:
                    headings.append(tok)

        id_allocator = _HeadingIdAllocator(state, headings)
        toc_items = []
        for i, tok in enumerate(headings):
            if not tok["attrs"].get("id"):
                value = heading_id(tok, i)
                id_allocator.assign(tok, value, ensure_unique=auto_heading_id)
            toc_items.append(normalize_toc_item(md, tok, parent=state))

        # save items into state
        state.env["toc_items"] = toc_items

    md.before_render_hooks.append(toc_hook)


class _HeadingIdAllocator:
    def __init__(self, state: "BlockState", headings: Iterable[Dict[str, Any]]) -> None:
        self.used_ids: Set[str] = {m.group(1) or m.group(2) for m in _HTML_ID_RE.finditer(state.src)}
        self.used_ids.update(_iter_unquoted_html_ids(state.src))
        for token in headings:
            value = token.get("attrs", {}).get("id")
            if value:
                self.used_ids.add(value)

    def assign(self, token: Dict[str, Any], value: str, ensure_unique: bool = True) -> str:
        if ensure_unique:
            value = self._unique(value)
        self.used_ids.add(value)
        token["attrs"]["id"] = value
        return value

    def _unique(self, value: str) -> str:
        if value not in self.used_ids:
            return value

        index = 1
        while value + "_" + str(index) in self.used_ids:
            index += 1
        return value + "_" + str(index)


def normalize_toc_item(md: "Markdown", token: Dict[str, Any], parent: Optional[Any] = None) -> Tuple[int, str, str]:
    text = token["text"]
    tokens = md.inline(text, parent.env if parent else {})
    assert md.renderer is not None
    html = md.renderer(tokens, BlockState())
    text = striptags(html)
    attrs = token["attrs"]
    return attrs["level"], attrs["id"], text


def render_toc_ul(toc: Iterable[Tuple[int, str, str]]) -> str:
    """Render a <ul> table of content HTML. The param "toc" should
    be formatted into this structure::

        [
          (level, id, text),
        ]

    For example::

        [
          (1, 'toc-intro', 'Introduction'),
          (2, 'toc-install', 'Install'),
          (2, 'toc-upgrade', 'Upgrade'),
          (1, 'toc-license', 'License'),
        ]
    """
    if not toc:
        return ""

    s = ""
    levels: List[int] = []
    for level, k, text in toc:
        item = '<a href="#{}">{}</a>'.format(escape(k), text)
        if not levels:
            s += "<li>" + item
            levels.append(level)
        elif level == levels[-1]:
            s += "</li>\n<li>" + item
        elif level > levels[-1]:
            s += "\n<ul>\n<li>" + item
            levels.append(level)
        else:
            levels.pop()
            while levels:
                last_level = levels.pop()
                if level == last_level:
                    s += "</li>\n</ul>\n</li>\n<li>" + item
                    levels.append(level)
                    break
                elif level > last_level:
                    s += "</li>\n<li>" + item
                    levels.append(last_level)
                    levels.append(level)
                    break
                else:
                    s += "</li>\n</ul>\n"
            else:
                levels.append(level)
                s += "</li>\n<li>" + item

    while len(levels) > 1:
        s += "</li>\n</ul>\n"
        levels.pop()

    if not s:
        return ""
    return "<ul>\n" + s + "</li>\n</ul>\n"
