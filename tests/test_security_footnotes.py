import re
from unittest import TestCase

from mistune.core import InlineState
from mistune.inline_parser import InlineParser
from mistune.plugins.footnotes import INLINE_FOOTNOTE, parse_inline_footnote


class _NoMembershipList(list[str]):
    def __contains__(self, item: object) -> bool:
        raise AssertionError("footnote membership must use footnote_indexes")


class TestFootnoteSecurity(TestCase):
    def test_inline_footnote_membership_uses_index_mapping(self):
        notes = _NoMembershipList(["FIRST"])
        indexes = {"FIRST": 0}
        state = InlineState(
            {
                "ref_footnotes": {"FIRST": "First note", "SECOND": "Second note"},
                "footnotes": notes,
                "footnote_indexes": indexes,
            }
        )
        match = re.match(INLINE_FOOTNOTE, "[^second]")
        self.assertIsNotNone(match)
        assert match is not None

        parse_inline_footnote(InlineParser(), match, state)

        self.assertEqual(notes, ["FIRST", "SECOND"])
        self.assertEqual(indexes, {"FIRST": 0, "SECOND": 1})
        self.assertEqual(
            state.tokens,
            [{"type": "footnote_ref", "raw": "SECOND", "attrs": {"index": 2}}],
        )
