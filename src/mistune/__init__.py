"""
mistune
~~~~~~~

A fast yet powerful Python Markdown parser with renderers and
plugins, compatible with CommonMark 0.31.2.

Documentation: https://mistune.lepture.com/
"""

from functools import lru_cache
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple, Union

from .block_parser import BlockParser
from .core import BaseRenderer, BlockState, InlineState
from .inline_parser import InlineParser
from .markdown import Markdown
from .plugins import Plugin, PluginRef, import_plugin
from .renderers.html import HTMLRenderer
from .util import escape, escape_url, safe_entity, unikey

RendererRef = Union[Literal["html", "ast"], BaseRenderer]


def create_markdown(
    escape: Optional[bool] = None,
    hard_wrap: bool = False,
    renderer: Optional[RendererRef] = "html",
    plugins: Optional[Iterable[PluginRef]] = None,
) -> Markdown:
    """Create a Markdown instance based on the given condition.

    :param escape: Boolean. If using html renderer, escape html. When it is
        ``None``, the renderer keeps its own escape setting.
    :param hard_wrap: Boolean. Break every new line into ``<br>``.
    :param renderer: renderer instance, default is HTMLRenderer.
    :param plugins: List of plugins.

    This method is used when you want to re-use a Markdown instance::

        markdown = create_markdown(
            escape=False,
            hard_wrap=True,
        )
        # re-use markdown function
        markdown('.... your text ...')
    """
    if renderer == "ast":
        # explicit and more similar to 2.x's API
        renderer = None
    elif renderer == "html":
        renderer = HTMLRenderer(escape=True if escape is None else escape)
    elif escape is not None and isinstance(renderer, HTMLRenderer):
        # a renderer instance was given, honor the explicit escape flag
        renderer.escape_enabled = escape

    inline = InlineParser(hard_wrap=hard_wrap)
    real_plugins: Optional[Iterable[Plugin]] = None
    if plugins is not None:
        real_plugins = [import_plugin(n) for n in plugins if n != "speedup"]
    return Markdown(renderer=renderer, inline=inline, plugins=real_plugins)


html: Markdown = create_markdown(escape=False, plugins=["strikethrough", "footnotes", "table"])


_BuiltinRendererRef = Optional[Literal["html", "ast"]]


@lru_cache(maxsize=128)
def _cached_markdown(escape: bool, renderer: _BuiltinRendererRef, plugins: Tuple[str, ...]) -> Markdown:
    return create_markdown(escape=escape, renderer=renderer, plugins=plugins)


def markdown(
    text: str,
    escape: bool = True,
    renderer: Optional[RendererRef] = "html",
    plugins: Optional[Iterable[Any]] = None,
) -> Union[str, List[Dict[str, Any]]]:
    plugin_refs = tuple(plugins) if plugins is not None else ()
    if (renderer is None or (isinstance(renderer, str) and renderer in ("html", "ast"))) and all(
        isinstance(plugin, str) for plugin in plugin_refs
    ):
        md = _cached_markdown(escape, renderer, plugin_refs)
    else:
        md = create_markdown(escape=escape, renderer=renderer, plugins=plugin_refs)
    return md(text)


__all__ = [
    "Markdown",
    "HTMLRenderer",
    "BlockParser",
    "BlockState",
    "BaseRenderer",
    "InlineParser",
    "InlineState",
    "escape",
    "escape_url",
    "safe_entity",
    "unikey",
    "html",
    "create_markdown",
    "markdown",
]

__version__ = "3.4.0"
__homepage__ = "https://mistune.lepture.com/"
