import mistune
from tests import BaseTestCase, normalize_html


DIFF_CASES = {
    "setext_headings_093",
    "html_blocks_191",  # mistune keeps \n
    "images_573",  # image can not be in image
    "links_495",
    "links_517",  # aggressive link group
    "links_518",
    "links_519",
    "links_531",
    "links_532",
}

IGNORE_CASES = {
    # we don't support link title in (title)
    "links_496",
    "links_504",
    # we don't support flanking delimiter run
    "emphasis_and_strong_emphasis_352",
    "emphasis_and_strong_emphasis_367",
    "emphasis_and_strong_emphasis_368",
    "emphasis_and_strong_emphasis_372",
    "emphasis_and_strong_emphasis_379",
    "emphasis_and_strong_emphasis_388",
    "emphasis_and_strong_emphasis_391",
    "emphasis_and_strong_emphasis_406",
    "emphasis_and_strong_emphasis_407",
    "emphasis_and_strong_emphasis_408",
    "emphasis_and_strong_emphasis_412",
    "emphasis_and_strong_emphasis_413",
    "emphasis_and_strong_emphasis_414",
    "emphasis_and_strong_emphasis_416",
    "emphasis_and_strong_emphasis_417",
    "emphasis_and_strong_emphasis_418",
    "emphasis_and_strong_emphasis_424",
    "emphasis_and_strong_emphasis_425",
    "emphasis_and_strong_emphasis_426",
    "emphasis_and_strong_emphasis_429",
    "emphasis_and_strong_emphasis_430",
    "emphasis_and_strong_emphasis_431",
    "emphasis_and_strong_emphasis_460",
    "emphasis_and_strong_emphasis_467",
    "emphasis_and_strong_emphasis_470",
    "emphasis_and_strong_emphasis_471",
    "emphasis_and_strong_emphasis_477",
    "emphasis_and_strong_emphasis_478",
}

for i in range(441, 447):
    IGNORE_CASES.add("emphasis_and_strong_emphasis_" + str(i))
for i in range(453, 459):
    IGNORE_CASES.add("emphasis_and_strong_emphasis_" + str(i))
for i in range(462, 466):
    IGNORE_CASES.add("emphasis_and_strong_emphasis_" + str(i))


class TestCommonMark(BaseTestCase):
    @classmethod
    def ignore_case(cls, n):
        return n in IGNORE_CASES or n in DIFF_CASES

    def assert_case(self, n, text, html):
        result = mistune.html(text)
        self.assertEqual(normalize_html(result), normalize_html(html))


TestCommonMark.load_fixtures("commonmark.json")
