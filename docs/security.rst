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

Parser bounds and recovery
--------------------------

``BlockParser.max_nested_level`` and ``InlineParser.max_nested_level`` default
to 20. Inline containers share one budget: alternating images, emphasis, links,
and formatting plugins does not grant each syntax its own allowance. When
``Markdown`` creates a missing block or inline parser, it uses the supplied
parser's limit::

    from mistune import BlockParser, HTMLRenderer, Markdown

    markdown = Markdown(
        renderer=HTMLRenderer(),
        block=BlockParser(max_nested_level=12),
    )
    assert markdown.inline.max_nested_level == 12

The older inline settings ``max_emphasis_depth`` and ``max_image_depth`` are
aliases for the shared limit. Limits must be positive; they cannot disable
nesting bounds.

Link reference labels follow CommonMark's maximum of 999 source characters,
including backslashes used for escapes. Bare link destinations must have
balanced parentheses, bounded by the parser's nesting limit, and cannot
contain ASCII control characters. Parenthesized titles cannot contain an
unescaped opening parenthesis.

A failed candidate becomes ordinary text. Parsing resumes after the failed
marker, so later valid links, emphasis, and code spans remain recognizable.
Reaching a nesting limit does not turn the remainder of the document into
unparsed text.

Links use an opening-bracket stack. Code spans and inline extensions use
source-local indexes of closing delimiters; they do not retain parse-failure
caches across nested sources or documents. Inline HTML terminators use the
same scanner, so repeated unclosed comments do not repeatedly scan the
remaining document.

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
