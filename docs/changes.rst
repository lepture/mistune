Changelog
=========

Here is the full history of mistune v3.

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
