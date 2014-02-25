Mistune (WIP)
=============

Yet another markdown parser, inspired by marked_ in JavaScript.

.. image:: https://travis-ci.org/lepture/mistune.png?branch=master
   :target: https://travis-ci.org/lepture/mistune
.. image:: https://coveralls.io/repos/lepture/mistune/badge.png?branch=master
   :target: https://coveralls.io/r/lepture/mistune


.. _marked: https://github.com/chjj/marked


Features
--------

* Pure Python. Tested in Python 2.6+, Python 3.3+ and PyPy.
* Very fast. It is the top one in all other **pure Python** markdown parsers.
* Advanced features. Table, footnotes, autolink, fenced code etc.

View the `benchmark results <https://github.com/lepture/mistune/issues/1>`_.

Installation
------------

Installing mistune with pip::

    $ pip install mistune

If pip is not available, try easy_install::

    $ easy_install mistune

Cython Feature
~~~~~~~~~~~~~~

Mistune can be faster, if you compile with cython::

    $ pip install cython mistune


Quick Start
-----------

A simple API that render a markdown formatted text::

    import mistune

    mistune.markdown('I am using **markdown**')
    # output: <p>I am using <strong>markdown</strong></p>


Mistune doesn't enable all features by default. You can enable them::

    features = [
        'table', 'fenced_code', 'footnotes',
        'autolink', 'strikethrough',
    ]

    mistune.markdown(text, features=features)
