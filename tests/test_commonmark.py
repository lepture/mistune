import mistune
from tests import BaseTestCase, normalize_html


class TestCommonMark(BaseTestCase):
    markdown = mistune.create_markdown(
        renderer=mistune.HTMLRenderer(escape=False, allow_harmful_protocols=True),
    )

    def assert_case(self, n, text, html):
        result = self.markdown(text)
        self.assertEqual(normalize_html(result), normalize_html(html))

    def test_commonmark_0312_inline_html_comments(self):
        cases = [
            (
                "foo <!-- this is a --\ncomment - with hyphens -->\n",
                "<p>foo <!-- this is a --\ncomment - with hyphens --></p>\n",
                "<p>foo &lt;!-- this is a --\ncomment - with hyphens --&gt;</p>\n",
            ),
            (
                "foo <!--> foo -->\n\nfoo <!---> foo -->\n",
                "<p>foo <!--> foo --&gt;</p>\n<p>foo <!---> foo --&gt;</p>\n",
                "<p>foo &lt;!--&gt; foo --&gt;</p>\n<p>foo &lt;!---&gt; foo --&gt;</p>\n",
            ),
        ]
        escaped_markdown = mistune.create_markdown()
        for text, raw_html, escaped_html in cases:
            with self.subTest(text=text):
                self.assertEqual(self.markdown(text), raw_html)
                self.assertEqual(escaped_markdown(text), escaped_html)


TestCommonMark.load_fixtures("commonmark.json")
