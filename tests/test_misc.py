import mistune
from unittest import TestCase


class TestMiscCases(TestCase):
    def test_none(self):
        self.assertEqual(mistune.html(None), "")

    def test_before_parse_hooks(self):
        def _add_name(md, state):
            state.env["name"] = "test"

        md = mistune.create_markdown()
        md.before_parse_hooks.append(_add_name)
        state = md.block.state_cls()
        md.parse("", state)
        self.assertEqual(state.env["name"], "test")

    def test_hard_wrap(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md("foo\nbar")
        expected = "<p>foo<br />\nbar</p>"
        self.assertEqual(result.strip(), expected)

        md = mistune.create_markdown(escape=False, hard_wrap=True, plugins=["speedup"])
        result = md("foo\nbar")
        self.assertEqual(result.strip(), expected)

    def test_speedup_plugin_is_compat_noop(self):
        base = mistune.create_markdown(escape=False)
        compat = mistune.create_markdown(escape=False, plugins=["speedup"])
        text = "foo **bar**\n\n[link](https://example.com)\n"

        self.assertEqual(compat(text), base(text))
        self.assertNotIn("paragraph", compat.block.rules)
        self.assertNotIn("text", compat.inline.rules)

    def test_block_plain_paragraph_fast_path_interrupts(self):
        cases = [
            (
                mistune.create_markdown(escape=False),
                "Title\n---\n",
                "<h2>Title</h2>",
            ),
            (
                mistune.create_markdown(escape=False),
                "foo\n- bar\n",
                "<p>foo</p>\n<ul>\n<li>bar</li>\n</ul>",
            ),
            (
                mistune.create_markdown(escape=False, plugins=["table"]),
                "A | B\n--|--\n1 | 2\n",
                "<table>\n<thead>\n<tr>\n  <th>A</th>\n  <th>B</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n  <td>1</td>\n  <td>2</td>\n</tr>\n</tbody>\n</table>",
            ),
            (
                mistune.create_markdown(escape=False, plugins=["def_list"]),
                "Term\n: def\n",
                "<dl>\n<dt>Term</dt>\n<dd>def</dd>\n</dl>",
            ),
        ]
        for md, text, html in cases:
            self.assertEqual(md(text).strip(), html)

    def test_block_quote_line_based_boundaries(self):
        cases = {
            "> foo\nbar\n": "<blockquote>\n<p>foo\nbar</p>\n</blockquote>",
            "> foo\n>\nbar\n": "<blockquote>\n<p>foo</p>\n</blockquote>\n<p>bar</p>",
            "> foo\n>\n> bar\n": "<blockquote>\n<p>foo</p>\n<p>bar</p>\n</blockquote>",
            "> foo\n---\n": "<blockquote>\n<p>foo</p>\n</blockquote>\n<hr />",
        }
        for text, html in cases.items():
            self.assertEqual(mistune.html(text).strip(), html)

    def test_list_tab_continuation_columns(self):
        result = mistune.html("-\t\tfoo\n")
        expected = "<ul>\n<li><pre><code>  foo</code></pre>\n</li>\n</ul>"
        self.assertEqual(result.strip(), expected)

    def test_escape_html(self):
        md = mistune.create_markdown(escape=True)
        result = md("<div>1</div>")
        expected = "<p>&lt;div&gt;1&lt;/div&gt;</p>"
        self.assertEqual(result.strip(), expected)

        result = md("<em>1</em>")
        expected = "<p>&lt;em&gt;1&lt;/em&gt;</p>"
        self.assertEqual(result.strip(), expected)

    def test_harmful_links(self):
        result = mistune.html("[h](javAscript:alert)")
        expected = '<p><a href="#harmful-link">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_backslash_space_in_link_destination_is_not_an_escape(self):
        # A space is not ASCII punctuation, so "\ " is a literal backslash and a
        # space that ends the bare destination: the link fails to parse and is
        # rendered as text (as CommonMark and other parsers do). Previously the
        # scanner treated "\ " as an escape and swallowed the space into the URL,
        # producing an illegal href containing %5C%20.
        result = mistune.html(r"[a](foo\ bar)")
        self.assertEqual(result.strip(), r"<p>[a](foo\ bar)</p>")

        # An escaped punctuation character is still consumed as an escape.
        result = mistune.html(r"[a](foo\*bar)")
        self.assertEqual(result.strip(), '<p><a href="foo*bar">a</a></p>')

    def test_harmful_links_variants(self):
        # entity-decoded, alternate-scheme, and reference-link forms are all
        # routed to the #harmful-link sentinel.
        for text in [
            "[h](javascript:alert)",
            "[h](&#x6a;avascript:alert)",
            "[h](javascript&colon;alert)",
            "[h](vbscript:msgbox)",
            "[h](file:///etc/passwd)",
            "[h](data:text/html,xss)",
            "[h](data:image/svg+xml,xss)",
            "[h][r]\n\n[r]: javascript:alert",
        ]:
            result = mistune.html(text)
            self.assertIn('href="#harmful-link"', result, text)
            self.assertNotIn("javascript:alert", result, text)

    def test_control_char_scheme_not_executable(self):
        # A control char or encoded colon inside the scheme is percent-encoded
        # by escape_url, so the rendered href is never an executable
        # javascript: scheme (regardless of the sentinel path).
        for text in [
            "[h](<java\tscript:alert>)",
            "[h](<java&#x09;script:alert>)",
            "[h](javascript%3Aalert)",
        ]:
            self.assertNotIn("javascript:alert", mistune.html(text), text)

    def test_ref_link(self):
        result = mistune.html("[link][h]\n\n[h]: /foo")
        expected = '<p><a href="/foo">link</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_link_bracket_cache_cases(self):
        cases = {
            "[[a]](/url)": '<p><a href="/url">[a]</a></p>',
            "[a [b] c](/url)": '<p><a href="/url">a [b] c</a></p>',
            r"[a\]b](/url)": '<p><a href="/url">a]b</a></p>',
            "[a [b [c": "<p>[a [b [c</p>",
        }
        for text, html in cases.items():
            self.assertEqual(mistune.html(text).strip(), html)

    def test_allow_harmful_protocols(self):
        renderer = mistune.HTMLRenderer(allow_harmful_protocols=True)
        md = mistune.Markdown(renderer)
        result = md("[h](javascript:alert)")
        expected = '<p><a href="javascript:alert">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_allow_data_protocols(self):
        renderer = mistune.HTMLRenderer(allow_harmful_protocols=["data:"])
        md = mistune.Markdown(renderer)
        result = md("[h](data:alert)")
        expected = '<p><a href="data:alert">h</a></p>'
        self.assertEqual(result.strip(), expected)

    def test_use_plugin(self):
        from mistune.plugins.url import url

        md = mistune.Markdown(mistune.HTMLRenderer())
        md.use(url)

    def test_inline_plugin_refreshes_fast_trigger_cache(self):
        def parse_at(inline, m, state):
            state.append_token({"type": "at", "raw": m.group(0)})
            return m.end()

        def render_at(renderer, text):
            return "<at>" + text + "</at>"

        def plugin(md):
            md.inline.register("at", r"@+", parse_at)
            md.renderer.register("at", render_at)

        md = mistune.create_markdown(escape=False)
        md("plain text")
        md.use(plugin)

        self.assertEqual(md("@@").strip(), "<p><at>@@</at></p>")

    def test_inline_plugin_with_untracked_trigger_uses_regex_scanner(self):
        def parse_x(inline, m, state):
            state.append_token({"type": "xword", "raw": m.group(0)})
            return m.end()

        def render_x(renderer, text):
            return "<x>" + text + "</x>"

        def plugin(md):
            md.inline.register("xword", r"(?=x)x+", parse_x)
            md.renderer.register("xword", render_x)

        md = mistune.create_markdown(escape=False)
        md.use(plugin)

        self.assertEqual(md("xx").strip(), "<p><x>xx</x></p>")

    def test_markdown_func(self):
        result = mistune.markdown("**b**")
        expected = "<p><strong>b</strong></p>\n"
        self.assertEqual(result, expected)

        # trigger to use cached parser
        result = mistune.markdown("**b**")
        self.assertEqual(result, expected)

    def test_ast_output(self):
        md = mistune.create_markdown(escape=False, renderer=None)
        text = '# h1\n\nfoo **bar**\n\n`&<>"`'
        result = md(text)
        expected = [
            {
                "type": "heading",
                "children": [{"type": "text", "raw": "h1"}],
                "attrs": {"level": 1},
                "style": "atx",
            },
            {"type": "blank_line"},
            {
                "type": "paragraph",
                "children": [
                    {"type": "text", "raw": "foo "},
                    {"type": "strong", "children": [{"type": "text", "raw": "bar"}]},
                ],
            },
            {"type": "blank_line"},
            {
                "type": "paragraph",
                "children": [
                    {"type": "codespan", "raw": '&<>"'},
                ],
            },
        ]
        self.assertEqual(result, expected)

    def test_emphasis_default(self):
        result = mistune.html("*_em_* __**strong**__")
        expected = "<p><em><em>em</em></em> <strong><strong>strong</strong></strong></p>"
        self.assertEqual(result.strip(), expected)

    def test_ast_url(self):
        md = mistune.create_markdown(escape=False, renderer=None)
        label = 'hi &<>"'
        url = "https://example.com/foo?a=1&b=2"
        text = "[{}]({})".format(label, url)
        result = md(text)
        expected = [
            {
                "type": "paragraph",
                "children": [
                    {
                        "type": "link",
                        "children": [{"type": "text", "raw": label}],
                        "attrs": {"url": url},
                    },
                ],
            },
        ]
        self.assertEqual(result, expected)

    def test_emsp(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md("\u2003\u2003foo\nbar\n\n\u2003\u2003foobar")
        expected = "<p>\u2003\u2003foo<br />\nbar</p>\n<p>\u2003\u2003foobar</p>"
        self.assertEqual(result.strip(), expected)

    def test_unicode_whitespace(self):
        text = "# \u3000\u3000abc"
        result = mistune.html(text)
        expected = "<h1>\u3000\u3000abc</h1>\n"
        self.assertEqual(result, expected)

    def test_image_alt_no_double_encoding(self):
        result = mistune.html("![dogs & cats](dogs.png)")
        expected = '<p><img src="dogs.png" alt="dogs &amp; cats" /></p>'
        self.assertEqual(result.strip(), expected)

        result = mistune.html("![dogs > cats](dogs.png)")
        expected = '<p><img src="dogs.png" alt="dogs &gt; cats" /></p>'
        self.assertEqual(result.strip(), expected)

        result = mistune.html('!["quoted"](dogs.png)')
        expected = '<p><img src="dogs.png" alt="&quot;quoted&quot;" /></p>'
        self.assertEqual(result.strip(), expected)

    def test_html_tag_text_following_list(self):
        md = mistune.create_markdown(escape=False, hard_wrap=True)
        result = md("foo\n- bar\n\ntable")
        expected = "<p>foo</p>\n<ul>\n<li>bar</li>\n</ul>\n<p>table</p>"
        self.assertEqual(result.strip(), expected)

    def test_max_nested_level_setting(self):
        self.assertEqual(mistune.BlockParser().max_nested_level, 20)
        self.assertEqual(mistune.create_markdown().block.max_nested_level, 20)
        md = mistune.Markdown(block=mistune.BlockParser(max_nested_level=7))
        self.assertEqual(md.block.max_nested_level, 7)

    def test_max_emphasis_depth_setting(self):
        self.assertEqual(mistune.InlineParser().max_emphasis_depth, 20)
        self.assertEqual(mistune.create_markdown().inline.max_emphasis_depth, 20)
        md = mistune.Markdown(inline=mistune.InlineParser(max_emphasis_depth=7))
        self.assertEqual(md.inline.max_emphasis_depth, 7)

    def test_max_image_depth_setting(self):
        self.assertEqual(mistune.InlineParser().max_image_depth, 20)
        self.assertEqual(mistune.create_markdown().inline.max_image_depth, 20)
        md = mistune.Markdown(inline=mistune.InlineParser(max_image_depth=7))
        self.assertEqual(md.inline.max_image_depth, 7)

    def test_deeply_nested_block_quote_and_list(self):
        # Block quotes and lists each capped their own nesting at the limit but
        # not each other's, so alternating them recursed without bound. This
        # must terminate instead of raising RecursionError.
        max_level = mistune.create_markdown().block.max_nested_level
        text = "".join(">" * i + " " + "- " * i + "item\n" for i in range(1, max_level + 80))
        md = mistune.create_markdown()
        md(text)
        ast = mistune.create_markdown(renderer="ast")
        ast(text)

    def test_table_plugin_redos_candidates(self):
        md = mistune.create_markdown(escape=False, plugins=["table"])
        md("|x" + " " * 16000 + "|\n|---|\n")
        md("|x|\n" + "|" * 32000 + "\n")

    def test_def_list_plugin_redos_candidate(self):
        md = mistune.create_markdown(escape=False, plugins=["def_list"])
        result = md("x\n" * 8000)
        self.assertTrue(result.startswith("<p>x\nx\n"))

    def test_cli_output_file_uses_utf8(self):
        from argparse import Namespace
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from mistune.__main__ import _output

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "out.html"
            _output("★", Namespace(output=str(path)))
            self.assertEqual(path.read_text(encoding="utf-8"), "★")

    def test_project_script_entrypoint(self):
        from pathlib import Path

        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('mistune = "mistune.__main__:cli"', pyproject)
