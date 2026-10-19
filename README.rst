Mistune v3
==========

A fast yet powerful Python Markdown parser with renderers and plugins.

Overview
--------

Convert Markdown to HTML with ease:

.. code-block:: python

    import mistune

    markdown = mistune.create_markdown()
    markdown(your_markdown_text)

``create_markdown()`` escapes raw HTML by default. The legacy
``mistune.html(trusted_markdown_text)`` helper enables raw HTML and several
plugins; use it only for trusted input or sanitize its output externally.

Useful Links
------------

1. GitHub: https://github.com/lepture/mistune
2. Docs: https://mistune.lepture.com/

License
-------

Mistune is licensed under BSD. Please see LICENSE for licensing details.
