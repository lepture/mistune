Command line tools
==================

.. meta::
    :description: How to use the command line tools of Mistune
        to convert Markdown to HTML, RST, and etc.

A command line tool to convert markdown content into HTML, learn
about the options of the command line tool::

    $ python -m mistune -h

    Mistune, a sane and fast python markdown parser.

    Here are some use cases of the command line tool:

        $ python -m mistune -m "Hi **Markdown**"
        <p>Hi <strong>Markdown</strong></p>

        $ python -m mistune -f README.md
        <p>...

        $ cat README.md | python -m mistune
        <p>...

    optional arguments:
      -h, --help            show this help message and exit
      -m MESSAGE, --message MESSAGE
                            the markdown message to convert
      -f FILE, --file FILE  the markdown file to convert
      -p NAME [NAME ...], --plugin NAME [NAME ...]
                            specifiy a plugin to use
      --escape              turn on escape option
      --hardwrap            turn on hardwrap option
      -o OUTPUT, --output OUTPUT
                            write the rendered result into file
      -r RENDERER, --renderer RENDERER
                            specify the output renderer
      --version             show program's version number and exit

Convert Markdown to HTML
------------------------

By default, the command line tool of mistune will convert markdown text
to HTML text::

    $ python -m mistune -f README.md

Convert Markdown to RestructuredText
------------------------------------

Mistune has a built-in RestructuredText formatter, specify the renderer
with ``-r rst``::

    $ python -m mistune -f README.md -r rst

Reformat Markdown
-----------------

You can reformat the markdown file with a markdown renderer::

    $ python -m mistune -f README.md -r markdown -o README.md

This command will reformat the text in ``README.md``.

Unix PIPE
---------

The command line tool supports unix PIPE. For instance::

    $ echo "foo **bar**" | python -m mistune
