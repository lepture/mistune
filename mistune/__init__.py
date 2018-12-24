from .markdown import Markdown
from .renderers import AstRenderer, HTMLRenderer


html = Markdown(HTMLRenderer(escape=False))


def markdown(text, escape=True, renderer=None, plugins=None):
    if renderer is None or renderer == 'html':
        renderer = HTMLRenderer(escape=escape)
    elif renderer == 'ast':
        renderer = AstRenderer()

    md = Markdown(renderer)
    if plugins:
        for plugin in plugins:
            md.use(plugin)
    return md(text)


__all__ = ['Markdown', 'AstRenderer', 'HTMLRenderer', 'html', 'markdown']
__version__ = '2.0.0'
