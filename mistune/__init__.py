from .markdown import Markdown
from .block_parser import BlockParser
from .inline_parser import InlineParser
from .renderers import AstRenderer, HTMLRenderer
from .scanner import escape, escape_url, escape_html, unikey


html = Markdown(HTMLRenderer(escape=False))


def markdown(text, escape=True, renderer=None, plugins=None):
    if renderer is None or renderer == 'html':
        renderer = HTMLRenderer(escape=escape)
    elif renderer == 'ast':
        renderer = AstRenderer()

    md = Markdown(renderer, plugins=plugins)
    return md(text)


__all__ = [
    'Markdown', 'AstRenderer', 'HTMLRenderer',
    'BlockParser', 'InlineParser',
    'escape', 'escape_url', 'escape_html', 'unikey',
    'html', 'markdown',
]
__version__ = '2.0.0'
