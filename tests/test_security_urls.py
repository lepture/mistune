from unittest import TestCase

from mistune import create_markdown, html


class TestSafeUrlSecurity(TestCase):
    def test_known_harmful_url_schemes_are_blocked(self):
        for url in [
            "javascript:alert(1)",
            "vbscript:msgbox(1)",
            "file:///etc/passwd",
            "data:text/html;base64,PHNjcmlwdD4=",
            "feed:javascript:alert(1)",
            "livescript:alert(1)",
            "mocha:alert(1)",
            "view-source:javascript:alert(1)",
            "jar:javascript:alert(1)",
            "ms-its:javascript:alert(1)",
            "mk:@MSITStore:javascript:alert(1)",
            "res:javascript:",
        ]:
            rendered = html(f"[h]({url})")
            self.assertIn('href="#harmful-link"', rendered, url)

    def test_unknown_url_scheme_is_blocked(self):
        rendered = html("[h](x-javascript:alert(1))")

        self.assertIn('href="#harmful-link"', rendered)

    def test_reference_and_autolink_harmful_url_schemes_are_blocked(self):
        cases = [
            "[h][r]\n\n[r]: feed:javascript:alert(1)",
            "<feed:javascript:alert(1)>",
            "[h][r]\n\n[r]: x-javascript:alert(1)",
            "<x-javascript:alert(1)>",
        ]
        for text in cases:
            rendered = create_markdown()(text)
            self.assertIn('href="#harmful-link"', rendered, text)

    def test_percent_encoded_harmful_url_scheme_is_blocked(self):
        for text in [
            "[h](javascript%3Aalert(1))",
            "[h](javascript%253Aalert(1))",
            "[h][r]\n\n[r]: javascript%3Aalert(1)",
            "![h](data%3Atext/html;base64,PHNjcmlwdD4=)",
            "[h](view-source:javascript:alert(1))",
            "[h](%20javascript%3Aalert(1))",
        ]:
            rendered = create_markdown()(text)
            self.assertIn("#harmful-link", rendered, text)

    def test_safe_percent_encoded_data_image_is_allowed(self):
        rendered = create_markdown()("![h](data%3Aimage/png;base64,AAAA)")
        self.assertIn('src="data%3Aimage/png;base64,AAAA"', rendered)

    def test_safe_url_schemes_are_allowed(self):
        for url in [
            "http://example.com",
            "https://example.com",
            "mailto:user@example.com",
            "tel:+123456789",
            "ftp://example.com/file",
            "ftps://example.com/file",
            "irc://example.com/channel",
            "ircs://example.com/channel",
            "//example.com/path",
            "/path",
            "./path:with-colon",
            "../path:with-colon",
            "path/with:colon",
            "#fragment",
            "?query",
        ]:
            rendered = html(f"[h]({url})")
            self.assertIn(f'href="{url}"', rendered, url)
