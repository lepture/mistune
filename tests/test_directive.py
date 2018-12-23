import os
from mistune import Markdown, HTMLRenderer
from mistune.plugins.directive import Directive
from tests.fixtures import ROOT
from unittest import TestCase


md = Markdown(renderer=HTMLRenderer(escape=False))
md.use(Directive())


class TestPluginDirective(TestCase):
    def test_include(self):
        html = md.read(os.path.join(ROOT, 'include/text.md'))
        self.assertIn('Could not include self', html)
        self.assertIn('Could not find file', html)
        self.assertIn('<div>include html</div>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('# Table of Contents', html)
