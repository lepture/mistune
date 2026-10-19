from unittest import TestCase

from mistune import HTMLRenderer, create_markdown
from mistune.directives import FencedDirective, Figure, Image
from mistune.directives.image import render_block_image, render_figure


class TestImageDirectiveSecurity(TestCase):
    def test_image_directive_rejects_css_dimension_injection(self):
        md = create_markdown(escape=True, plugins=[FencedDirective([Image()])])
        html = md("```{image} x.jpg\n:width: 100vw;height:100vh;position:fixed;top:0\n:height: 50%\n:alt: <alt>\n```\n")

        self.assertIn('alt="&lt;alt&gt;"', html)
        self.assertIn('style="height:50%;"', html)
        self.assertNotIn("position:fixed", html)

    def test_figure_directive_escapes_class_and_rejects_figwidth_css_injection(self):
        md = create_markdown(escape=True, plugins=[FencedDirective([Figure()])])
        html = md(
            '```{figure} x.jpg\n:figclass: evil" onclick="alert(1)\n:figwidth: 10px;position:fixed\n\ncaption\n```\n'
        )

        self.assertIn('class="figure evil&quot; onclick=&quot;alert(1)"', html)
        self.assertNotIn('onclick="alert(1)"', html)
        self.assertNotIn("position:fixed", html)
        self.assertNotIn('style="width:', html)

    def test_directive_renderers_escape_all_attribute_contexts(self):
        renderer = HTMLRenderer(escape=False)
        image = render_block_image(
            renderer,
            'https://example.com/a"b.png',
            alt='a"<b>',
            width="10px;position:fixed",
            height="50%",
            align="left",
            target="javascript:marker",
        )
        figure = render_figure(renderer, "caption", figclass='wide" onclick="marker', figwidth="10px;position:fixed")

        self.assertIn('src="https://example.com/a&quot;b.png"', image)
        self.assertIn('alt="a&quot;&lt;b&gt;"', image)
        self.assertIn('href="#harmful-link"', image)
        self.assertIn('style="height:50%;"', image)
        self.assertNotIn("position:fixed", image)
        self.assertIn('class="figure wide&quot; onclick=&quot;marker"', figure)
        self.assertNotIn('onclick="marker"', figure)
        self.assertNotIn("position:fixed", figure)
