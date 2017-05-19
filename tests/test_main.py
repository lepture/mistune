import io
import os
import unittest
import sys

import mistune


tests_dir = os.path.dirname(__file__)
# Are we running in Python 2.x?
py2 = sys.version_info < (3,)


class MainTestCase(unittest.TestCase):
    def setUp(self):
        super(MainTestCase, self).setUp()
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def tearDown(self):
        super(MainTestCase, self).tearDown()
        sys.stdin = self._stdin
        sys.stdout = self._stdout
        sys.stderr = self._stderr

    def test_display_help(self):
        # If --help is in argv, a usage is emitted and SystemExit is raised.

        argv = [mistune.__file__, '--help']
        dest = io.BytesIO() if py2 else io.StringIO()
        sys.stderr = dest

        # Py26 doesn't have assertIn nor using assertRaises as a context manager.
        self.assertRaises(SystemExit, mistune.main, argv)
        self.assertTrue('When run as a script' in dest.getvalue())

    def test_reads_stdin_writes_stdout(self):
        src = os.path.join(tests_dir, 'fixtures', 'data', 'tree.md')
        dest = io.BytesIO() if py2 else io.StringIO()

        sys.stdin = open(src)
        sys.stdout = dest

        mistune.main([mistune.__file__])

        expected = (
            '<h2>Title here</h2>\n<p>Some text.</p>\n<p>In two paragraphs. And'
            ' then a list.</p>\n<ul>\n<li>foo</li>\n<li>bar<ol>\n<li>meep</li>'
            '\n<li>stuff</li>\n</ol>\n</li>\n</ul>\n'
        )

        self.assertEqual(dest.getvalue(), expected)


