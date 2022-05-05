from .markdown import Markdown
from .block_parser import BlockParser
from .inline_parser import InlineParser
from .renderers import HTMLRenderer
# from .plugins import PLUGINS
from .util import escape, escape_url, escape_html, unikey


def create_markdown(escape=True, hard_wrap=False, renderer=None, plugins=None):
    """Create a Markdown instance based on the given condition.

    :param escape: Boolean. If using html renderer, escape html.
    :param hard_wrap: Boolean. Break every new line into ``<br>``.
    :param renderer: renderer instance or string of ``html`` and ``ast``.
    :param plugins: List of plugins, string or callable.

    This method is used when you want to re-use a Markdown instance::

        markdown = create_markdown(
            escape=False,
            renderer='html',
            plugins=['url', 'strikethrough', 'footnotes', 'table'],
        )
        # re-use markdown function
        markdown('.... your text ...')
    """
    if renderer is None or renderer == 'html':
        renderer = HTMLRenderer(escape=escape)
    elif renderer == 'ast':
        renderer = None

    if plugins:
        _plugins = []
        for p in plugins:
            if isinstance(p, str):
                pass
                # _plugins.append(PLUGINS[p])
            else:
                _plugins.append(p)
        plugins = _plugins

    inline = InlineParser(renderer, hard_wrap=hard_wrap)
    return Markdown(renderer, inline=inline, plugins=plugins)


html = create_markdown(
    escape=False,
    renderer='html',
    # plugins=['strikethrough', 'footnotes', 'table'],
)


__cached_parsers = {}


def markdown(text, escape=True, renderer=None, plugins=None):
    key = (escape, renderer, plugins)
    if key in __cached_parsers:
        return __cached_parsers[key](text)

    md = create_markdown(escape=escape, renderer=renderer, plugins=plugins)
    # improve the speed for markdown parser creation
    __cached_parsers[key] = md
    return md(text)


__all__ = [
    'Markdown', 'HTMLRenderer',
    'BlockParser', 'InlineParser',
    'escape', 'escape_url', 'escape_html', 'unikey',
    'html', 'create_markdown', 'markdown',
]

__version__ = '2.0.2'
