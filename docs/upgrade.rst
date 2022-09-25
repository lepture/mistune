Upgrade Guide
=============


Upgrade from v2 to v3
---------------------

HTMLRenderer
~~~~~~~~~~~~

When customizing renderers, these methods' parameters are changed::


    -    link(self, link, text=None, title=None)
    +    link(self, text, url, title=None)

    -    image(self, src, alt="", title=None)
    +    image(self, alt, url, title=None)

    -    heading(self, text, level)
    +    heading(self, text, level, **attrs)

    -    list(self, text, ordered, level, start=None)
    +    list(self, text, ordered, **attrs)

    -    list_item(self, text, level)
    +    list_item(self, text, **attrs)

    -    table_cell(self, text, align=None, is_head=False)
    +    table_cell(self, text, align=None, head=False)

AstRenderer
~~~~~~~~~~~

There is no ``AstRenderer`` in v3, just pass ``None`` to ``create_markdown``::

    import mistune

    md = mistune.create_markdown(renderer=None)
    md('...markdown text...')

Plugins
~~~~~~~

Please check the built-in plugins to find out how to write a mistune plugin.

Directives
~~~~~~~~~~

Removed ``self.parse_options`` and ``self.parse_text`` methods on ``Directive``
class. Please check the source code to find out how to create a directive.
