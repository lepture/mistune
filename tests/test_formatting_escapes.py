import pytest

from mistune import create_markdown


@pytest.mark.parametrize("speedup", [False, True])
@pytest.mark.parametrize(
    "plugin,source,expected",
    [
        ("strikethrough", r"~~delete \~~ me~~", "<p><del>delete ~~ me</del></p>\n"),
        ("mark", r"==mark \== me==", "<p><mark>mark == me</mark></p>\n"),
        ("insert", r"^^insert \^^ me^^", "<p><ins>insert ^^ me</ins></p>\n"),
    ],
)
def test_escaped_first_delimiter_does_not_close_span(plugin: str, source: str, expected: str, speedup: bool) -> None:
    plugins = [plugin, "speedup"] if speedup else [plugin]
    assert create_markdown(plugins=plugins)(source) == expected


@pytest.mark.parametrize("speedup", [False, True])
@pytest.mark.parametrize(
    "plugin,source,expected",
    [
        ("strikethrough", "~~delete me~~", "<p><del>delete me</del></p>\n"),
        ("mark", "==mark me==", "<p><mark>mark me</mark></p>\n"),
        ("insert", "^^insert me^^", "<p><ins>insert me</ins></p>\n"),
        ("strikethrough", r"~~delete \~\~ me~~", "<p><del>delete ~~ me</del></p>\n"),
        ("mark", r"==mark \=\= me==", "<p><mark>mark == me</mark></p>\n"),
        ("insert", r"^^insert \^\^ me^^", "<p><ins>insert ^^ me</ins></p>\n"),
    ],
)
def test_existing_formatting_closers_and_escapes(plugin: str, source: str, expected: str, speedup: bool) -> None:
    plugins = [plugin, "speedup"] if speedup else [plugin]
    assert create_markdown(plugins=plugins)(source) == expected
