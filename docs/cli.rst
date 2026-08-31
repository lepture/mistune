Command line tools
==================

.. meta::
    :description: How to use the command line tools of Mistune
        to convert Markdown to HTML, Markdown, and reStructuredText.

Mistune includes a command line tool. Use ``-h`` to show its options::

    $ python -m mistune -h

    Mistune, a sane and fast Python Markdown parser.

    Examples:

        $ python -m mistune -m "Hi **Markdown**"
        <p>Hi <strong>Markdown</strong></p>

        $ python -m mistune -f README.md
        <p>...

        $ cat README.md | python -m mistune
        <p>...

    options:
      -h, --help            show this help message and exit
      -m, --message MESSAGE
                            the Markdown message to convert
      -f, --file FILE       the Markdown file to convert
      -p, --plugin NAME [NAME ...]
                            specify a plugin to use
      --escape              enable the escape option
      --hardwrap            enable the hardwrap option
      -o, --output OUTPUT   write the rendered result into file
      -r, --renderer RENDERER
                            specify the output renderer
      --version             show program's version number and exit

Convert Markdown to HTML
------------------------

By default, the command line tool converts Markdown text to HTML::

    $ python -m mistune -f README.md

Convert Markdown to reStructuredText
------------------------------------

Mistune includes a reStructuredText renderer. Specify it with ``-r rst``::

    $ python -m mistune -f README.md -r rst

Reformat Markdown
-----------------

Use the Markdown renderer to reformat a Markdown file::

    $ python -m mistune -f README.md -r markdown -o README.md

This command reformats the text in ``README.md``.

UNIX Pipes
----------

The command line tool supports UNIX pipes. For example::

    $ echo "foo **bar**" | python -m mistune
