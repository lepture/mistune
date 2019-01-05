# coding: utf-8

import mistune


def test_block_lexer():

    bl = mistune.BlockLexer()

    assert bl.default_rules is not mistune.BlockLexer.default_rules


def test_inline_lexer():

    r = mistune.Renderer()
    il = mistune.InlineLexer(r)

    assert il.default_rules is not mistune.InlineLexer.default_rules
    assert il.inline_html_rules is not mistune.InlineLexer.inline_html_rules
