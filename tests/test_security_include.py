import os
import tempfile
from unittest import TestCase

from mistune import create_markdown
from mistune.directives import Include, RSTDirective


class TestIncludeSecurity(TestCase):
    def test_include_rejects_traversal_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = os.path.join(tmpdir, "root")
            os.mkdir(root)
            secret = os.path.join(tmpdir, "secret.txt")
            source = os.path.join(root, "source.md")
            with open(secret, "w") as f:
                f.write("topsecret")
            with open(source, "w") as f:
                f.write(".. include:: ../secret.txt\n\n.. include:: " + secret + "\n")

            md = create_markdown(plugins=[RSTDirective([Include()])])
            html = md.read(source)[0]

        self.assertIn("Could not include outside source dir", html)
        self.assertNotIn("topsecret", html)

    def test_include_text_escapes_with_html_escape_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "source.md")
            child = os.path.join(tmpdir, "child.txt")
            with open(source, "w") as f:
                f.write(".. include:: child.txt\n")
            with open(child, "w") as f:
                f.write("<script>alert(1)</script>")

            md = create_markdown(plugins=[RSTDirective([Include()])])
            html = md.read(source)[0]

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_include_html_escapes_with_html_escape_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "source.md")
            child = os.path.join(tmpdir, "child.html")
            with open(source, "w") as f:
                f.write(".. include:: child.html\n")
            with open(child, "w") as f:
                f.write("<script>alert(1)</script>")

            md = create_markdown(plugins=[RSTDirective([Include()])])
            html = md.read(source)[0]

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_include_rejects_circular_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            a = os.path.join(tmpdir, "a.md")
            b = os.path.join(tmpdir, "b.md")
            with open(a, "w") as f:
                f.write(".. include:: b.md\n")
            with open(b, "w") as f:
                f.write(".. include:: a.md\n")

            md = create_markdown(plugins=[RSTDirective([Include()])])
            html = md.read(a)[0]

        self.assertIn("Could not include circular reference", html)
