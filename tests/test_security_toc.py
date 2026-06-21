from unittest import TestCase

from mistune import create_markdown
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
