import pytest

from mistune import create_markdown


@pytest.fixture(params=[False, True], ids=["plain", "speedup"])
def md(request):
    plugins = ["ruby", "speedup"] if request.param else ["ruby"]
    return create_markdown(escape=False, plugins=plugins)


@pytest.mark.parametrize("target,definitions", [("(/inner)", ""), ("[reading]", "\n\n[reading]: /inner")])
def test_ruby_link_deactivates_outer_link(md, target, definitions):
    source = "[See [kanji(reading)]" + target + "](/outer)" + definitions
    assert md(source) == '<p>[See <a href="/inner"><ruby>kanji<rt>reading</rt></ruby></a>](/outer)</p>\n'


def test_ruby_link_inside_html_anchor_stays_unlinked(md):
    source = '<a href="/outer">[kanji(reading)](/inner)</a>'
    assert md(source) == '<p><a href="/outer"><ruby>kanji<rt>reading</rt></ruby>(/inner)</a></p>\n'


def test_ruby_link_deactivates_outer_reference_link(md):
    source = "[See [kanji(reading)](/inner)][outer]\n\n[outer]: /outer"
    assert md(source) == (
        '<p>[See <a href="/inner"><ruby>kanji<rt>reading</rt></ruby></a>]'
        '<a href="/outer">outer</a></p>\n'
    )


def test_missing_ruby_reference_preserves_outer_link(md):
    source = "[See [kanji(reading)][missing]](/outer)"
    assert md(source) == '<p><a href="/outer">See <ruby>kanji<rt>reading</rt></ruby>[missing]</a></p>\n'


def test_ruby_links_and_image_wrappers_still_render(md):
    linked_ruby = '<p><a href="/inner"><ruby>kanji<rt>reading</rt></ruby></a></p>\n'
    assert md("[kanji(reading)](/inner)") == linked_ruby
    assert md("[kanji(reading)][ref]\n\n[ref]: /inner") == linked_ruby
    assert md("![[kanji(reading)](/inner)](/image.png)") == '<p><img src="/image.png" alt="kanjireading" /></p>\n'
    assert md("[[kan(kan)][ji(ji)]](/outer)") == (
        '<p><a href="/outer"><ruby>kan<rt>kan</rt></ruby><ruby>ji<rt>ji</rt></ruby></a></p>\n'
    )
