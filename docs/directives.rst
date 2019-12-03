Directives
==========

Directive is a special plugin which is inspired by reStructuredText. The
syntax is very powerful:

.. code-block:: text

    .. directive-name:: directive value
       :option-key: option value
       :option-key: option value

       full featured markdown text here

It was designed to be used by other plugins. There are three built-in
plugins based on directive.

Admonitions
-----------

.. code-block:: text

    .. warning::

       You are looking at the **dev** documentation. Check out our
       [stable](/stable/) documentation instead.

Admonitions contains a group of ``directive-name``:

.. code-block:: text

    attention  caution  danger  error
    hint  important  note  tip  warning

To enable admonitions::

    import mistune
    from mistune.plugins.directive import PluginDirective, PluginAdmonition

    # PluginDirective is required, and it should be before PluginAdmonition
    markdown = mistune.create_markdown(
        plugins=[PluginDirective(), PluginAdmonition()]
    )


TOC Plugin
----------

.. code-block:: text

    .. toc:: Table of Contents
       :depth: 3

TOC plugin is based on directive. It can add a table of contents section in
the documentation. Let's take an example:

.. code-block:: text

   Here is the first paragraph, and we put TOC below.

   .. toc::

   # H1 title

   ## H2 title

   # H1 title

The rendered HTML will show a TOC at the ``.. toc::`` position. To enable
TOC plugin::

    import mistune
    from mistune.plugins.directive import PluginDirective
    from mistune.plugins.toc import PluginToc

    # PluginDirective is required, and it should be before PluginToc
    markdown = mistune.create_markdown(
        plugins=[PluginDirective(), PluginToc()]
    )

Include
-------

.. code-block:: text

    .. include:: hello.md

``include`` is a powerful plugin for documentation generator. With this
plugin, we can embed contents from other files.
