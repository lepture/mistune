import mistune

project = "Mistune"
copyright = "2019, Hsiaoming Yang"
author = "Hsiaoming Yang"

master_doc = "index"

# The full version, including alpha/beta/rc tags
version = mistune.__version__
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "shibuya"
html_context = {
    "source_type": "github",
    "source_user": "lepture",
    "source_repo": "mistune",
}
html_theme_options = {
    "accent_color": "indigo",
    "light_logo": "_static/logo-black.svg",
    "dark_logo": "_static/logo-white.svg",
    "twitter_site": "lepture",
    "twitter_creator": "lepture",
    "twitter_url": "https://twitter.com/lepture",
    "github_url": "https://github.com/lepture/mistune",
    "nav_links": [
        {
            "title": "Projects",
            "children": [
                {
                    "title": "Shibuya",
                    "url": "https://shibuya.lepture.com/",
                    "summary": "A responsive, good looking with modern design documentation theme for Sphinx.",
                },
                {
                    "title": "Pygments Styles",
                    "url": "https://pygments-styles.org/",
                    "summary": "A curated collection of Pygments styles based on VS Code themes.",
                },
                {
                    "title": "Sphinx Iconify",
                    "url": "https://sphinx-iconify.lepture.com/",
                    "summary": "A sphinx extension to use <code>&lt;iconify-icon&gt;</code> web component.",
                },
                {
                    "title": "Mistune",
                    "url": "http://mistune.lepture.com/",
                    "summary": "A fast yet powerful Python Markdown parser with renderers and plugins.",
                },
                {
                    "title": "Wenmode",
                    "url": "http://wenmode.lepture.com/",
                    "summary": "A fast, composable Markdown parser and renderer toolkit.",
                },
            ],
        },
        {"title": "Sponsor me", "url": "https://github.com/sponsors/lepture"},
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_copy_source = False
html_show_sourcelink = False

html_favicon = "_static/light-icon.svg"
