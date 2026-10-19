Security model
==============

Mistune parses text supplied by its caller. Applications should choose a trust
mode deliberately and keep application resource controls outside the parser.

Safe defaults
-------------

``mistune.create_markdown()`` and ``mistune.HTMLRenderer()`` escape raw HTML
and reject unsafe URL schemes by default. Reuse the returned parser when
processing multiple documents::

    import mistune

    markdown = mistune.create_markdown()
    html = markdown(untrusted_markdown_text)

The global ``mistune.html`` object is a legacy convenience parser created with
``escape=False``. It permits raw HTML and must not process untrusted input
unless an external HTML sanitizer processes the rendered result.

Trust boundaries
----------------

``escape=True`` encodes raw HTML tokens. It is not a general HTML sanitizer,
and it does not replace application-level request-size limits, execution
isolation, or other resource controls. A custom renderer that deliberately
emits raw HTML establishes its own trust boundary.

HTML plugins and renderers should use the public helper matching each output
context:

* ``escape_raw`` for raw HTML tokens;
* ``escape_attribute`` for a single attribute value;
* ``render_attrs`` for generated, fixed-name attributes;
* ``sanitize_url`` before placing a URL in an attribute.

Do not treat ``escape=False`` as permission to skip attribute encoding or URL
filtering.

Extension performance
---------------------

Custom inline extensions may pass an exhaustive ``start_chars`` hint to
``InlineParser.register()``. Omitting the hint is correct and uses the combined
regular-expression scanner. An incomplete hint can skip valid matches, so
declare one only when every possible starting character is known.

Applications accepting untrusted documents should still set appropriate input
size and execution limits. Mistune does not impose a universal document-size
limit or interrupt parsing with a timeout.

Reporting vulnerabilities
-------------------------

Do not open a public issue for a suspected vulnerability. Follow the
repository's `security policy
<https://github.com/lepture/mistune/blob/main/.github/SECURITY.md>`_ to report it
privately.
