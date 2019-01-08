from .extra import plugin_url, plugin_strikethrough
from .footnote import plugin_footnote
from .table import plugin_table
from .directive import plugin_directive, PluginDirective

PLUGINS = {
    'url': plugin_url,
    'strikethrough': plugin_strikethrough,
    'footnote': plugin_footnote,
    'table': plugin_table,
    'directive': plugin_directive,
}

__all__ = [
    'PLUGINS', 'PluginDirective',
    'plugin_url', 'plugin_strikethrough',
    'plugin_footnote',
    'plugin_table',
    'plugin_directive',
]
