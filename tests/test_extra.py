import mistune


def test_escape():
    ret = mistune.markdown('<div>**foo**</div>', escape=True)
    assert '&gt;' in ret

    ret = mistune.markdown('this **foo** is <b>bold</b>', escape=True)
    assert '&gt;' in ret


def test_linebreak():
    ret = mistune.markdown('this **foo** \nis me')
    assert '<br>' not in ret

    ret = mistune.markdown('this **foo** \nis me', hard_wrap=True)
    assert '<br>' in ret


def test_safe_links():
    attack_vectors = (
        # "standard" javascript pseudo protocol
        ('javascript:alert`1`', ''),
        # bypass attempt
        ('jAvAsCrIpT:alert`1`', ''),
        # bypass with newline
        ('javasc\nript:alert`1`', ''),
        # javascript pseudo protocol with entities
        ('javascript&colon;alert`1`', 'javascript&amp;colon;alert`1`'),
        # javascript pseudo protocol with prefix (dangerous in Chrome)
        ('\x1Ajavascript:alert`1`', ''),
        # vbscript-URI (dangerous in Internet Explorer)
        ('vbscript:msgbox', ''),
        # breaking out of the attribute
        ('"<>', '&quot;&lt;&gt;'),
    )
    for vector, expected in attack_vectors:
        # image
        assert 'src="%s"' % expected in mistune.markdown('![atk](%s)' % vector)
        # link
        assert 'href="%s"' % expected in mistune.markdown('[atk](%s)' % vector)


def test_skip_style():
    ret = mistune.markdown(
        'foo\n<style>body{color:red}</style>', skip_style=True
    )
    assert ret == '<p>foo</p>\n'


def test_use_xhtml():
    ret = mistune.markdown('foo\n\n----\n\nbar')
    assert '<hr>' in ret
    ret = mistune.markdown('foo\n\n----\n\nbar', use_xhtml=True)
    assert '<hr />' in ret

    ret = mistune.markdown('foo  \nbar', use_xhtml=True)
    assert '<br />' in ret

    ret = mistune.markdown('![foo](bar "title")', use_xhtml=True)
    assert '<img src="bar" alt="foo" title="title" />' in ret


def test_parse_inline_html():
    ret = mistune.markdown(
        '<div>**foo**</div>', parse_inline_html=True, escape=False
    )
    assert '<strong>' not in ret
    ret = mistune.markdown(
        '<span>**foo**</span>', parse_inline_html=True, escape=False
    )
    assert '<span><strong>' in ret

    ret = mistune.markdown(
        '<span id="foo">**foo**</span>', parse_inline_html=True, escape=False
    )
    assert '<span id="foo"><strong>' in ret

    ret = mistune.markdown(
        '<span id=foo>**foo**</span>', parse_inline_html=True, escape=False
    )
    assert '<span id=foo><strong>' in ret

    ret = mistune.markdown(
        '<a>http://lepture.com</a>', parse_inline_html=True, escape=False
    )
    assert 'href' not in ret


def test_block_html():
    ret = mistune.markdown(
        '<div ></div>', escape=False
    )
    assert '<div ></div>' in ret


def test_parse_block_html():
    ret = mistune.markdown(
        '<div>**foo**</div>', parse_block_html=True, escape=False
    )
    assert '<div><strong>' in ret

    ret = mistune.markdown(
        '<div id="foo">**foo**</div>', parse_block_html=True, escape=False
    )
    assert '<div id="foo"><strong>' in ret

    ret = mistune.markdown(
        '<div id=foo>**foo**</div>', parse_block_html=True, escape=False
    )
    assert '<div id=foo><strong>' in ret

    ret = mistune.markdown(
        '<span>**foo**</span>', parse_block_html=True, escape=False
    )
    assert '<strong>' not in ret


def test_parse_nested_html():
    ret = mistune.markdown(
        '<div><a href="http://example.org">**foo**</a></div>',
        parse_block_html=True, escape=False
    )
    assert '<div><a href="http://example.org">' in ret
    assert '<strong>' not in ret

    ret = mistune.markdown(
        '<div><a href="http://example.org">**foo**</a></div>',
        parse_block_html=True, parse_inline_html=True, escape=False
    )
    assert '<div><a href="http://example.org"><strong>' in ret


def test_trigger_more_cases():
    markdown = mistune.Markdown(
        inline=mistune.InlineLexer,
        block=mistune.BlockLexer,
        skip_html=True
    )
    ret = markdown.render('foo[^foo]\n\n[^foo]: foo\n\n[^foo]: bar\n')
    assert 'bar' not in ret


def test_not_escape_block_tags():
    text = '<h1>heading</h1> text'
    assert text in mistune.markdown(text, escape=False)


def test_not_escape_inline_tags():
    text = '<a name="top"></a>'
    assert text in mistune.markdown(text, escape=False)
    # space between =
    text = '<span style = "color:red;">test</span>'
    assert text in mistune.markdown(text, escape=False)


def test_hard_wrap_renderer():
    text = 'foo\nnewline'
    renderer = mistune.Renderer(hard_wrap=True)
    func = mistune.Markdown(renderer=renderer)
    assert '<br>' in func(text)
