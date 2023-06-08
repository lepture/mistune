import mistune

project = 'Mistune'
copyright = '2019, Hsiaoming Yang'
author = 'Hsiaoming Yang'

master_doc = 'index'

# The full version, including alpha/beta/rc tags
version = mistune.__version__
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'shibuya'
html_theme_options = {
    "light_logo": "_static/logo-black.svg",
    "dark_logo": "_static/logo-white.svg",

    "light_css_variables": {
        "--sy-rc-theme": "143, 118, 214",
    },
    "dark_css_variables": {
        "--sy-rc-theme": "130, 80, 223",
    },

    'twitter_site': 'lepture',
    'twitter_creator': 'lepture',
    'twitter_url': 'https://twitter.com/lepture',
    'github_url': 'https://github.com/lepture/mistune',

    'nav_links': [
        {
            'title': 'Projects',
            'children': [
                {
                    'title': 'Authlib',
                    'url': 'https://authlib.org/',
                    'summary': 'OAuth, JOSE, OpenID, etc'
                },
                {
                    'title': 'Shibuya',
                    'url': 'https://shibuya.lepture.com/',
                    'summary': 'A pretty Sphinx theme',
                }
            ]
        },
        {'title': 'Sponsor me', 'url': 'https://github.com/sponsors/lepture'}
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_copy_source = False
html_show_sourcelink = False

html_favicon = "_static/light-icon.svg"
