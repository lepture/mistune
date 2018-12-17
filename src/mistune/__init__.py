from .markdown import Markdown
from .renderers import AstRenderer, HTMLRenderer


def html(text, escape=False):
    renderer = HTMLRenderer(escape=escape)
    md = Markdown(renderer)
    return md(text)


__all__ = ['Markdown', 'AstRenderer', 'HTMLRenderer']
__version__ = '2.0.0'
