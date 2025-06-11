#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
 
AUTHOR = u'Wizmann'
SITENAME = u"Maerlyn's Rainbow"
SITEURL = 'https://wizmann.top/'

PATH = 'content' 
STATIC_PATHS = ['statistics']

FAVICON='/statistics/favicon.png'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zhs'

# Feed generation is usually not desired when developing
FEED = 'feeds/all.rss.xml'

PYGMENTS_STYLE = "solarizedlight"

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False

MENUITEMS = (
    ('Blog', '/category/blog.html'),
    ('Online Judge', 'https://vijos.org/d/wizmann/p'),
)

# Blogroll
LINKS =  (
    ('Pelican', 'http://getpelican.com/'),
)

# Social widget
SOCIAL = (
    ('github', 'https://github.com/wizmann'),
    ('rss', SITEURL + '/feeds/all.atom.xml'),
)

DEFAULT_PAGINATION = 10

THEME = 'pelican-themes/pelican-bootstrap3'
BOOTSTRAP_THEME='flatly'
DISQUS_SITENAME = u'wizmann'
DEFAULT_DATE_FORMAT = ('%Y-%m-%d')

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

PLUGIN_PATH = ["pelican-plugins"]
PLUGINS = ["sitemap", "summary", 'tag_cloud', 'i18n_subsites', "render_math"]

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.toc': {'permalink': False},
        'markdown.extensions.nl2br': {},          # GFM-like: newlines become <br>
        'markdown.extensions.sane_lists': {},     # GFM-like: list parsing
        'markdown.extensions.smarty': {},         # Typographic substitutions
    },
    'output_format': 'html5',
}

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.7,
        "indexes": 0.5,
        "pages": 0.3,
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly",
    }
}
