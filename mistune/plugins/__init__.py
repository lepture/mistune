from .extra import plugin_url, plugin_strikethrough
from .footnote import plugin_footnote
from .table import plugin_table
from .directive import plugin_directive, PluginDirective
from .toc import plugin_toc, PluginToc


PLUGINS = {
    'url': plugin_url,
    'strikethrough': plugin_strikethrough,
    'footnote': plugin_footnote,
    'table': plugin_table,
    'directive': plugin_directive,
    'toc': plugin_toc,
}

__all__ = [
    'PLUGINS',
    'plugin_url', 'plugin_strikethrough',
    'plugin_footnote',
    'plugin_table',
    'plugin_directive', 'PluginDirective',
    'plugin_toc', 'PluginToc',
]
