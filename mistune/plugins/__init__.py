from .extra import plugin_url, plugin_strikethrough
from .footnote import plugin_footnote
from .table import plugin_table


PLUGINS = {
    'url': plugin_url,
    'strikethrough': plugin_strikethrough,
    'footnote': plugin_footnote,
    'table': plugin_table,
}

__all__ = [
    'PLUGINS',
    'plugin_url', 'plugin_strikethrough',
    'plugin_footnote',
    'plugin_table',
]
