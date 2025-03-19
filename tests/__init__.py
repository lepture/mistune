import re
from abc import abstractmethod
from unittest import TestCase

from tests import fixtures


class BaseTestCase(TestCase):
    @classmethod
    def load_fixtures(cls, case_file: str) -> None:
        def attach_case(n: str, text: str, html: str) -> None:
            def method(self: "BaseTestCase") -> None:
                self.assert_case(n, text, html)

            name = "test_{}".format(n)
            method.__name__ = name
            method.__doc__ = "Run fixture {} - {}".format(case_file, n)
            setattr(cls, name, method)

        for n, text, html in fixtures.load_examples(case_file):
            if cls.ignore_case(n):
                continue
            attach_case(n, text, html)

    @classmethod
    def ignore_case(cls, name: str) -> bool:
        return False

    @abstractmethod
    def parse(self, text: str) -> str: ...

    def assert_case(self, name: str, text: str, html: str) -> None:
        result = self.parse(text)
        self.assertEqual(result, html)


def normalize_html(html: str) -> str:
    html = re.sub(r">\n+", ">", html)
    html = re.sub(r"\n+<", "<", html)
    return html.strip()
