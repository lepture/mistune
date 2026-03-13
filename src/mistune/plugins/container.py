import re
from typing import TYPE_CHECKING, Any, Dict, Match, Optional

if TYPE_CHECKING:
    from ..block_parser import BlockParser
    from ..core import BaseRenderer, BlockState
    from ..markdown import Markdown

__all__ = ["plugin_container"]

CONTAINER_PATTERN = r"^ {0,3}(?P<container_marker>:{3,})(?P<container_space> +|$)(?P<container_info>.*?)(?:\n|$)"

SUPPORTED_CONTAINER_NAMES = {
    "info",
    "warning",
    "danger",
    "success",
    "note",
    "tip",
}


def parse_container(block: "BlockParser", m: Match[str], state: "BlockState") -> Optional[int]:
    marker = m.group("container_marker")
    info = m.group("container_info").strip()
    
    parts = info.split(None, 1)
    if parts:
        name = parts[0].lower()
        title = parts[1] if len(parts) > 1 else ""
    else:
        name = ""
        title = ""
    
    if name not in SUPPORTED_CONTAINER_NAMES:
        return None
    
    if not title:
        title = name.capitalize()
    
    marker_len = len(marker)
    _end = re.compile(r"^ {0,3}:{" + str(marker_len) + r",}[ \t]*(?:\n|$)", re.M)
    cursor_start = m.end()
    
    m2 = _end.search(state.src, cursor_start)
    if m2:
        content = state.src[cursor_start : m2.start()]
        end_pos = m2.end()
    else:
        content = state.src[cursor_start:]
        end_pos = state.cursor_max
    
    content = content.strip()
    
    child = state.child_state(content)
    block.parse(child)
    
    token = {
        "type": "container",
        "children": child.tokens,
        "attrs": {"name": name, "title": title},
    }
    state.append_token(token)
    return end_pos


def render_html_container(renderer: "BaseRenderer", text: str, name: str = "note", title: str = "", **attrs: Any) -> str:
    html = '<div class="container ' + name + '">\n'
    html += '<p class="container-title">' + title + '</p>\n'
    html += text
    html += '</div>\n'
    return html


def plugin_container(md: "Markdown") -> None:
    """A mistune plugin to support custom containers.

    Container syntax looks like:

    .. code-block:: text

        ::: warning Warning Title
        This is a warning message.
        :::

        ::: info
        This is an info message.
        :::

    :param md: Markdown instance
    """
    md.block.register("container", CONTAINER_PATTERN, parse_container, before="paragraph")
    
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("container", render_html_container)
