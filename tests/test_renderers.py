from unittest import TestCase

from mistune import create_markdown
from mistune.renderers.rst import RSTRenderer
from mistune.renderers.markdown import MarkdownRenderer
from tests import BaseTestCase


def load_renderer(renderer):
    class TestRenderer(BaseTestCase):
        parse = create_markdown(renderer=renderer)

    name = renderer.NAME
    TestRenderer.load_fixtures("renderer_" + name + ".txt")
    globals()["TestRenderer" + name.title()] = TestRenderer


load_renderer(RSTRenderer())
load_renderer(MarkdownRenderer())


class TestMarkdownRendererRoundTrip(TestCase):
    """Reformatting valid Markdown must not change its meaning: rendering the
    reformatted source to HTML must match rendering the original source."""

    to_html = create_markdown(escape=False)
    reformat = create_markdown(renderer=MarkdownRenderer())

    def assert_round_trip(self, text):
        self.assertEqual(
            self.to_html(self.reformat(text)),
            self.to_html(text),
        )

    def test_escaped_block_markers(self):
        # an escaped leading marker is literal text, not a new block
        for marker in (r"\*", r"\-", r"\+", r"\#", r"\##", r"\>", r"1\.", r"3\)"):
            self.assert_round_trip(marker + " literal\n")

    def test_escaped_marker_on_continuation_line(self):
        self.assert_round_trip("paragraph\n\\* not a list\n")

    def test_escaped_marker_inside_list_item(self):
        self.assert_round_trip("- item\n\n  \\# not a heading\n")

    def test_escaped_backtick(self):
        self.assert_round_trip(r"\`not code\`" + "\n")

    def test_real_markers_preserved(self):
        for text in (
            "* bullet\n",
            "# heading\n",
            "1. ordered\n",
            "> quote\n",
            "`code`\n",
            "*emphasis*\n",
        ):
            self.assert_round_trip(text)

    def test_prose_not_over_escaped(self):
        for text in (
            "snake_case_var\n",
            "use - dashes - here\n",
            "C# and a.b.c and 1.5\n",
            "ratio a/b is fine\n",
        ):
            self.assert_round_trip(text)


class TestTaskListRoundTrip(TestCase):
    """The task_lists plugin rewrites a list_item into a task_list_item and
    moves the checkbox marker into attrs. The markdown and rst renderers must
    re-emit it instead of silently dropping it (issues #401 and #441)."""

    to_html = create_markdown(escape=False, plugins=["task_lists"])
    reformat = create_markdown(renderer=MarkdownRenderer(), plugins=["task_lists"])
    to_rst = create_markdown(renderer=RSTRenderer(), plugins=["task_lists"])

    def assert_round_trip(self, text):
        self.assertEqual(
            self.to_html(self.reformat(text)),
            self.to_html(text),
        )

    def test_checkbox_preserved(self):
        # the exact issue example: the checkbox used to disappear entirely
        self.assertEqual(
            self.reformat("- [x] done\n- [ ] todo\n"),
            "- [x] done\n- [ ] todo\n",
        )

    def test_round_trip_variants(self):
        for text in (
            "- [x] done\n- [ ] todo\n",
            "- [X] upper-x is checked\n",
            "1. [ ] a\n2. [x] b\n",
            "- [ ] outer\n  - [x] inner\n",
            "- [ ] line one\n  line two\n",
            "- plain item\n- [ ] task item\n",
        ):
            self.assert_round_trip(text)

    def test_rst_preserves_checkbox(self):
        self.assertIn("[x] done", self.to_rst("- [x] done\n"))
        self.assertIn("[ ] todo", self.to_rst("- [ ] todo\n"))
