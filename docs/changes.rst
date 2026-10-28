Changelog
=========

Here is the full history of mistune v3.

Unreleased
----------

* Accept empty command-line messages and piped documents without falling back
  to another input source or reporting missing input.
* Use the language name from the fence info string in the Pygments renderer
  example, allowing additional metadata after it.
* Require Python 3.11 or later; remove Python 3.10 support.
* Remove the ``typing-extensions`` runtime dependency and use ``typing.Self``
  from the standard library.

Version 3.4.0
-------------

**Released on Oct 19, 2026**

* Add Python 3.15 support and include it in the CI test matrix.
* Require Python 3.10 or later.
* Parse inline links with an opening-bracket stack and replace per-syntax
  failure caches with source-local delimiter scanning.
* Share one inline nesting budget across images, links, emphasis, and plugins.
  Expose ``InlineParser.max_nested_level``; the older ``max_emphasis_depth``
  and ``max_image_depth`` settings configure the same limit.
* Preserve later valid syntax when a candidate fails or reaches a nesting
  limit, rather than treating the remaining input as unparsed text.
* Enforce CommonMark's 999-character reference label limit, balanced and
  bounded destination parentheses, and link title constraints.
* Improve performance for unclosed inline HTML, unmatched code delimiters,
  deeply nested images, and repeated text fragments.
* Recognize inline HTML comments permitted by CommonMark 0.31.2.
* Parse links containing full reference images without treating the image's
  reference label as a nested link.
* Preserve reference definitions parsed inside multi-paragraph footnotes.
* Accept definition-list markers indented by up to three spaces.
* Prefer longer registered abbreviation matches over shorter prefixes.
* Require at least one digit in ordered list continuation markers.
* Add Markdown rendering for strikethrough, mark, and insert plugins.
* Preserve escaped pipes in table code spans, literal trailing heading hashes,
  meaningful code span edge spaces, and leading blank lines in Markdown output.
* Keep images whose alt text matches their URL from becoming autolinks.
* Preserve non-line-break separator characters in rendered lists and hard line
  breaks in tight ReST list items.
* Document per-document renderer context and correct the custom Markdown
  renderer example.
* Preserve literal backslashes, image introducers, HTML delimiters and entity
  prefixes when rendering Markdown for a round trip.
* Only recognize task list markers in a list item's leading paragraph,
  preserving literal markers in headings.
* Bound the global convenience-parser cache and avoid retaining caller-owned
  renderers and plugin objects.
* Add public HTML output helpers for raw HTML, attributes, and URL policy.
* Share collision-safe default heading IDs between both TOC APIs.
* Add explicit start-character hints for custom inline rules; unhinted custom
  rules now use the correctness-first regular-expression scanner.
* Consolidate adversarial parser growth tests and document the security model.

Version 3.3.4
-------------

**Released on Jul 22, 2026**

* Harden inline parsing against deeply nested and adversarial link, image,
  emphasis, formatting, math, and reference inputs.
* Improve performance for repeated link suffixes, dense emphasis, unclosed
  formatting markers, inline spoilers, and adjacent ruby tokens.
* Refactor the inline parser into dedicated emphasis and link modules.
* Escape literal ``*``/``_`` emphasis markers in the Markdown renderer so
  round-tripping escaped text does not re-introduce emphasis.

Version 3.3.3
-------------

**Released on Jul 9, 2026**

* Limit deeply nested emphasis and image parsing to avoid ``RecursionError``.
* Fix repeated link suffix and unclosed formatting marker performance issues.
* Fix unclosed inline spoiler performance issues.
* Avoid recursive parsing for adjacent ruby tokens.
* Speed up footnote reference indexing.

Version 3.3.2
-------------

**Released on Jun 23, 2026**

* Fix Python 3.8 import compatibility in the inline parser.
* Fix mypy compatibility for list parsing on Python 3.8 and 3.9+.

Version 3.3.1
-------------

**Released on Jun 22, 2026**

* Fix ``abbr`` plugin compatibility with escaped inline text.
* Normalize included Markdown line endings before parsing directives.

Version 3.3.0
-------------

**Released on Jun 21, 2026**

* Improve CommonMark compatibility and parser performance.
* Add command line entrypoint with UTF-8 output.
* Support display and backtick math.
* Render plugin list and table nodes in Markdown renderer.
* Escape leading block markers in Markdown renderer.
* Fix RST renderer for block quotes nested in lists.
* Avoid generated heading ID collisions in TOC.
* Harden URL, image, figure, and include directive handling.
* Fix quadratic scans in inline links, reference links, and formatting markers.
* Fix math escaping, currency pattern matching, and cross-line matching.

Version 3.2.1
-------------

**Released on May 3, 2026**

* Escape link in ``render_toc_ul``.
* Escape text in math plugin.
* Fix regex for math plugin.
* Escape heading's ID attribute.
* Fix ``LINK_TITLE_RE`` to prevent DoS.
* Escape class attribute for admonition directive.
* Remove double-encoding of image alt text.
* Escape class attribute for image directive.
* Fix width/height attribute for image directive.

Version 3.2.0
-------------

**Released on Dec 23, 2025**

* Announce supports for python 3.14
* Fix footnotes plugins for code blocks, ref links, blockquote and etc.
* Fix ref links in TOC.

Version 3.1.4
-------------

**Released on Aug 29, 2025**

* Add fenced directive break rule in list parser.
* Prevent removing unicode whitespace when parsing atx heading.

Version 3.1.3
-------------

**Released on Mar 19, 2025**

* Announce supports for python 3.12 and 3.13

Version 3.1.2
-------------

**Released on Feb 19, 2025**

* Fix ``footnotes`` plugin for AST renderer

Version 3.1.1
-------------

**Released on Jan 28, 2025**

* Fix ``render_toc_ul`` method for empty iterable
* Fix ruby plugin's regex pattern and HTML rendering

Version 3.1.0
-------------

**Released on Dec 30, 2024**

* Fix only HTML-escape URLs when rendering to HTML
* Add block_quote prefix on empty lines too

Version 3.0.2
-------------

**Released on Sep 30, 2023**

* Fix list parser to avoid RecursionError

Version 3.0.1
-------------

**Released on Jun 10, 2023**

* Add ``py.typed`` for mypy
* Add ``tests``, ``docs`` for sdist
* Support ``renderer="ast"`` for rendering AST

Version 3.0.0
-------------

**Released on Jun 08, 2023**

* Do not strip leading unicode spaces like emsp
* Ensure new line at end of the text

Version 3.0.0rc5
----------------

**Released on Mar 22, 2023**

* Fix fenced directives
* Fix inline link parser
* Fix block math plugin for multiple lines
* Fix empty list item for markdown renderer

Version 3.0.0rc4
----------------

**Released on Nov 30, 2022**

* Fix plugin footnotes when there is no newline at the end
* Move safe HTML entities to HTMLRenderer
* Redesign directives parsing
* Add Image and Figure directive

Version 3.0.0rc3
----------------

**Released on Nov 25, 2022**

* Render inline math with ``\(`` and ``\)``
* Added ``RSTRenderer``, and ``MarkdownRenderer``
* Fix ``toc_hook`` method
* **Breaking change**, rename ``RstDirective`` to ``RSTDirective``

Version 3.0.0rc2
----------------

**Released on Nov 6, 2022**

* Add **spoiler** plugin
* Add ``collapse`` option for ``TableOfContents`` directive
* **Breaking change** on directive design, added fenced directive

Version 3.0.0rc1
----------------

**Released on Sep 26, 2022**

* Add **superscript** plugin

Version 3.0.0a3
---------------

**Released on Jul 14, 2022**

* Fix ruby plugin
* Change toc parameter ``depth`` to ``level``

Version 3.0.0a2
---------------

**Released on Jul 13, 2022**

* Escape block code in HTMLRenderer
* Fix parsing links

Version 3.0.0a1
---------------

**Released on Jul 12, 2022**

This is the first release of v3. Features included:

* redesigned mistune
* plugins
* directives
