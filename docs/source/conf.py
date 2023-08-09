# Configuration file for the Sphinx documentation builder.
import os
import sys
from pathlib import Path

top_level_dir = Path(__file__).resolve().parent.parent
module_dir = os.path.join(top_level_dir, "django_custom_admin_pages")
sys.path.append(module_dir)

from django_custom_admin_pages.boot_django import boot_django

boot_django()


# -- Project information

project = "Django Custom Admin Pages"
copyright = ""
author = "lekjos"

release = "1.1.1"
version = "1.1.1"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
