import platform
import time
from unittest import TestCase

from mistune import create_markdown

IS_PYPY = platform.python_implementation() == "PyPy"
DEADLINE = 1.0 if IS_PYPY else 0.5


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
        payload = '[x](y "' + "\\!" * 24 + ")"

        start = time.monotonic()
        html = md(payload)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[x](y", html)

    def test_nested_bracket_link_input_does_not_recurse_forever(self):
        text = "[" * 8000 + "x" + "]" * 8000

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[", html)

    def test_failed_outer_bracket_preserves_nested_link(self):
        html = create_markdown()("[[x](https://example.com)]")

        self.assertEqual('<p>[<a href="https://example.com">x</a>]</p>\n', html)

    def test_failed_reference_after_nested_brackets_returns_quickly(self):
        text = "[" * 8000 + "x" + "]" * 8000 + "[missing]"

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[missing]", html)

    def test_failed_reference_does_not_hide_following_inline_link(self):
        html = create_markdown()("[foo][bar](https://example.com)")

        self.assertEqual('<p>[foo]<a href="https://example.com">bar</a></p>\n', html)

    def test_unmatched_bracket_input_returns_quickly(self):
        text = "[" * 4000

        start = time.monotonic()
        html = create_markdown()(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertIn("[", html)

    def test_deep_emphasis_input_does_not_recurse_forever(self):
        marks = "*" * 1000
        text = marks + "a" + marks

        start = time.monotonic()
        html = create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assertLessEqual(html.count("<strong>") + html.count("<em>"), 20)
        self.assertTrue(ast)

    def test_deep_image_input_does_not_recurse_forever(self):
        text = "![" * 1000 + "a" + "](u)" * 1000

        start = time.monotonic()
        create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assert_max_token_depth(ast, "image", 20)

    def test_link_with_deep_image_input_does_not_recurse_forever(self):
        text = "[" + "![" * 1000 + "a" + "](u)" * 1000 + "](u)"

        start = time.monotonic()
        create_markdown()(text)
        ast = create_markdown(renderer="ast")(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
        self.assert_max_token_depth(ast, "image", 20)

    def test_deep_link_input_does_not_recurse_forever(self):
        text = "[" * 1000 + "a" + "](u)" * 1000

        start = time.monotonic()
        create_markdown(renderer="ast")(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)

    def test_repeated_link_suffixes_are_near_linear(self):
        md = create_markdown()

        def render(size):
            text = "[" * size + "a" + "](/u)" * size + "\n"
            start = time.process_time()
            md(text)
            return time.process_time() - start

        render(200)
        small = render(1000)
        large = render(2000)

        self.assertLess(large, DEADLINE)
        self.assertLess(large, small * 3)

    def test_repeated_unclosed_inline_spoilers_are_near_linear(self):
        md = create_markdown(plugins=["spoiler"])

        def render(size):
            text = ">! a " * size + "\n"
            start = time.process_time()
            md(text)
            return time.process_time() - start

        render(200)
        small = render(1000)
        large = render(2000)

        self.assertLess(large, DEADLINE)
        self.assertLess(large, small * 3)

    def test_adjacent_ruby_tokens_do_not_recurse_forever(self):
        text = "[a(b)]" * 3000 + "\n"

        start = time.monotonic()
        create_markdown(plugins=["ruby"])(text)
        elapsed = time.monotonic() - start

        self.assertLess(elapsed, DEADLINE)
