from unittest import TestCase

from mistune import create_markdown
from mistune.directives import FencedDirective, Figure, Image


class TestImageDirectiveSecurity(TestCase):
    def test_image_directive_rejects_css_dimension_injection(self):
        md = create_markdown(escape=True, plugins=[FencedDirective([Image()])])
        html = md(
            "```{image} x.jpg\n"
            ":width: 100vw;height:100vh;position:fixed;top:0\n"
            ":height: 50%\n"
            ":alt: <alt>\n"
            "```\n"
        )

        self.assertIn('alt="&lt;alt&gt;"', html)
        self.assertIn('style="height:50%;"', html)
        self.assertNotIn("position:fixed", html)

    def test_figure_directive_escapes_class_and_rejects_figwidth_css_injection(self):
        md = create_markdown(escape=True, plugins=[FencedDirective([Figure()])])
        html = md(
            "```{figure} x.jpg\n"
            ':figclass: evil" onclick="alert(1)\n'
            ":figwidth: 10px;position:fixed\n"
            "\n"
            "caption\n"
            "```\n"
        )

        self.assertIn('class="figure evil&quot; onclick=&quot;alert(1)"', html)
        self.assertNotIn('onclick="alert(1)"', html)
        self.assertNotIn("position:fixed", html)
        self.assertNotIn('style="width:', html)
