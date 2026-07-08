import mistune
from tests import BaseTestCase, normalize_html


class TestCommonMark(BaseTestCase):
    markdown = mistune.create_markdown(
        renderer=mistune.HTMLRenderer(escape=False, allow_harmful_protocols=True),
    )

    def assert_case(self, n, text, html):
        result = self.markdown(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures("commonmark.json")
