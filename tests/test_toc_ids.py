from unittest import TestCase

from mistune import create_markdown
from mistune.directives import FencedDirective, RSTDirective, TableOfContents
from mistune.toc import add_toc_hook, render_toc_ul


class TestTocHtmlIds(TestCase):
    def test_hook_scans_full_html_attribute_names_before_id(self):
        for attribute in (
            "data-é=x",
            "数据=x",
            "δ=x",
            "data-😺=x",
            "0data=x",
            "@click=x",
            "data`key=x",
            'data-é="x>y"',
            "data-é",
            "data\u00a0id=x",
        ):
            with self.subTest(attribute=attribute):
                md = create_markdown(escape=False)
                add_toc_hook(md)
                html, state = md.parse("<div " + attribute + " id=toc_1>Intro</div>\n\n# Heading")
                self.assertIn('<h1 id="toc_1_1">Heading</h1>', html)
                self.assertEqual(state.env["toc_items"], [(1, "toc_1_1", "Heading")])
                self.assertIn('href="#toc_1_1"', render_toc_ul(state.env["toc_items"]))

    def test_non_ascii_attribute_names_do_not_match_id_suffixes(self):
        for name in ("data-é", "é-id", "data\u00a0id", "id\u00a0", "іd"):
            with self.subTest(name=name):
                md = create_markdown(escape=False)
                add_toc_hook(md)
                html, state = md.parse("<div " + name + "=toc_1>Intro</div>\n\n# Heading")
                self.assertIn('<h1 id="toc_1">Heading</h1>', html)
                self.assertEqual(state.env["toc_items"], [(1, "toc_1", "Heading")])

    def test_hook_reserves_unquoted_html_ids(self):
        for element in (
            "<div id=toc_1>intro</div>",
            "<div ID=toc_1>intro</div>",
            "<div id = toc_1>intro</div>",
            "<div id=toc_1 class=intro>intro</div>",
            "<div id=toc_1\tclass=intro>intro</div>",
            "<div id=toc_1\nclass=intro>intro</div>",
            "<div id=toc_1\fclass=intro>intro</div>",
            '<div title=">" id=toc_1>intro</div>',
            "<span id=toc_1>intro</span>",
            "<div id=toc_1 />",
            "<div id=toc_&#49;>intro</div>",
        ):
            with self.subTest(element=element):
                md = create_markdown(escape=False)
                add_toc_hook(md)
                html, state = md.parse(element + "\n\n# Heading\n")
                self.assertIn('<h1 id="toc_1_1">Heading</h1>', html)
                self.assertEqual(state.env["toc_items"], [(1, "toc_1_1", "Heading")])
                self.assertIn('href="#toc_1_1"', render_toc_ul(state.env["toc_items"]))

    def test_directive_reserves_mixed_quoted_and_unquoted_html_ids(self):
        for directive, marker in (
            (FencedDirective, "```{toc}\n```"),
            (RSTDirective, ".. toc::"),
        ):
            with self.subTest(directive=directive):
                md = create_markdown(escape=False, plugins=[directive([TableOfContents()])])
                source = '<div data-é=x id=toc_1></div>\n<div id="toc_1_1"></div>\n\n' + marker + "\n\n# Heading\n"
                html = md(source)
                self.assertIn('<h1 id="toc_1_2">Heading</h1>', html)
                self.assertIn('href="#toc_1_2"', html)

    def test_quoted_ids_and_nonmatching_unquoted_values(self):
        for element, expected in (
            ('<div id="toc_1"></div>', "toc_1_1"),
            ("<div id='toc_1'></div>", "toc_1_1"),
            ('<div id=""></div>', "toc_1"),
            ("<div id=toc_10></div>", "toc_1"),
            ("<div id=toc_1/other></div>", "toc_1"),
            ("<div id=toc_1/>", "toc_1"),
            ("<div id=toc_1\u00a0other></div>", "toc_1"),
            ("Use id=toc_1 as an example.", "toc_1"),
            ("`id=toc_1`", "toc_1"),
            ('<span title="id=toc_1">intro</span>', "toc_1"),
            ("<div data-id=toc_1></div>", "toc_1"),
            ('<div title="<span id=toc_1>">intro</div>', "toc_1"),
        ):
            with self.subTest(element=element):
                md = create_markdown(escape=False)
                add_toc_hook(md)
                html, state = md.parse(element + "\n\n# Heading\n")
                self.assertIn('<h1 id="' + expected + '">Heading</h1>', html)
                self.assertEqual(state.env["toc_items"], [(1, expected, "Heading")])

    def test_custom_heading_ids_remain_authoritative(self):
        md = create_markdown(escape=False)
        add_toc_hook(md, heading_id=lambda token, index: "toc_1")
        html, state = md.parse("<div id=toc_1></div>\n\n# Heading\n")
        self.assertIn('<h1 id="toc_1">Heading</h1>', html)
        self.assertEqual(state.env["toc_items"], [(1, "toc_1", "Heading")])

    def test_literal_html_examples_retain_conservative_reservation(self):
        for value in ('"toc_1"', "toc_1"):
            for source in (
                "`<div id=" + value + ">`",
                "```html\n<div id=" + value + ">\n```",
                "<!-- <div id=" + value + "> -->",
            ):
                with self.subTest(source=source):
                    md = create_markdown(escape=False)
                    add_toc_hook(md)
                    html, state = md.parse(source + "\n\n# Heading\n")
                    self.assertIn('<h1 id="toc_1_1">Heading</h1>', html)
                    self.assertEqual(state.env["toc_items"], [(1, "toc_1_1", "Heading")])
