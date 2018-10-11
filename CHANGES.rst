Changelog
----------

Here is the full history of mistune.

Version 0.8.4
~~~~~~~~~~~~~

Released on Oct. 11, 2018

* Support an escaped pipe char in a table cell. `#150`_
* Fix ordered and unordered list. `#152`_
* Fix spaces between = in HTML tags
* Add max_recursive_depth for list and blockquote.
* Fix fences code block.

.. _`#150`: https://github.com/lepture/mistune/pull/150
.. _`#152`: https://github.com/lepture/mistune/pull/152

Version 0.8.3
~~~~~~~~~~~~~

Relased on Dec. 04, 2017

* Fix nested html issue. `#137`_

.. _`#137`: https://github.com/lepture/mistune/pull/137


Version 0.8.2
~~~~~~~~~~~~~

Relased on Dec. 04, 2017

* Fix ``_keyify`` with lower case.


Version 0.8.1
~~~~~~~~~~~~~

Released on Nov. 07, 2017

* Security fix CVE-2017-16876, thanks Dawid Czarnecki

Version 0.8
~~~~~~~~~~~

Released on Oct. 26, 2017

* Remove non breaking spaces preprocessing
* Remove rev and rel attribute for footnotes
* Fix bypassing XSS vulnerability by junorouse

This version is strongly recommended, since it fixed
a security issue.

Version 0.7.4
~~~~~~~~~~~~~

Released on Mar. 14, 2017

* Fix escape_link method by Marcos Ojeda
* Handle block HTML with no content by David Baumgold
* Use expandtabs for tab
* Fix escape option for text renderer
* Fix HTML attribute regex pattern

Version 0.7.3
~~~~~~~~~~~~~

Released on Jun. 28, 2016

* Fix strikethrough regex
* Fix HTML attribute regex
* Fix close tag regex

Version 0.7.2
~~~~~~~~~~~~~

Released on Feb. 26, 2016

* Fix `hard_wrap` options on renderer.
* Fix emphasis regex pattern
* Fix base64 image link `#80`_.
* Fix link security per `#87`_.

.. _`#80`: https://github.com/lepture/mistune/issues/80
.. _`#87`: https://github.com/lepture/mistune/issues/87


Version 0.7.1
~~~~~~~~~~~~~

Released on Aug. 22, 2015

* Fix inline html when there is no content per `#71`_.

.. _`#71`: https://github.com/lepture/mistune/issues/71


Version 0.7
~~~~~~~~~~~

Released on Jul. 18, 2015

* Fix the breaking change in version 0.6 with options: **parse_inline_html** and **parse_block_html**
* Breaking change: remove **parse_html** option for explicit
* Change option **escape** default value to ``True`` for security reason


Version 0.6
~~~~~~~~~~~

Released on Jun. 17, 2015

* Breaking change on inline HTML, text in inline HTML will not be parsed per `#38`_.
* Replace **tag** renderer with **inline_html** for breaking change on inline HTML
* Double emphasis, emphasis, code, and strikethrough can contain one linebreak per `#48`_.
* Match autolinks that do not have / in their URI via `#53`_.
* A work around on link that contains ``)`` per `#46`_.
* Add ``<font>`` tag for inline tags per `#55`_.

.. _`#38`: https://github.com/lepture/mistune/issues/38
.. _`#46`: https://github.com/lepture/mistune/issues/46
.. _`#48`: https://github.com/lepture/mistune/issues/48
.. _`#53`: https://github.com/lepture/mistune/pull/53
.. _`#55`: https://github.com/lepture/mistune/issues/55


Version 0.5.1
~~~~~~~~~~~~~

Released on Mar. 10, 2015

* Fix a bug when list item is blank via `ipython#7929`_.
* Use python-wheels to build wheels for Mac.

.. _`ipython#7929`: https://github.com/ipython/ipython/issues/7929


Version 0.5
~~~~~~~~~~~

Released on Dec. 5, 2014. This release will break things.

* For custom lexers, **features** is replaced with **rules**.
* Refactor on function names and codes.
* Add a way to output the render tree via `#20`_.
* Fix emphasis and strikethrough regular expressions.

.. _`#20`: https://github.com/lepture/mistune/pull/20

Version 0.4.1
~~~~~~~~~~~~~

Released on Oct. 12, 2014

* Add option for parse markdown in block level html.
* Fix on lheading, any number of underline = or - will work.
* Patch for setup if Cython is available but no C compiler.

Version 0.4
~~~~~~~~~~~

Released on Aug. 14, 2014

* Bugfix. Use inspect to detect renderer class.
* Move all meth:`escape` to renderer. Use renderer to escape everything.
* A little changes in code style and parameter naming.
* Don't parse text in a block html, behave like sundown.

Version 0.3.1
~~~~~~~~~~~~~

Released on Jul. 31, 2014

* Fix in meth:`Renderer.block_code`, no need to add ``\n`` in ``<code>``.
* Trim whitespace of code in code span via `#15`_.

.. _`#15`: https://github.com/lepture/mistune/issues/15

Version 0.3
~~~~~~~~~~~

Released on Jun. 27, 2014

* Add ``<hr>`` in footnotes renderer
* Add hard_wrap configuration for GFM linebreaks.
* Add text renderer, via `#9`_.
* Define features for lexers available via `#11`_.

.. _`#9`: https://github.com/lepture/mistune/pull/9
.. _`#11`: https://github.com/lepture/mistune/pull/11

Version 0.2
~~~~~~~~~~~

Released on Mar. 12, 2014

* Use tuple instead of list for efficient
* Add ``line_match`` and ``line_started`` property on InlineLexer, via `#4`_

.. _`#4`: https://github.com/lepture/mistune/pull/4

Version 0.1
~~~~~~~~~~~

First preview release.
