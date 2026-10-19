from unittest import TestCase

import pytest

from mistune import BlockParser, InlineParser, Markdown, create_markdown
from mistune.plugins import import_plugin
from tests.perf_utils import assert_near_linear


@pytest.mark.parametrize("length", [500, 501, 998, 999, 1000])
def test_reference_label_length_is_measured_in_source_characters(length):
    label = "a" * length
    source = f"[text][{label}]\n\n[{label}]: /url\n"
    result = create_markdown()(source)
    if length <= 999:
        assert result == '<p><a href="/url">text</a></p>\n'
    else:
        assert '<a href="/url">' not in result
        assert label in result


@pytest.mark.parametrize("pairs,valid", [(499, True), (500, False)])
def test_escaped_reference_label_characters_count_toward_limit(pairs, valid):
    label = r"\*" * pairs
    result = create_markdown()(f"[text][{label}]\n\n[{label}]: /url\n")
    assert ('<a href="/url">text</a>' in result) is valid


def test_reference_label_limit_does_not_limit_inline_link_text():
    text = "a" * 2000
    assert create_markdown()(f"[{text}](/url)") == f'<p><a href="/url">{text}</a></p>\n'


@pytest.mark.parametrize("level,valid", [(19, True), (20, True), (21, False)])
def test_destination_parenthesis_limit(level, valid):
    destination = "(" * level + "url" + ")" * level
    result = create_markdown()(f"[text]({destination}) [ok](/ok) *em* `code`")
    assert ('<a href="' + destination + '">text</a>' in result) is valid
    assert result.endswith('<a href="/ok">ok</a> <em>em</em> <code>code</code></p>\n')
    if not valid:
        assert f"[text]({destination})" in result


@pytest.mark.parametrize("character", ["\x01", "\x08", "\x1f", "\x7f"])
def test_bare_destination_rejects_ascii_control_characters(character):
    result = create_markdown()(f"[bad](a{character}b) [ok](/ok)")
    assert result.count("<a ") == 1
    assert result.endswith('<a href="/ok">ok</a></p>\n')


def test_parenthesized_title_rejects_unescaped_nested_parentheses():
    result = create_markdown()('[bad](/url (a (b))) [ok](/ok "a (b)")')
    assert result == '<p>[bad](/url (a (b))) <a href="/ok" title="a (b)">ok</a></p>\n'


@pytest.mark.parametrize("destination", ["<a<b>", "<a\\\nb>", "a(b", "a)b"])
def test_invalid_reference_destination_remains_text(destination):
    result = create_markdown()(f"[bad]: {destination}\n\n[bad] [ok](/ok)")
    assert '<a href="/ok">ok</a>' in result
    assert "[bad]" in result
    assert result.count("<a ") == 1


def test_invalid_image_reference_keeps_inner_link():
    result = create_markdown()("[![x][y](/inner)](/outer)")
    assert result == '<p>[![x]<a href="/inner">y</a>](/outer)</p>\n'


@pytest.mark.parametrize(
    "source",
    [
        "[[missing]][ref] [ok](/ok)",
        "[](foo( [outer ![inner](url)](/outer) [ok](/ok)",
        "[]( <foo [bar](/url) [ok](/ok)",
        "[" * 2000 + "missing" + "]" * 2000 + " [ok](/ok)",
        "![" * 1000 + "text" + "](/image)" * 1000 + " [ok](/ok)",
    ],
)
def test_failed_candidates_preserve_following_legal_syntax(source):
    result = create_markdown()(source + " *em* `code`")
    assert result.endswith('<a href="/ok">ok</a> <em>em</em> <code>code</code></p>\n')


def inline_depth(tokens):
    maximum = 0
    stack = [(token, 0) for token in tokens]
    while stack:
        token, depth = stack.pop()
        if "children" in token:
            depth += 1
            maximum = max(maximum, depth)
            stack.extend((child, depth) for child in token["children"])
    return maximum


@pytest.mark.parametrize("limit", [1, 3, 7])
@pytest.mark.parametrize("plugin", ["strikethrough", "mark", "insert", "spoiler"])
def test_mixed_inline_syntax_shares_one_depth_budget(limit, plugin):
    markers = {"strikethrough": ("~~", "~~"), "mark": ("==", "=="), "insert": ("^^", "^^"), "spoiler": (">!", "!<")}
    start, end = markers[plugin]
    text = "text"
    for _ in range(30):
        text = f"{start} before *![alt {text}](/image)* after {end}"
    md = Markdown(inline=InlineParser(max_nested_level=limit))
    md.use(import_plugin(plugin))
    ast = md("prefix " + text + " [ok](/ok) *em*")
    assert inline_depth(ast[0]["children"]) <= limit
    tail = ast[0]["children"]
    assert any(token["type"] == "link" and token["attrs"]["url"] == "/ok" for token in tail)
    assert tail[-1]["type"] == "emphasis"


@pytest.mark.parametrize(
    "content,plugins,definitions",
    [
        ("<https://example.com>", [], ""),
        ("<user@example.com>", [], ""),
        ("https://example.com", ["url"], ""),
        ("HTML", ["abbr"], "\n\n*[HTML]: expansion\n"),
        ("[字(read)](/inner)", ["ruby"], ""),
    ],
)
def test_automatic_and_plugin_links_respect_the_remaining_budget(content, plugins, definitions):
    md = Markdown(inline=InlineParser(max_nested_level=1))
    for plugin in ["strikethrough", *plugins]:
        md.use(import_plugin(plugin))
    ast = md(f"~~{content}~~ [ok](/ok)" + definitions)
    inline = ast[0]["children"]
    assert inline[0]["type"] == "strikethrough"
    assert inline_depth(inline) == 1
    assert any(token["type"] == "link" and token["attrs"]["url"] == "/ok" for token in inline)


@pytest.mark.parametrize("limit", [0, -1])
def test_nesting_limits_must_be_positive(limit):
    with pytest.raises(ValueError, match="max_nested_level"):
        InlineParser(max_nested_level=limit)
    with pytest.raises(ValueError, match="max_nested_level"):
        BlockParser(max_nested_level=limit)


def test_inline_depth_aliases_configure_the_same_limit():
    parser = InlineParser(max_image_depth=3)
    assert parser.max_nested_level == parser.max_emphasis_depth == 3
    parser.max_emphasis_depth = 7
    assert parser.max_image_depth == parser.max_nested_level == 7


def test_code_delimiters_are_matched_by_complete_run_length():
    source = " ".join("`" * length + "text" for length in range(1, 120))
    result = create_markdown()(source + " [ok](/ok) *em*")
    assert result.endswith('<a href="/ok">ok</a> <em>em</em></p>\n')
    assert "<code>" not in result


@pytest.mark.parametrize("parser", [BlockParser(max_nested_level=3), InlineParser(max_nested_level=3)])
def test_markdown_uses_the_same_default_limit_for_both_parsers(parser):
    md = Markdown(block=parser) if isinstance(parser, BlockParser) else Markdown(inline=parser)
    assert md.block.max_nested_level == md.inline.max_nested_level == 3


@pytest.mark.parametrize("marker", ["<!--", "<?", "<![CDATA[", "<!DOCTYPE text"])
def test_unclosed_inline_html_recovers_without_rescanning_the_document(marker):
    md = create_markdown()

    def render(size):
        return md("prefix " + (marker + " text ") * size + "[ok](/ok) *em* `code`")

    _, result = assert_near_linear(TestCase(), render, 1000, 2000)
    assert result.endswith('<a href="/ok">ok</a> <em>em</em> <code>code</code></p>\n')


@pytest.mark.parametrize("html", ["<??>", "<![CDATA[]]>", "<!DOCTYPE html>", "<!-->", "<!--->", "<!-- a -- b -->"])
def test_inline_html_delimiter_boundaries(html):
    result = create_markdown(escape=False)("prefix " + html + " [ok](/ok)")
    assert result == f'<p>prefix {html} <a href="/ok">ok</a></p>\n'


@pytest.mark.parametrize("source", ["<!A>", "<!ABC>", "<!A!>", "<!a b>"])
def test_invalid_declarations_do_not_consume_later_closing_delimiters(source):
    result = create_markdown(escape=False)("prefix " + source + " later > [ok](/ok)")
    assert "&lt;!" in result
    assert result.endswith('later &gt; <a href="/ok">ok</a></p>\n')


def test_links_inside_many_pending_images_do_not_rescan_image_openers():
    md = create_markdown()

    def render(size):
        return md("![" * size + "[text](/inner) " * size + "](/image)" * size + " [ok](/ok)")

    _, result = assert_near_linear(TestCase(), render, 500, 1000)
    assert result.endswith('<a href="/ok">ok</a></p>\n')


def test_unclosed_destinations_recover_in_linear_time():
    md = create_markdown()

    def render(size):
        return md("[](" * size + " [ok](/ok) *em*")

    _, result = assert_near_linear(TestCase(), render, 2000, 4000)
    assert result.endswith('<a href="/ok">ok</a> <em>em</em></p>\n')
