# Sphinx documentation configuration for ceptor-ai (ceptor-ai)
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "ceptor-ai"
copyright = "2026, Mahmoud"
author = "Mahmoud"
release = "0.2.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
