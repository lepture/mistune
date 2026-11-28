import pytest

from mistune import create_markdown
from mistune.renderers.rst import RSTRenderer


@pytest.mark.parametrize("level,marker", [(1, "="), (3, "~"), (6, "'")])
@pytest.mark.parametrize(
    "text,width",
    [
        ("Intro 简介", 10),
        ("日本語 Guide", 12),
        ("한글 Guide", 10),
        ("ＡＢ Guide", 10),
        ("Heading 🚀", 10),
        ("Plain title", 11),
        ("Café title", 10),
        ("e\u0301 title", 8),
        ("Intro\t简介", 12),
        ("A\tB", 9),
        ("简介\tGuide", 15),
        ("é\tB", 9),
        ("Intro\t\t简介", 20),
        ("A\tB\tC", 17),
    ],
)
def test_rst_heading_display_width(level, marker, text, width):
    render = create_markdown(renderer=RSTRenderer())
    assert render("#" * level + " " + text) == text + "\n" + marker * width + "\n"
