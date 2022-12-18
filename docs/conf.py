# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

import semantic_release  # noqa

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinxcontrib.apidoc",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "python-semantic-release"
copyright = "2020, Rolf Erik Lekang"

version = semantic_release.__version__
release = semantic_release.__version__

# language = None
# today = ''
# today_fmt = '%B %d, %Y'

exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "alabaster"
# html_static_path = ["_static"]
htmlhelp_basename = "python-semantic-releasedoc"


# -- Automatically run sphinx-apidoc --------------------------------------

docs_path = os.path.dirname(__file__)
apidoc_output_dir = os.path.join(docs_path, "api")
apidoc_module_dir = os.path.join(docs_path, "..", "semantic_release")
apidoc_separate_modules = True
apidoc_module_first = True
apidoc_extra_args = ["-d", "3"]


def setup(app):
    pass


# -- Options for LaTeX output ---------------------------------------------
latex_documents = [
    (
        "index",
        "python-semantic-release.tex",
        "python-semantic-release Documentation",
        "Rolf Erik Lekang",
        "manual",
    ),
]


# -- Options for manual page output ---------------------------------------
man_pages = [
    (
        "index",
        "python-semantic-release",
        "python-semantic-release Documentation",
        ["Rolf Erik Lekang"],
        1,
    )
]


# -- Options for Texinfo output -------------------------------------------
texinfo_documents = [
    (
        "index",
        "python-semantic-release",
        "python-semantic-release Documentation",
        "Rolf Erik Lekang",
        "python-semantic-release",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = "python-semantic-release"
epub_author = "Rolf Erik Lekang"
epub_publisher = "Rolf Erik Lekang"
epub_copyright = "2020, Rolf Erik Lekang"
epub_exclude_files = ["search.html"]
