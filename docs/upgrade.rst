Upgrade Guide
=============


Upgrade from v2 to v3
---------------------

HTMLRenderer
~~~~~~~~~~~~

When customizing renderers, these methods' parameters are changed:

.. code-block:: diff

    -    link(self, link, text=None, title=None)
    +    link(self, text, url, title=None)

    -    image(self, src, alt="", title=None)
    +    image(self, text, url, title=None)

    -    heading(self, text, level)
    +    heading(self, text, level, **attrs)

    -    list(self, text, ordered, level, start=None)
    +    list(self, text, ordered, **attrs)

    -    list_item(self, text, level)
    +    list_item(self, text)

    -    table_cell(self, text, align=None, is_head=False)
    +    table_cell(self, text, align=None, head=False)

For plugins:

.. code-block:: diff

    - abbr(self, key, definition)
    + abbr(self, text: str, title: str)

    - task_list_item(self, text: str, level: int, checked: bool)
    + task_list_item(self, text: str, checked: bool)

AstRenderer
~~~~~~~~~~~

There is no ``AstRenderer`` in v3, just pass ``None`` or ``'ast'`` to ``create_markdown``::

    import mistune

    md = mistune.create_markdown(renderer='ast') # or render=None
    md('...markdown text...')

Plugins
~~~~~~~

Please check the advanced guide and built-in plugins source code to find
out how to write a mistune plugin.

Directives
~~~~~~~~~~

Find out all the details in :ref:`directives`. In v3, there is one more
style of directive -- fenced style directive.
