from importlib import import_module
from typing import TYPE_CHECKING, Dict, Protocol, Union, cast

if TYPE_CHECKING:
    from ..markdown import Markdown

_plugins = {
    "speedup": "mistune.plugins.speedup.speedup",
    "strikethrough": "mistune.plugins.formatting.strikethrough",
    "mark": "mistune.plugins.formatting.mark",
    "insert": "mistune.plugins.formatting.insert",
    "superscript": "mistune.plugins.formatting.superscript",
    "subscript": "mistune.plugins.formatting.subscript",
    "footnotes": "mistune.plugins.footnotes.footnotes",
    "table": "mistune.plugins.table.table",
    "url": "mistune.plugins.url.url",
    "abbr": "mistune.plugins.abbr.abbr",
    "def_list": "mistune.plugins.def_list.def_list",
    "math": "mistune.plugins.math.math",
    "ruby": "mistune.plugins.ruby.ruby",
    "task_lists": "mistune.plugins.task_lists.task_lists",
    "spoiler": "mistune.plugins.spoiler.spoiler",
}


class Plugin(Protocol):
    def __call__(self, md: "Markdown") -> None: ...


_cached_modules: Dict[str, Plugin] = {}

PluginRef = Union[str, Plugin]  # reference to register a plugin


def import_plugin(name: PluginRef) -> Plugin:
    if callable(name):
        return name

    if name in _cached_modules:
        return _cached_modules[name]

    if name not in _plugins:
        # `name` used to be treated as an arbitrary dotted module path here,
        # so anyone able to influence the plugins list (e.g. from a config
        # file or an HTTP parameter) could import and call any importable
        # object, not just a real Markdown plugin. Nothing in the docs
        # documents that as a supported way to register a plugin, since a
        # custom plugin is meant to be passed as the callable itself, so
        # this path is just rejected outright now.
        raise ValueError(f"Unknown plugin: {name!r}")

    module_path, func_name = _plugins[name].rsplit(".", 1)
    module = import_module(module_path)
    plugin = cast(Plugin, getattr(module, func_name))
    _cached_modules[name] = plugin
    return plugin
