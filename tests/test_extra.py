import os
import sys
import base64

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


def test_ie_get_http3():
    ie = mistune._ImageEmbedder()

    if sys.version_info[0] == 3:
        ie._get_http3()
    else:
        try:
            ie._get_http3()
        except ImportError:
            pass
        else:
            raise Exception("Expected an exception for Python3 support under Python2.")


def test_ie_get_http2():
    ie = mistune._ImageEmbedder()

    if sys.version_info[0] == 2:
        ie._get_http2()
    else:
        try:
            ie._get_http2()
        except ImportError:
            pass
        else:
            raise Exception("Expected an exception for Python2 support.")


def test_ie_http():
    ie = mistune._ImageEmbedder()

    def fake_get_http2():
        def fake_http(url):
            return 'faker2', 'content_type'

        return fake_http

    ie._get_http2 = fake_get_http2

    def fake_get_http3():
        def fake_http(url):
            return 'faker3', 'content_type'

        return fake_http

    ie._get_http3 = fake_get_http3

    content, content_type = ie._http('http://aa.bb')

    if sys.version_info[0] == 2:
        assert content == 'faker2'
    elif sys.version_info[0] == 3:
        assert content == 'faker3'

    assert content_type == 'content_type'


def test_ie_http__instance_cached():
    ie = mistune._ImageEmbedder()
    ie._http_requestor = lambda x: ('test_data', 'content-type')

    content, content_type = ie._http('http://host/image')

    assert content == 'test_data'
    assert content_type == 'content-type'


def test_ie_embed_images_url():
    def return_image(self, url):
        return 'png_data', 'image/png'

    old_function = mistune._ImageEmbedder._get_base64_with_image_url
    mistune._ImageEmbedder._get_base64_with_image_url = return_image

    try:
        renderer = mistune.Renderer(embed_images=True)
        func = mistune.Markdown(renderer=renderer)

        markdown = """\
![alt text](https://some.domain/some_image.png)"""

        ret = func.render(markdown)

        assert '<p><img src="data:image/png;base64,png_data" alt="alt text"></p>\n' == ret
    finally:
        mistune._ImageEmbedder._get_base64_with_image_url = old_function


def test_ie_embed_images_local():
    renderer = mistune.Renderer(embed_local_images=True)
    func = mistune.Markdown(renderer=renderer)

    filepath = os.path.join(os.path.dirname(__file__), 'image.png')
    markdown = "![alt text]({filepath})".format(filepath=filepath)

    actual = func.render(markdown)

    expected = '<p><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAY1BMVEX///8AAADy8vLDw8OGhoYJCQnf398EBAQdHR3s7OwPDw/7+/uioqIkJCQnJye6urrJyckbGxtlZWWwsLBvb29BQUE6Ojrk5OR+fn4WFhYvLy/W1tZqampVVVV4eHiUlJQ1NTVSAT8kAAABJ0lEQVR4nO3XWXKDMBBFUZpBgJjBgDGe9r/K2EkqcRHpL9VUKvds4D0EtKQgAAAAAAAAAAAA+NPC2Zg53Cs9Hw5jnWXV1Jdmj/jbPZFPaX1UrxCNqbw6DYVqfpnJho01G5TLNl8kUWwQ/Xj+9walVn4+uvJFqlWpwC11F5CzzkvI75586XSWYEh8BSRWKXDw5suoMZZDzyf4lGkMxLn2F7CtQgHjHAIfkuY/FJirnV9BOPkLdCq7cu8vMKmcjkrfJBa5auQHxvsf2kilQHD0FbgonQjMyZ2/KC3AYzuyrvxUZyt6KmLXhtgrXhAcDdI+18t/NCg383CJtS9I6/nlZGwvat/ft2KNx8wmie2ma6R7K/kSmrZpWrPb7RQAAAAAAAAAAOBXvAGvzwnuz+x0kQAAAABJRU5ErkJggg==" alt="alt text"></p>\n'

    if actual != expected:
        raise Exception("Local image not embedded properly:\nACTUAL:\n=======\n{}\n\nEXPECTED:\n=========\n{}\n".format(actual, expected))


def test_ie_get_base64_with_image_filepath():
    ie = mistune._ImageEmbedder()

    filepath = os.path.join(os.path.dirname(__file__), 'image.png')
    content, content_type = ie._get_base64_with_image_filepath(filepath)

    expected = "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAY1BMVEX///8AAADy8vLDw8OGhoYJCQnf398EBAQdHR3s7OwPDw/7+/uioqIkJCQnJye6urrJyckbGxtlZWWwsLBvb29BQUE6Ojrk5OR+fn4WFhYvLy/W1tZqampVVVV4eHiUlJQ1NTVSAT8kAAABJ0lEQVR4nO3XWXKDMBBFUZpBgJjBgDGe9r/K2EkqcRHpL9VUKvds4D0EtKQgAAAAAAAAAAAA+NPC2Zg53Cs9Hw5jnWXV1Jdmj/jbPZFPaX1UrxCNqbw6DYVqfpnJho01G5TLNl8kUWwQ/Xj+9walVn4+uvJFqlWpwC11F5CzzkvI75586XSWYEh8BSRWKXDw5suoMZZDzyf4lGkMxLn2F7CtQgHjHAIfkuY/FJirnV9BOPkLdCq7cu8vMKmcjkrfJBa5auQHxvsf2kilQHD0FbgonQjMyZ2/KC3AYzuyrvxUZyt6KmLXhtgrXhAcDdI+18t/NCg383CJtS9I6/nlZGwvat/ft2KNx8wmie2ma6R7K/kSmrZpWrPb7RQAAAAAAAAAAOBXvAGvzwnuz+x0kQAAAABJRU5ErkJggg=="
    assert content == expected

    assert content_type == 'image/png'


def test_ie_get_base64_with_image_url():
    ie = mistune._ImageEmbedder()

    ie._http = lambda x: (b'image-content', 'image-type')

    encoded, content_type = ie._get_base64_with_image_url('http://host/image')

    content = base64.b64decode(encoded)

    expected = b'image-content'
    assert content == expected

    assert content_type == 'image-type'


def test_ie_get_embedded_image_url():
    ie = mistune._ImageEmbedder()

    ie._http = lambda x: (b'image-content', 'image-type')

    content = ie.get_embedded_image('http://aa.com/image')

    expected = '<img src="data:image-type;base64,aW1hZ2UtY29udGVudA==">'

    assert content == expected


def test_ie_get_embedded_image_url__xhtml():
    ie = mistune._ImageEmbedder()

    ie._http = lambda x: (b'image-content', 'image-type')

    content = ie.get_embedded_image('http://aa.com/image', use_xhtml=True)

    expected = '<img src="data:image-type;base64,aW1hZ2UtY29udGVudA==" />'

    assert content == expected


def test_ie_get_embedded_image_filepath():
    ie = mistune._ImageEmbedder()

    filepath = os.path.join(os.path.dirname(__file__), 'image.png')
    content = ie.get_embedded_image(filepath, allow_local=True)

    expected = """\
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAY1BMVEX///8AAADy8vLDw8OGhoYJCQnf398EBAQdHR3s7OwPDw/7+/uioqIkJCQnJye6urrJyckbGxtlZWWwsLBvb29BQUE6Ojrk5OR+fn4WFhYvLy/W1tZqampVVVV4eHiUlJQ1NTVSAT8kAAABJ0lEQVR4nO3XWXKDMBBFUZpBgJjBgDGe9r/K2EkqcRHpL9VUKvds4D0EtKQgAAAAAAAAAAAA+NPC2Zg53Cs9Hw5jnWXV1Jdmj/jbPZFPaX1UrxCNqbw6DYVqfpnJho01G5TLNl8kUWwQ/Xj+9walVn4+uvJFqlWpwC11F5CzzkvI75586XSWYEh8BSRWKXDw5suoMZZDzyf4lGkMxLn2F7CtQgHjHAIfkuY/FJirnV9BOPkLdCq7cu8vMKmcjkrfJBa5auQHxvsf2kilQHD0FbgonQjMyZ2/KC3AYzuyrvxUZyt6KmLXhtgrXhAcDdI+18t/NCg383CJtS9I6/nlZGwvat/ft2KNx8wmie2ma6R7K/kSmrZpWrPb7RQAAAAAAAAAAOBXvAGvzwnuz+x0kQAAAABJRU5ErkJggg==">"""

    assert content == expected


def test_ie_get_embedded_image_filepath__xhtml():
    ie = mistune._ImageEmbedder()

    filepath = os.path.join(os.path.dirname(__file__), 'image.png')
    content = ie.get_embedded_image(filepath, allow_local=True, use_xhtml=True)

    expected = """\
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAY1BMVEX///8AAADy8vLDw8OGhoYJCQnf398EBAQdHR3s7OwPDw/7+/uioqIkJCQnJye6urrJyckbGxtlZWWwsLBvb29BQUE6Ojrk5OR+fn4WFhYvLy/W1tZqampVVVV4eHiUlJQ1NTVSAT8kAAABJ0lEQVR4nO3XWXKDMBBFUZpBgJjBgDGe9r/K2EkqcRHpL9VUKvds4D0EtKQgAAAAAAAAAAAA+NPC2Zg53Cs9Hw5jnWXV1Jdmj/jbPZFPaX1UrxCNqbw6DYVqfpnJho01G5TLNl8kUWwQ/Xj+9walVn4+uvJFqlWpwC11F5CzzkvI75586XSWYEh8BSRWKXDw5suoMZZDzyf4lGkMxLn2F7CtQgHjHAIfkuY/FJirnV9BOPkLdCq7cu8vMKmcjkrfJBa5auQHxvsf2kilQHD0FbgonQjMyZ2/KC3AYzuyrvxUZyt6KmLXhtgrXhAcDdI+18t/NCg383CJtS9I6/nlZGwvat/ft2KNx8wmie2ma6R7K/kSmrZpWrPb7RQAAAAAAAAAAOBXvAGvzwnuz+x0kQAAAABJRU5ErkJggg==" />"""

    assert content == expected


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


def test_hard_wrap_renderer():
    text = 'foo\nnewline'
    renderer = mistune.Renderer(hard_wrap=True)
    func = mistune.Markdown(renderer=renderer)
    assert '<br>' in func(text)
