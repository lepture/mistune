from unittest import TestCase

from mistune import create_markdown
from mistune.directives import FencedDirective, TableOfContents
from mistune.toc import add_toc_hook, render_toc_ul


class TestTocSecurity(TestCase):
    def test_custom_heading_id_is_escaped(self):
        md = create_markdown(escape=True)
        add_toc_hook(md, heading_id=lambda token, index: token.get("text", ""))

        html, _state = md.parse('## foo" onmouseover="alert(1)" x="\n')

        self.assertIn('id="foo&quot; onmouseover=&quot;alert(1)&quot; x=&quot;"', html)
        self.assertNotIn('onmouseover="alert(1)"', html)

    def test_toc_href_is_escaped(self):
        md = create_markdown(escape=True)
        add_toc_hook(md, heading_id=lambda token, index: token.get("text", ""))

        _html, state = md.parse('## x"><script>alert(1)</script><a href="\n')
        toc = render_toc_ul(state.env["toc_items"])

        self.assertIn('href="#x&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;&lt;a href=&quot;"', toc)
        self.assertNotIn("<script>", toc)

    def test_default_toc_id_avoids_existing_html_id_collision(self):
        md = create_markdown(escape=False)
        add_toc_hook(md)

        html, state = md.parse('<div id="toc_1"></div>\n\n# title\n')
        toc = render_toc_ul(state.env["toc_items"])

        self.assertIn('<h1 id="toc_1_1">title</h1>', html)
        self.assertIn('href="#toc_1_1"', toc)

    def test_directive_toc_avoids_sequential_html_id_collisions(self):
        md = create_markdown(escape=False, plugins=[FencedDirective([TableOfContents()])])
        source = '<div id="toc_1"></div>\n<div id="toc_1_1"></div>\n\n```{toc}\n```\n\n# title\n'

        html = md(source)

        self.assertIn('<h1 id="toc_1_2">title</h1>', html)
        self.assertIn('href="#toc_1_2"', html)

    def test_toc_hooks_preserve_existing_heading_id(self):
        md = create_markdown(escape=False, plugins=[FencedDirective([TableOfContents()])])

        def set_heading_id(_md, state):
            for token in state.tokens:
                if token["type"] == "heading":
                    token["attrs"]["id"] = "existing"

        md.before_render_hooks.insert(0, set_heading_id)
        html = md("```{toc}\n```\n\n# title\n")

        self.assertIn('<h1 id="existing">title</h1>', html)
        self.assertIn('href="#existing"', html)
        self.assertNotIn('id="toc_1"', html)

    def test_two_toc_sections_share_heading_ids(self):
        md = create_markdown(escape=False, plugins=[FencedDirective([TableOfContents()])])
        html = md("```{toc}\n```\n\n```{toc}\n```\n\n# title\n")

        self.assertEqual(html.count('<h1 id="toc_1">title</h1>'), 1)
        self.assertEqual(html.count('href="#toc_1"'), 2)

    def test_hook_preserves_existing_heading_id(self):
        md = create_markdown(escape=False)

        def set_heading_id(_md, state):
            for token in state.tokens:
                if token["type"] == "heading":
                    token["attrs"]["id"] = "existing"

        md.before_render_hooks.append(set_heading_id)
        add_toc_hook(md)
        html, state = md.parse("# title\n")

        self.assertIn('<h1 id="existing">title</h1>', html)
        self.assertIn('href="#existing"', render_toc_ul(state.env["toc_items"]))
