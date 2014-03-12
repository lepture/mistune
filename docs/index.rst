.. include:: ../README.rst

Developer Guide
---------------

Here is the API reference for mistune.

.. module:: mistune

.. autoclass:: Renderer
   :members:

.. autoclass:: Markdown
   :members:

.. autofunction:: markdown
.. autofunction:: escape

Changelog
----------

Here is the full history of mistune.

Version 0.2.0
~~~~~~~~~~~~~

Released on Mar. 12, 2014

* Use tuple instead of list for efficient
* Add ``line_match`` and ``line_started`` property on InlineLexer, via `#4`_

.. _`#4`: https://github.com/lepture/mistune/pull/4

Version 0.1.0
~~~~~~~~~~~~~

First preview release.
