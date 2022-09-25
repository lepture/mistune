Command line tools
==================

A command line tool to convert markdown content into HTML, here
are some use cases of the command line tool:

    $ python -m mistune -m "Hi **Markdown**"
    <p>Hi <strong>Markdown</strong></p>

    $ python -m mistune -f README.md
    <p>...

Learn more about the options:

    $ python -m mistune -h
