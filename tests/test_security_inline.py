from unittest import TestCase

from mistune import create_markdown
from tests.perf_utils import assert_near_linear


class TestInlineParserSecurity(TestCase):
    def assert_max_token_depth(self, tokens, token_type, max_depth):
        stack = [(token, 0) for token in tokens]
        while stack:
            token, depth = stack.pop()
            if token["type"] == token_type:
                depth += 1
                self.assertLessEqual(depth, max_depth)
            for child in token.get("children", ()):
                stack.append((child, depth))

    def test_link_title_redos_payload_returns_quickly(self):
        md = create_markdown()

        def render(size):
            return md('[x](y "' + "\\!" * size + ")")

        _small, html = assert_near_linear(self, render, 1000, 2000)
        self.assertIn("[x](y", html)

    def test_nested_bracket_link_input_does_not_recurse_forever(self):
        md = create_markdown()

        def render(size):
            return md("[" * size + "x" + "]" * size)

        _small, html = assert_near_linear(self, render, 4000, 8000)
        self.assertIn("[", html)

    def test_failed_outer_bracket_preserves_nested_link(self):
        html = create_markdown()("[[x](https://example.com)]")

        self.assertEqual('<p>[<a href="https://example.com">x</a>]</p>\n', html)

    def test_failed_reference_after_nested_brackets_returns_quickly(self):
        md = create_markdown()

        def render(size):
            return md("[" * size + "x" + "]" * size + "[missing]")

        _small, html = assert_near_linear(self, render, 2000, 4000)
        self.assertIn("[missing]", html)

    def test_failed_reference_does_not_hide_following_inline_link(self):
        html = create_markdown()("[foo][bar](https://example.com)")

        self.assertEqual('<p>[foo]<a href="https://example.com">bar</a></p>\n', html)

    def test_unmatched_bracket_input_returns_quickly(self):
        md = create_markdown()

        def render(size):
            return md("[" * size)

        _small, html = assert_near_linear(self, render, 2000, 4000)
        self.assertIn("[", html)

    def test_deep_emphasis_input_does_not_recurse_forever(self):
        marks = "*" * 1000
        text = marks + "a" + marks

        html = create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)

        self.assertLessEqual(html.count("<strong>") + html.count("<em>"), 20)
        self.assertTrue(ast)

    def test_deep_image_input_does_not_recurse_forever(self):
        text = "![" * 1000 + "a" + "](u)" * 1000

        create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)

        self.assert_max_token_depth(ast, "image", 20)

    def test_link_with_deep_image_input_does_not_recurse_forever(self):
        text = "[" + "![" * 1000 + "a" + "](u)" * 1000 + "](u)"

        create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)

        self.assert_max_token_depth(ast, "image", 20)

    def test_deep_link_input_does_not_recurse_forever(self):
        md = create_markdown(renderer="ast")

        def render(size):
            return md("[" * size + "a" + "](u)" * size)

        _small, ast = assert_near_linear(self, render, 500, 1000)
        self.assertTrue(ast)

    def test_repeated_link_suffixes_are_near_linear(self):
        md = create_markdown()

        def render(size):
            return md("[" * size + "a" + "](/u)" * size + "\n")

        _small, html = assert_near_linear(self, render, 1000, 2000)
        self.assertIn('href="/u"', html)

    def test_repeated_unclosed_inline_spoilers_are_near_linear(self):
        md = create_markdown(plugins=["spoiler"])

        def render(size):
            return md(">! a " * size + "\n")

        _small, html = assert_near_linear(self, render, 1000, 2000)
        self.assertIn("&gt;! a", html)

    def test_adjacent_ruby_tokens_do_not_recurse_forever(self):
        md = create_markdown(plugins=["ruby"])

        def render(size):
            return md("[a(b)]" * size + "\n")

        _small, html = assert_near_linear(self, render, 1500, 3000)
        self.assertIn("<ruby>", html)
