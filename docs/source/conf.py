# Configuration file for the Sphinx documentation builder.
import os
import sys
from pathlib import Path

top_level_dir = Path(__file__).resolve().parent.parent.parent
module_dir = os.path.join(top_level_dir, "django_custom_admin_pages")
print(f"top_level_dir: {str(top_level_dir)}")
print(f"module_dir: {str(module_dir)}")
sys.path.append(module_dir)
sys.path.append(str(top_level_dir))

print("System Path:")
for path in sys.path:
    print(path)


print("\nModules: ")
# Iterate over the keys (module names) in sys.modules
for module_name in sys.modules:
    print(module_name)


# List all files in the directory
files = os.listdir(module_dir)

import pkgutil

# Get a list of all available modules on the Python path
available_modules = list(pkgutil.iter_modules())

print("\navailable modules:")
# Print the list of module names
for module_info in available_modules:
    print(module_info.name)

print("\nFiles in module:")
# Print the list of files
for file in files:
    print(file)

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
