from unittest import TestCase

from mistune import create_markdown


class TestSafeUrlSecurity(TestCase):
    def test_percent_encoded_harmful_url_scheme_is_blocked(self):
        for text in [
            "[h](javascript%3Aalert(1))",
            "[h](javascript%253Aalert(1))",
            "[h][r]\n\n[r]: javascript%3Aalert(1)",
            "![h](data%3Atext/html;base64,PHNjcmlwdD4=)",
            "[h](view-source:javascript:alert(1))",
        ]:
            html = create_markdown()(text)
            self.assertIn("#harmful-link", html, text)

    def test_safe_percent_encoded_data_image_is_allowed(self):
        html = create_markdown()("![h](data%3Aimage/png;base64,AAAA)")
        self.assertIn('src="data%3Aimage/png;base64,AAAA"', html)
